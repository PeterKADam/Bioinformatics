import inspect
import os
import sys
import os.path
import unittest
from unittest import TestResult, TextTestRunner
from contextlib import redirect_stdout
from io import StringIO
import traceback
import re

GRADE_MODE = os.getenv('GRADE_MODE')

PROJECT_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('test_', '')

class NullDevice:

    def write(self, s):
        pass

# Redirect all stdout from the imported module to a null device to not confuse
# the student too much...
try:
    with redirect_stdout(NullDevice()):
        # import progexam as project
       project = __import__(PROJECT_NAME)
except:
    print("YOUR CODE CANNOT BE RUN:\n\nHere is the error:\n")
    traceback.print_exc(file=sys.stdout)
    print("\nFIX THAT FIRST BEFORE YOU USE THE TEST SCRIPT")
    sys.exit(99)


assertion_msg = """The call:

    {func}({args})

returned:

    {actual}

However, it should return:

    {expected}
"""


def suiteFactory(*testcases):

    ln    = lambda f: getattr(tc, f).__code__.co_firstlineno
    lncmp = lambda a, b: ln(a) - ln(b)

    test_suite = unittest.TestSuite()
    for tc in testcases:
        test_suite.addTest(unittest.makeSuite(tc, sortUsing=lncmp))

    return test_suite


def caseFactory():
    from inspect import findsource
    
    g = globals().copy()
    cases = [g[obj] for obj in g if obj.startswith("Test") and issubclass(g[obj], unittest.TestCase)]
    ordered_cases = sorted(cases, key=lambda f: findsource(f)[1])
    return ordered_cases


def function_not_defined(module, func_name):
    return not (hasattr(module, func_name) and callable(getattr(module, func_name)))


def indent(text, indent=4):
    return '\n'.join([(indent * ' ') + line for line in text.splitlines()])


def skip_initial_nonlocal(tb):
    if tb is None:
        return tb
    if tb.tb_frame.f_code.co_filename.startswith('test_'):
        return skip_initial_nonlocal(tb.tb_next)
    if 'unittest' in tb.tb_frame.f_code.co_filename:
        return skip_initial_nonlocal(tb.tb_next)

    return tb

######################################################

from copy import deepcopy

class NonStandardElementError(Exception):

    def __init___(self, dErrArguments):
        def __init__(self,*args,**kwargs):
            Exception.__init__(self,*args,**kwargs)
  

def round_datastruct_recursively(d):
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list) or isinstance(v, dict):
                round_datastruct_recursively(v)
            elif isinstance(v, float):
                d[k] = round(d[k], 5)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            if isinstance(v, list) or isinstance(v, dict):
                round_datastruct_recursively(v)
            elif isinstance(v, float):
                d[i] = round(d[i], 5)
    elif not (isinstance(d, float) or isinstance(d, int) or isinstance(d, str)):
        raise NonStandardElementError(d)

def compare_datastruct_nice(exp, act):
    """
    Compares data structures in a way that rounds float values in them
    """
    exp_rounded = deepcopy(exp)
    act_rounded = deepcopy(act)
    try:
        round_datastruct_recursively(exp_rounded)
        round_datastruct_recursively(act_rounded)
    except NonStandardElementError as err:
        return False
    return exp_rounded == act_rounded

######################################################

class AnvProgTestResult(TestResult):
    separator = '=' * 70

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = False
        self.dots = True
        self.descriptions = descriptions

        self.skipped_functions = list()

        if GRADE_MODE:
            report_file = os.path.splitext(os.path.basename(__file__))[0] + '.csv'
            self.file = open(report_file, 'w')

        # match = re.search(r'assignment_(au\d+)_attempt', os.path.basename(os.getcwd()))
        # if match:
        #     self.student_id = match.group(1)
        # else:
        #     self.student_id = 'NA'

        blackboard_match = re.search(r'assignment_(au\d+)_attempt', os.path.basename(os.getcwd()))
        digitalexam_match = re.search(r'([^_]+)_\d+_\d+_.+' + PROJECT_NAME, os.path.basename(os.getcwd()))

        if blackboard_match:
            self.student_id = blackboard_match.group(1)
        elif digitalexam_match:
            self.student_id = digitalexam_match.group(1)            
        else:
            self.student_id = 'NA'

    def addSuccess(self, test):
        super().addSuccess(test)

        if GRADE_MODE:
            self.file.write('{},{},{},{}\n'.format(self.student_id, test.__class__.__name__, test._testMethodName, 'ok'))
            self.file.flush()

    def addError(self, test, err):
        super().addError(test, err)
        errcls, errobj, tb = err
        new_tb = skip_initial_nonlocal(tb)

        if GRADE_MODE:
            self.file.write('{},{},{},{}\n'.format(self.student_id, test.__class__.__name__, test._testMethodName, 'error'))
            self.file.flush()

        # self.stream.writeln(
        #     'ERROR DURING TEST CASE: {}'.format(test._testMethodName))
        self.stream.writeln(
            'YOUR CODE FAILED WHILE RUNNING A TEST ({})'.format(test._testMethodName))
        self.stream.writeln()
        self.stream.writeln('It means that your function could not be run the way specified in the assignment.')
        self.stream.writeln()
        self.stream.writeln('MESSAGE:')
        self.stream.writeln(indent('{}'.format(errobj)))
        self.stream.writeln()
        self.stream.writeln('DETAILED:')
        self.stream.writeln(
            indent('Below is a detailed description of where the error occurred'))
        self.stream.writeln(indent(
            'and what code was run before the error occurred. It is often'))
        self.stream.writeln(indent(
            'most useful to read this description from the bottom and up.'))
        self.stream.writeln()

        # self.stream.writeln(
        #     indent('\n'.join(traceback.format_tb(new_tb))))
        self.stream.writeln(
            indent("...Skipped frames not relevant to your code..."))
        self.stream.writeln()
        self.stream.writeln(
            indent(''.join(traceback.format_exception(errcls, errobj, new_tb))))

        self.stream.writeln()
        self.stream.writeln(self.separator)
        self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        _, errobj, tb = err

        if GRADE_MODE:
            self.file.write('{},{},{},{}\n'.format(self.student_id, test.__class__.__name__, test._testMethodName, 'failed'))
            self.file.flush()

        self.stream.writeln(
            'FAILED TEST CASE: {}'.format(test._testMethodName))
        self.stream.writeln()
        self.stream.writeln('MESSAGE:')
        self.stream.writeln(indent(str(errobj)))
        self.stream.writeln()

        if isinstance(errobj, AssertEqualAssertionError):
            self.stream.writeln('EXPECTED:')
            self.stream.writeln(indent(repr(errobj.expected)))
            self.stream.writeln()
            self.stream.writeln('ACTUAL:')
            self.stream.writeln(indent(repr(errobj.actual)))
            self.stream.writeln()

        # if isinstance(errobj, AssertionError):
        #     new_tb = skip_initial_nonlocal(tb)
        #     self.stream.writeln(
        #         'ERROR DURING TEST CASE: {}'.format(test._testMethodName))
        #     self.stream.writeln()
        #     self.stream.writeln('MESSAGE:')
        #     self.stream.writeln(indent('Your function contains an "assert" statement that raised an error'))
        #     self.stream.writeln(indent('Remove the assert statement to resolve this error'))
        #     self.stream.writeln()
        #     self.stream.writeln('DETAILED:')
        #     self.stream.writeln(
        #         indent('Below is a detailed description of where the error occurred'))
        #     self.stream.writeln()
        #     self.stream.writeln(indent(traceback.format_tb(new_tb)[-1]))
        #     # self.stream.writeln(
        #     #     indent('\n'.join(traceback.format_tb(new_tb))))
        #     self.stream.writeln()

        self.stream.writeln(self.separator)
        self.stream.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)

        if reason not in self.skipped_functions:
            self.skipped_functions.append(reason)

        if GRADE_MODE:
            self.file.write('{},{},{},{}\n'.format(self.student_id, test.__class__.__name__, test._testMethodName, 'skipped'))
            self.file.flush()

        # self.stream.writeln(
        #     'ATTENTION! A test of "{}" was skipped because this function was not defined. '.format(reason))
        # self.stream.writeln(
        #     'Functions not correctly defined are marked as FAILED. Please make sure this is what you intended!')
        # self.stream.writeln('')
        # self.stream.flush()

    def addExpectedFailure(self, test, err):
        raise NotImplementedError()

    def addUnexpectedSuccess(self, test):
        raise NotImplementedError()

    def stopTestRun(self):
        super().stopTestRun()

        if self.skipped_functions:
            self.stream.writeln()
            self.stream.writeln('*'*57)
            self.stream.writeln(
                'ATTENTION! The following functions are not defined:')
            self.stream.writeln('')
            self.stream.writeln(
                '\n'.join('\t{}'.format(x) for x in self.skipped_functions))
            self.stream.writeln()
            self.stream.writeln(
                'These functions are either not correctly named (spelled)')
            self.stream.writeln(
                'or not defined at all. They will be marked as FAILED.')
            self.stream.writeln(
                'Check your spelling if this is not what you intend.')
            self.stream.writeln('*'*57)
            self.stream.writeln()
            self.stream.flush()


class AnvProgTestRunner(TextTestRunner):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, resultclass=AnvProgTestResult, **kwargs)


class AssertEqualAssertionError(AssertionError):
    """
    A simple extension of AssertionError allowing us to store the actual and
    expected values for later use.
    """

    def __init__(self, actual, expected, msg):
        super(AssertEqualAssertionError, self).__init__(msg)
        self.actual = actual
        self.expected = expected


class AssertEqualNiceAssertionError(AssertionError):

    def __init__(self, actual, expected, func, args, kwargs):
        self.actual = actual
        self.expected = expected
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        args_str = ', '.join(map(repr, self.args))
        if self.kwargs:
            kwargs_str = ', '.join('{}={!r}'.format(k, w)
                                   for k, w in self.kwargs.items())
            args_str += ', ' + kwargs_str
        return assertion_msg.format(
            func=self.func.__name__,
            args=args_str,
            actual=repr(self.actual),
            expected=repr(self.expected))


class AnvProgTestCase(unittest.TestCase):

    def assertFunctionDefined(self, module, name):
        self.assertTrue(hasattr(module, name),
                        msg="'{}' is not defined".format(name))
        self.assertTrue(callable(getattr(module, name)),
                        msg="'{}' is not a function".format(name))

    def assertFunctionPosParams(self, func, expected):
        signature = str(inspect.signature(func))
        self.assertTrue(expected == signature,
                        msg="Wrong names of function parameters\n\n"
                            "Correct function definition:\n\n"
                            "{}\n\n"
                            "Got:\n\n"
                            "{}".format(func.__name__ + expected, func.__name__ + signature))

    def assertEqualNice(self, expected, func, *args, **kwargs):
        actual = func(*args, **kwargs)

        if isinstance(expected, dict) or isinstance(actual, dict) or \
            isinstance(expected, list) or isinstance(actual, list):
            if not compare_datastruct_nice(expected, actual):
                raise AssertEqualNiceAssertionError(
                    actual, expected, func, args, kwargs)

        elif isinstance(expected, float) or isinstance(actual, float):
            if abs(expected - actual) > 1e-4:
                raise AssertEqualNiceAssertionError(
                    actual, expected, func, args, kwargs)
        elif actual != expected:
            raise AssertEqualNiceAssertionError(
                actual, expected, func, args, kwargs)

    def assertEqual(self, first, second, msg=None):
        # Suppress diffs for strings.
        if msg is None and isinstance(first, str) and isinstance(second, str):
            msg = 'Got \'{}\' but expected \'{}\''.format(first, second)

        try:
            super().assertEqual(first, second, msg=msg)
        except AssertionError as err:
            if msg is None:
                msg = err.args[0]

            raise AssertEqualAssertionError(first, second, msg)

    def assertTrue(self, expr, msg=None):
        # Override super().assertTrue() to suppress the default 'X is not true'
        # output when msg is not None.
        if msg is None:
            msg = '{} is not true'.format(expr)
        if not expr:
            raise AssertionError(msg)

    def assertFalse(self, expr, msg=None):
        # Override super().assertFalse() to suppress the default 'X is not
        # false' output when msg is not None.
        if msg is None:
            msg = '{} is not false'.format(expr)
        if expr:
            raise AssertionError(msg)

###############################################################################
#                                                                             #
#                                 TESTS HERE                                  #
#                                                                             #
###############################################################################

codon_map = {'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L', 'TCT': 'S',
             'TCC': 'S', 'TCA': 'S', 'TCG': 'S', 'TAT': 'Y', 'TAC': 'Y',
             'TAA': '*', 'TAG': '*', 'TGT': 'C', 'TGC': 'C', 'TGA': '*',
             'TGG': 'W', 'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
             'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P', 'CAT': 'H',
             'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q', 'CGT': 'R', 'CGC': 'R',
             'CGA': 'R', 'CGG': 'R', 'ATT': 'I', 'ATC': 'I', 'ATA': 'I',
             'ATG': 'M', 'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
             'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K', 'AGT': 'S',
             'AGC': 'S', 'AGA': 'R', 'AGG': 'R', 'GTT': 'V', 'GTC': 'V',
             'GTA': 'V', 'GTG': 'V', 'GCT': 'A', 'GCC': 'A', 'GCA': 'A',
             'GCG': 'A', 'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
             'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'}

start_codon = 'ATG'

stop_codons = ['TAG', 'TGA', 'TAA']

@unittest.skipIf(function_not_defined(project, 'find_start_positions'), 'find_start_positions')
class TestFindStartPositions(AnvProgTestCase):

    def test_find_start_positions_1(self):
        self.assertTrue(isinstance(
            project.find_start_positions('AATGA'), list))

    def test_find_start_positions_2(self):
        self.assertTrue(isinstance(project.find_start_positions(''), list))

    def test_find_start_positions_3(self):
        self.assertEqualNice(
            [1, 5, 9], project.find_start_positions, 'AATGAATGTATG')

    def test_find_start_positions_4(self):
        self.assertEqualNice(
            [0, 3, 6], project.find_start_positions, 'ATGATGATG')


@unittest.skipIf(function_not_defined(project, 'find_next_codon'), 'find_next_codon')
class TestFindNextCodon(AnvProgTestCase):

    def test_find_next_codon_1(self):
        self.assertEqualNice(6, project.find_next_codon,
                             'AATTTATTT', 0, 'TTT')

    def test_find_next_codon_2(self):
        self.assertEqualNice(2, project.find_next_codon,
                             'AATTTATTT', 2, 'TTT')

    def test_find_next_codon_3(self):
        self.assertEqualNice(
            None, project.find_next_codon, 'AATTTATTT', 1, 'TTT')


@unittest.skipIf(function_not_defined(project, 'find_next_stop_codon'), 'find_next_stop_codon')
class TestFindNextStopCodon(AnvProgTestCase):

    def test_find_next_stop_codon_1(self):
        self.assertEqualNice(3, project.find_next_stop_codon, 'AAATGAATG', 0)

    def test_find_next_stop_codon_2(self):
        self.assertEqualNice(0, project.find_next_stop_codon, 'TAGTGAATG', 0)

    def test_find_next_stop_codon_3(self):
        self.assertEqualNice(5, project.find_next_stop_codon, 'ATGAATAG', 2)

    def test_find_next_stop_codon_4(self):
        self.assertEqualNice(
            None, project.find_next_stop_codon, 'ATGAAATAG', 2)


@unittest.skipIf(function_not_defined(project, 'find_orfs'), 'find_orfs')
class TestFindOrfs(AnvProgTestCase):

    def test_find_orfs_1(self):
        self.assertEqualNice([[0, 6], [11, 17]],
                             project.find_orfs, 'ATGAAATAGAAATGAAATAGTAA')

    def test_find_orfs_2(self):
        self.assertEqualNice([[0, 15], [4, 10]],
                             project.find_orfs, 'ATGAATGAAATAGAATGAAA')

    def test_find_orfs_3(self):
        self.assertEqualNice([], project.find_orfs, 'AAATGAAAAAAAAAA')


class TestCodonMap(AnvProgTestCase):

    def test_codon_map_defined_1(self):
        self.assertTrue(hasattr(project, 'codon_map'),
                       'The variable `codon_map` has not been defined.')

    def test_codon_map_defined_2(self):
        self.assertEqual(project.codon_map, codon_map,
                       'It seems you have changed to `codon_map` in your file.')


@unittest.skipIf(function_not_defined(project, 'translate_codon'), 'translate_codon')
class TestTranslateCodon(AnvProgTestCase):

    def test_translate_codon_1(self):
        self.assertEqualNice('M', project.translate_codon, 'ATG')

    def test_translate_codon_2(self):
        self.assertEqualNice('*', project.translate_codon, 'TAA')

    def test_translate_codon_3(self):
        self.assertEqualNice('?', project.translate_codon, 'NNN')

    def test_translate_codon_4(self):
        self.assertEqualNice('T', project.translate_codon, 'ACG')

    def test_translate_codon_5(self):
        self.assertEqualNice('?', project.translate_codon, 'NNN')

    def test_translate_codon_6(self):
        self.assertEqualNice('*', project.translate_codon, 'TAA')


@unittest.skipIf(function_not_defined(project, 'split_codons'), 'split_codons')
class TestSplitCodons(AnvProgTestCase):

    def test_split_codons_1(self):
        self.assertEqualNice(['AAA', 'TTT', 'CCC', 'GGG'], project.split_codons, 'AAATTTCCCGGG')

    def test_split_codons_2(self):
        self.assertEqualNice(['NNN', 'NNN', 'NNN', 'NNN'], project.split_codons, 'NNNNNNNNNNNN')

    def test_split_codons_3(self):
        self.assertEqualNice(['ATG'], project.split_codons, 'ATG')

    def test_split_codons_4(self):
        self.assertEqualNice([], project.split_codons, '')


@unittest.skipIf(function_not_defined(project, 'translate_orf'), 'translate_orf')
class TestTranslateOrf(AnvProgTestCase):

    def test_translate_orf_1(self):
        self.assertEqualNice('MPM*', project.translate_orf, 'ATGCCCATGTGA')

    def test_translate_orf_2(self):
        self.assertEqualNice('M?M*', project.translate_orf, 'ATGATNATGTGA')

    def test_translate_orf_3(self):
        self.assertEqualNice('M*', project.translate_orf, 'ATGTGA')

    def test_translate_orf_4(self):
        self.assertEqualNice('', project.translate_orf, '')


@unittest.skipIf(function_not_defined(project, 'read_genome'), 'read_genome')
class TestReadGenome(AnvProgTestCase):

    def test_read_genome_1(self):
        self.assertTrue(project.read_genome(
            'e_coli_O157_H157_str_Sakai.fasta').endswith('CGCCTTAGTAAGTATTTTTC'))


@unittest.skipIf(function_not_defined(project, 'find_candidate_proteins'), 'find_candidate_proteins')
class TestFindCandidateProteins(AnvProgTestCase):


    def test_find_candidate_proteins_1(self):
        self.assertEqualNice(
            ['MM*', 'M*', 'MM*', 'M*'], project.find_candidate_proteins, "AAAATGATGTAGAAAATGATGTAGAAA")

    def test_find_candidate_proteins_2(self):
        genome = project.read_genome('e_coli_O157_H157_str_Sakai.fasta')
        predicted_first_1k = ['MSLCGLKKESLTAASELVTCRE*', 'MKRISTTITTTITTTITITITTGNGAG*',
                              'MQNVFCGLPIFWKAMPGRGRWPPSSLPPPKSPTTWWR*', 'MPGRGRWPPSSLPPPKSPTTWWR*',
                              'MLYPISAMPNVFLPNF*', 'MPNVFLPNF*', 'MSCMALVC*', 'MALVC*']
        self.assertEqualNice(predicted_first_1k,
                             project.find_candidate_proteins, genome[:1000])


if __name__ == '__main__':
    # if GRADE_MODE:
    #    unittest.main(failfast=False, testRunner=AnvProgTestRunner)
    # else:
    #    unittest.main(failfast=True, testRunner=AnvProgTestRunner)
    cases = suiteFactory(*caseFactory())
    if GRADE_MODE:
       failfast=False
    else:
       failfast=True
    runner = AnvProgTestRunner(failfast=failfast)
    test_result = runner.run(cases)
    sys.exit(int(not test_result.wasSuccessful()))
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

class TestCodonMap(AnvProgTestCase):

    def test_codon_map_defined_1(self):
        self.assertTrue(hasattr(project, 'codon_map'),
                       'The variable `codon_map` has not been defined.')

    def test_codon_map_defined_2(self):
        self.assertEqual(project.codon_map, codon_map,
                       'It seems you have changed to `codon_map` in your file.')


@unittest.skipIf(function_not_defined(project, 'split_codons'), 'split_codons')
class TestSplitCodons(AnvProgTestCase):

    # def test_aaa_split_codons_exists(self):
    #     self.assertFunctionDefined(project, 'split_codons')

    def test_split_codons_1(self):
        self.assertEqualNice(['AAA', 'TTT', 'CCC', 'GGG'], project.split_codons, 'AAATTTCCCGGG')

    def test_split_codons_2(self):
        self.assertEqualNice(['NNN', 'NNN', 'NNN', 'NNN'], project.split_codons, 'NNNNNNNNNNNN')

    def test_split_codons_3(self):
        self.assertEqualNice(['ATG'], project.split_codons, 'ATG')

    def test_split_codons_4(self):
        self.assertEqualNice([], project.split_codons, '')


@unittest.skipIf(function_not_defined(project, 'count_codons'), 'count_codons')
class TestCountCodons(AnvProgTestCase):

    def test_count_codons_1(self):
        self.assertEqualNice({'CTT': 0, 'ATG': 1, 'ACA': 0, 'ACG': 0, 'ATC': 0, 'AAC': 0,
                              'ATA': 0, 'AGG': 0, 'CCT': 0, 'ACT': 0, 'AGC': 0, 'AAG': 0,
                              'AGA': 0, 'CAT': 0, 'AAT': 0, 'ATT': 0, 'CTG': 0, 'CTA': 0,
                              'CTC': 0, 'CAC': 0, 'AAA': 0, 'CCG': 0, 'AGT': 0, 'CCA': 0,
                              'CAA': 0, 'CCC': 0, 'TAT': 0, 'GGT': 0, 'TGT': 0, 'CGA': 0,
                              'CAG': 0, 'TCT': 0, 'GAT': 0, 'CGG': 0, 'TTT': 0, 'TGC': 0,
                              'GGG': 0, 'TAG': 0, 'GGA': 0, 'TGG': 0, 'GGC': 0, 'TAC': 0,
                              'TTC': 0, 'TCG': 0, 'TTA': 0, 'TTG': 0, 'TCC': 0, 'ACC': 0,
                              'TAA': 0, 'GCA': 0, 'GTA': 0, 'GCC': 0, 'GTC': 0, 'GCG': 0,
                              'GTG': 0, 'GAG': 0, 'GTT': 0, 'GCT': 0, 'TGA': 1, 'GAC': 0,
                              'CGT': 0, 'GAA': 0, 'TCA': 0, 'CGC': 0}, 
                              project.count_codons, 
                              'ATGTGA')


    def test_count_codons_2(self):
        self.assertEqualNice({'CTT': 0, 'ATG': 1, 'ACA': 0, 'ACG': 0, 'ATC': 0, 'AAC': 0,
                              'ATA': 0, 'AGG': 0, 'CCT': 0, 'ACT': 0, 'AGC': 0, 'AAG': 0,
                              'AGA': 0, 'CAT': 0, 'AAT': 0, 'ATT': 0, 'CTG': 0, 'CTA': 0,
                              'CTC': 0, 'CAC': 0, 'AAA': 0, 'CCG': 0, 'AGT': 0, 'CCA': 0,
                              'CAA': 0, 'CCC': 0, 'TAT': 0, 'GGT': 0, 'TGT': 0, 'CGA': 0,
                              'CAG': 0, 'TCT': 0, 'GAT': 0, 'CGG': 0, 'TTT': 0, 'TGC': 0,
                              'GGG': 0, 'TAG': 0, 'GGA': 0, 'TGG': 0, 'GGC': 0, 'TAC': 0,
                              'TTC': 0, 'TCG': 0, 'TTA': 0, 'TTG': 0, 'TCC': 4, 'ACC': 0,
                              'TAA': 0, 'GCA': 0, 'GTA': 0, 'GCC': 0, 'GTC': 0, 'GCG': 0,
                              'GTG': 0, 'GAG': 0, 'GTT': 0, 'GCT': 0, 'TGA': 1, 'GAC': 0,
                              'CGT': 0, 'GAA': 0, 'TCA': 0, 'CGC': 0}, 
                              project.count_codons, 
                              'ATGTCCTCCTCCTCCTGA')




@unittest.skipIf(function_not_defined(project, 'group_counts_by_amino_acid'), 'group_counts_by_amino_acid')
class TestGroupCountsByAminoAcid(AnvProgTestCase):

    def test_group_counts_by_amino_acid_1(self):
        self.assertEqualNice({'A': {'GCA': 0, 'GCC': 0, 'GCT': 0, 'GCG': 0}, 
                              'C': {'TGC': 0, 'TGT': 0}, 
                              'E': {'GAG': 0, 'GAA': 0}, 
                              'D': {'GAT': 0, 'GAC': 0}, 
                              'G': {'GGT': 0, 'GGG': 0, 'GGA': 0, 'GGC': 0}, 
                              'F': {'TTC': 0, 'TTT': 0}, 
                              'I': {'ATT': 0, 'ATC': 0, 'ATA': 0}, 
                              'H': {'CAC': 0, 'CAT': 0}, 
                              'K': {'AAG': 0, 'AAA': 0}, 
                              '*': {'TAG': 0, 'TGA': 1, 'TAA': 0}, 
                              'M': {'ATG': 1}, 
                              'L': {'CTT': 0, 'CTG': 0, 'CTA': 0, 'CTC': 0, 'TTA': 0, 'TTG': 0}, 
                              'N': {'AAT': 0, 'AAC': 0}, 
                              'Q': {'CAA': 0, 'CAG': 0},
                              'P': {'CCT': 0, 'CCG': 0, 'CCA': 0, 'CCC': 0}, 
                              'S': {'TCT': 0, 'AGC': 0, 'TCG': 0, 'AGT': 0, 'TCC': 0, 'TCA': 0}, 
                              'R': {'AGG': 0, 'CGC': 0, 'CGG': 0, 'CGA': 0, 'AGA': 0, 'CGT': 0}, 
                              'T': {'ACC': 0, 'ACA': 0, 'ACG': 0, 'ACT': 0}, 
                              'W': {'TGG': 0}, 
                              'V': {'GTA': 0, 'GTC': 0, 'GTT': 0, 'GTG': 0}, 
                              'Y': {'TAT': 0, 'TAC': 0}}, 
                              project.group_counts_by_amino_acid, 
                              {'CTT': 0, 'ATG': 1, 'ACA': 0, 'ACG': 0, 'ATC': 0, 'AAC': 0,
                              'ATA': 0, 'AGG': 0, 'CCT': 0, 'ACT': 0, 'AGC': 0, 'AAG': 0,
                              'AGA': 0, 'CAT': 0, 'AAT': 0, 'ATT': 0, 'CTG': 0, 'CTA': 0,
                              'CTC': 0, 'CAC': 0, 'AAA': 0, 'CCG': 0, 'AGT': 0, 'CCA': 0,
                              'CAA': 0, 'CCC': 0, 'TAT': 0, 'GGT': 0, 'TGT': 0, 'CGA': 0,
                              'CAG': 0, 'TCT': 0, 'GAT': 0, 'CGG': 0, 'TTT': 0, 'TGC': 0,
                              'GGG': 0, 'TAG': 0, 'GGA': 0, 'TGG': 0, 'GGC': 0, 'TAC': 0,
                              'TTC': 0, 'TCG': 0, 'TTA': 0, 'TTG': 0, 'TCC': 0, 'ACC': 0,
                              'TAA': 0, 'GCA': 0, 'GTA': 0, 'GCC': 0, 'GTC': 0, 'GCG': 0,
                              'GTG': 0, 'GAG': 0, 'GTT': 0, 'GCT': 0, 'TGA': 1, 'GAC': 0,
                              'CGT': 0, 'GAA': 0, 'TCA': 0, 'CGC': 0})


    def test_group_counts_by_amino_acid_2(self):
        self.assertEqualNice({'A': {'GCA': 0, 'GCC': 0, 'GCT': 0, 'GCG': 0}, 
                              'C': {'TGC': 0, 'TGT': 0}, 
                              'E': {'GAG': 0, 'GAA': 0}, 
                              'D': {'GAT': 0, 'GAC': 0}, 
                              'G': {'GGT': 0, 'GGG': 0, 'GGA': 0, 'GGC': 0}, 
                              'F': {'TTC': 0, 'TTT': 0}, 
                              'I': {'ATT': 0, 'ATC': 0, 'ATA': 0}, 
                              'H': {'CAC': 0, 'CAT': 0}, 
                              'K': {'AAG': 0, 'AAA': 0}, 
                              '*': {'TAG': 0, 'TGA': 1, 'TAA': 0}, 
                              'M': {'ATG': 1}, 
                              'L': {'CTT': 0, 'CTG': 0, 'CTA': 0, 'CTC': 0, 'TTA': 0, 'TTG': 0}, 
                              'N': {'AAT': 0, 'AAC': 0}, 
                              'Q': {'CAA': 0, 'CAG': 0},
                              'P': {'CCT': 0, 'CCG': 0, 'CCA': 0, 'CCC': 0}, 
                              'S': {'TCT': 0, 'AGC': 0, 'TCG': 0, 'AGT': 0, 'TCC': 4, 'TCA': 0}, 
                              'R': {'AGG': 0, 'CGC': 0, 'CGG': 0, 'CGA': 0, 'AGA': 0, 'CGT': 0}, 
                              'T': {'ACC': 0, 'ACA': 0, 'ACG': 0, 'ACT': 0}, 
                              'W': {'TGG': 0}, 
                              'V': {'GTA': 0, 'GTC': 0, 'GTT': 0, 'GTG': 0}, 
                              'Y': {'TAT': 0, 'TAC': 0}}, 
                              project.group_counts_by_amino_acid, 
                              {'CTT': 0, 'ATG': 1, 'ACA': 0, 'ACG': 0, 'ATC': 0, 'AAC': 0,
                              'ATA': 0, 'AGG': 0, 'CCT': 0, 'ACT': 0, 'AGC': 0, 'AAG': 0,
                              'AGA': 0, 'CAT': 0, 'AAT': 0, 'ATT': 0, 'CTG': 0, 'CTA': 0,
                              'CTC': 0, 'CAC': 0, 'AAA': 0, 'CCG': 0, 'AGT': 0, 'CCA': 0,
                              'CAA': 0, 'CCC': 0, 'TAT': 0, 'GGT': 0, 'TGT': 0, 'CGA': 0,
                              'CAG': 0, 'TCT': 0, 'GAT': 0, 'CGG': 0, 'TTT': 0, 'TGC': 0,
                              'GGG': 0, 'TAG': 0, 'GGA': 0, 'TGG': 0, 'GGC': 0, 'TAC': 0,
                              'TTC': 0, 'TCG': 0, 'TTA': 0, 'TTG': 0, 'TCC': 4, 'ACC': 0,
                              'TAA': 0, 'GCA': 0, 'GTA': 0, 'GCC': 0, 'GTC': 0, 'GCG': 0,
                              'GTG': 0, 'GAG': 0, 'GTT': 0, 'GCT': 0, 'TGA': 1, 'GAC': 0,
                              'CGT': 0, 'GAA': 0, 'TCA': 0, 'CGC': 0})



@unittest.skipIf(function_not_defined(project, 'normalize_counts'), 'normalize_counts')
class TestNormalizeCounts(AnvProgTestCase):

    # def test_aaa_split_codons_exists(self):
    #     self.assertFunctionDefined(project, 'split_codons')

    def test_normalize_counts_1(self):
        self.assertEqualNice({'ATC': 0.5, 'ATA': 0.1, 'ATT': 0.4}, 
                             project.normalize_counts, 
                             {'ATT': 8, 'ATC': 10, 'ATA': 2})

    def test_normalize_counts_2(self):
        self.assertEqualNice(None, 
                             project.normalize_counts, 
                             {'ATT': 0, 'ATC': 0, 'ATA': 0})


@unittest.skipIf(function_not_defined(project, 'normalize_grouped_counts'), 'normalize_grouped_counts')
class TestNormalizeGroupedCounts(AnvProgTestCase):

    def test_normalize_grouped_counts_1(self):
        self.assertEqualNice({'S': {'AGT': 0.0, 'TCG': 0.0, 'TCT': 0.0, 'TCA': 1.0, 'TCC': 0.0, 'AGC': 0.0}, 
                              '*': {'TAA': 0.0, 'TGA': 1.0, 'TAG': 0.0}, 
                              'M': {'ATG': 1.0}}, project.normalize_grouped_counts,
                              {'A': {'GCA': 0, 'GCC': 0, 'GCT': 0, 'GCG': 0}, 
                              'C': {'TGC': 0, 'TGT': 0}, 
                              'E': {'GAG': 0, 'GAA': 0}, 
                              'D': {'GAT': 0, 'GAC': 0}, 
                              'G': {'GGT': 0, 'GGG': 0, 'GGA': 0, 'GGC': 0}, 
                              'F': {'TTC': 0, 'TTT': 0}, 
                              'I': {'ATT': 0, 'ATC': 0, 'ATA': 0}, 
                              'H': {'CAC': 0, 'CAT': 0}, 
                              'K': {'AAG': 0, 'AAA': 0}, 
                              '*': {'TAG': 0, 'TGA': 1, 'TAA': 0}, 
                              'M': {'ATG': 1}, 
                              'L': {'CTT': 0, 'CTG': 0, 'CTA': 0, 'CTC': 0, 'TTA': 0, 'TTG': 0}, 
                              'N': {'AAT': 0, 'AAC': 0}, 
                              'Q': {'CAA': 0, 'CAG': 0},
                              'P': {'CCT': 0, 'CCG': 0, 'CCA': 0, 'CCC': 0}, 
                              'S': {'TCT': 0, 'AGC': 0, 'TCG': 0, 'AGT': 0, 'TCC': 0, 'TCA': 1}, 
                              'R': {'AGG': 0, 'CGC': 0, 'CGG': 0, 'CGA': 0, 'AGA': 0, 'CGT': 0}, 
                              'T': {'ACC': 0, 'ACA': 0, 'ACG': 0, 'ACT': 0}, 
                              'W': {'TGG': 0}, 
                              'V': {'GTA': 0, 'GTC': 0, 'GTT': 0, 'GTG': 0}, 
                              'Y': {'TAT': 0, 'TAC': 0}})


    def test_normalize_grouped_counts_2(self):
        self.assertEqualNice({'S': {'AGT': 0.0, 'TCG': 1.0, 'TCT': 0.0, 'TCA': 0.0, 'TCC': 0.0, 'AGC': 0.0}, 
                              '*': {'TAA': 0.0, 'TGA': 1.0, 'TAG': 0.0}, 
                              'M': {'ATG': 1.0}}, project.normalize_grouped_counts,
                              {'A': {'GCA': 0, 'GCC': 0, 'GCT': 0, 'GCG': 0}, 
                              'C': {'TGC': 0, 'TGT': 0}, 
                              'E': {'GAG': 0, 'GAA': 0}, 
                              'D': {'GAT': 0, 'GAC': 0}, 
                              'G': {'GGT': 0, 'GGG': 0, 'GGA': 0, 'GGC': 0}, 
                              'F': {'TTC': 0, 'TTT': 0}, 
                              'I': {'ATT': 0, 'ATC': 0, 'ATA': 0}, 
                              'H': {'CAC': 0, 'CAT': 0}, 
                              'K': {'AAG': 0, 'AAA': 0}, 
                              '*': {'TAG': 0, 'TGA': 1, 'TAA': 0}, 
                              'M': {'ATG': 1}, 
                              'L': {'CTT': 0, 'CTG': 0, 'CTA': 0, 'CTC': 0, 'TTA': 0, 'TTG': 0}, 
                              'N': {'AAT': 0, 'AAC': 0}, 
                              'Q': {'CAA': 0, 'CAG': 0},
                              'P': {'CCT': 0, 'CCG': 0, 'CCA': 0, 'CCC': 0}, 
                              'S': {'TCT': 0, 'AGC': 0, 'TCG': 7, 'AGT': 0, 'TCC': 0, 'TCA': 0}, 
                              'R': {'AGG': 0, 'CGC': 0, 'CGG': 0, 'CGA': 0, 'AGA': 0, 'CGT': 0}, 
                              'T': {'ACC': 0, 'ACA': 0, 'ACG': 0, 'ACT': 0}, 
                              'W': {'TGG': 0}, 
                              'V': {'GTA': 0, 'GTC': 0, 'GTT': 0, 'GTG': 0}, 
                              'Y': {'TAT': 0, 'TAC': 0}})


    def test_normalize_grouped_counts_3(self):
        self.assertEqualNice({'S': {'AGT': 0.0, 'TCG': 0.5, 'TCT': 0.5, 'TCA': 0.0, 'TCC': 0.0, 'AGC': 0.0}, 
                              '*': {'TAA': 0.0, 'TGA': 1.0, 'TAG': 0.0}, 
                              'M': {'ATG': 1.0}}, project.normalize_grouped_counts,
                              {'A': {'GCA': 0, 'GCC': 0, 'GCT': 0, 'GCG': 0}, 
                              'C': {'TGC': 0, 'TGT': 0}, 
                              'E': {'GAG': 0, 'GAA': 0}, 
                              'D': {'GAT': 0, 'GAC': 0}, 
                              'G': {'GGT': 0, 'GGG': 0, 'GGA': 0, 'GGC': 0}, 
                              'F': {'TTC': 0, 'TTT': 0}, 
                              'I': {'ATT': 0, 'ATC': 0, 'ATA': 0}, 
                              'H': {'CAC': 0, 'CAT': 0}, 
                              'K': {'AAG': 0, 'AAA': 0}, 
                              '*': {'TAG': 0, 'TGA': 1, 'TAA': 0}, 
                              'M': {'ATG': 1}, 
                              'L': {'CTT': 0, 'CTG': 0, 'CTA': 0, 'CTC': 0, 'TTA': 0, 'TTG': 0}, 
                              'N': {'AAT': 0, 'AAC': 0}, 
                              'Q': {'CAA': 0, 'CAG': 0},
                              'P': {'CCT': 0, 'CCG': 0, 'CCA': 0, 'CCC': 0}, 
                              'S': {'TCT': 7, 'AGC': 0, 'TCG': 7, 'AGT': 0, 'TCC': 0, 'TCA': 0}, 
                              'R': {'AGG': 0, 'CGC': 0, 'CGG': 0, 'CGA': 0, 'AGA': 0, 'CGT': 0}, 
                              'T': {'ACC': 0, 'ACA': 0, 'ACG': 0, 'ACT': 0}, 
                              'W': {'TGG': 0}, 
                              'V': {'GTA': 0, 'GTC': 0, 'GTT': 0, 'GTG': 0}, 
                              'Y': {'TAT': 0, 'TAC': 0}})



@unittest.skipIf(function_not_defined(project, 'codon_usage'), 'codon_usage')
class TestCodonBias(AnvProgTestCase):

    def test_codon_usage_1(self):
        self.assertEqualNice({'M': {'ATG': 1.0},
                              '*': {'TAA': 0.0, 'TAG': 0.0, 'TGA': 1.0}}, 
                              project.codon_usage, 
                              'ATGTGA')

    def test_codon_usage_2(self):
        self.assertEqualNice({'P': {'CCG': 0.5, 'CCT': 0.0, 'CCA': 0.5, 'CCC': 0.0}, 
                              'D': {'GAT': 1.0, 'GAC': 0.0}, 
                              'L': {'CTC': 0.2, 'TTG': 0.0, 'CTT': 0.2, 'CTG': 0.0, 'TTA': 0.6, 'CTA': 0.0}, 
                              'M': {'ATG': 1.0}, 
                              'K': {'AAA': 1.0, 'AAG': 0.0}, 
                              'C': {'TGC': 1.0, 'TGT': 0.0}, 
                              '*': {'TAA': 0.0, 'TAG': 0.0, 'TGA': 1.0}}, 
                              project.codon_usage, 
                              'ATGTGCGATCCAAAATTACCGCTTTTATTACTCTGA')


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
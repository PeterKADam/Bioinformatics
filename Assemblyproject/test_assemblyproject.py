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

'''
      TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTCGTCCAGACCCCTAGCTGGTACGTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGTCGTGAACACATCAGT
Read4 TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGC
                         Read2 CTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGG
                                                         Read5 CGATTCCAGGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCT
                                                                 Read1 GGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTCGTCCAGACCCCTAGC
                                                                                          Read6 TGACAGTAGATCTCGTCCAGACCCCTAGCTGGTACGTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGT
                                                                                                                             Read3 GTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGTCGTGAACACATCAGT
'''

test_reads = {'Read1': 'GGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTCGTCCAGACCCCTAGC', 
              'Read6': 'TGACAGTAGATCTCGTCCAGACCCCTAGCTGGTACGTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGT', 
              'Read2': 'CTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGG', 
              'Read5': 'CGATTCCAGGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTC',
              'Read4': 'TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGCG',
              'Read3': 'GTCTTCAGTAGAAAATTGTTTTTTTCTTCCAAGAGGTCGGAGTCGTGAACACATCAGT'}

test_overlaps =  {'Read1': {'Read6': 29, 'Read5': 1, 'Read4': 0, 'Read3': 0, 'Read2': 1}, 
                  'Read3': {'Read1': 0, 'Read5': 0, 'Read6': 1, 'Read4': 1, 'Read2': 0}, 
                  'Read2': {'Read1': 13, 'Read5': 21, 'Read6': 0, 'Read3': 1, 'Read4': 0}, 
                  'Read5': {'Read1': 39, 'Read4': 0, 'Read6': 14, 'Read3': 0, 'Read2': 1}, 
                  'Read6': {'Read1': 0, 'Read5': 0, 'Read4': 1, 'Read3': 43, 'Read2': 0}, 
                  'Read4': {'Read1': 1, 'Read5': 2, 'Read6': 0, 'Read3': 1, 'Read2': 17}}

test_print = """       Read1 Read2 Read3 Read4 Read5 Read6
 Read1     -     1     0     0     1    29
 Read2    13     -     1     0    21     0
 Read3     0     0     -     1     0     1
 Read4     1    17     1     -     2     0
 Read5    39     1     0     0     -    14
 Read6     0     0    43     1     0     -
"""

test_first_read = 'Read4'

test_read_order = ['Read4', 'Read2', 'Read5', 'Read1', 'Read6', 'Read3']


test_genome = 'TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCC' \
              'CACGGGGTACCCATAACTTGACAGTAGATCTCGTCCAGACCCCTAGCTGGTACGTCTTCAGTAGAAAATTGTTT' \
              'TTTTCTTCCAAGAGGTCGGAGTCGTGAACACATCAGT'

@unittest.skipIf(function_not_defined(project, 'read_data'), 'read_data')
class TestExercise1(AnvProgTestCase):

    def test_read_data_returns_dictionary(self):
        reads = project.read_data('sequencing_reads.txt')
        self.assertTrue(isinstance(reads, dict))

    def test_read_data_returns_dictionary_correctly(self):
        reads = project.read_data('sequencing_reads.txt')
        self.assertEqualNice(test_reads, project.read_data, 'sequencing_reads.txt')

@unittest.skipIf(function_not_defined(project, 'mean_length'), 'mean_length')
class TestExercise2(AnvProgTestCase):
    
    def test_mean_length_returns_mean_length_of_sequences1(self):
        reads = {
            'Read1': 'ACGT',
            'Read2': 'ACGTACGT',
        }
        self.assertEqualNice(6, project.mean_length, reads)

    def test_mean_length_returns_mean_length_of_sequences2(self):
        reads = {
            'Read1': 'ACGTTGCA',
            'Read2': 'ACGTACGT',
        }
        self.assertEqualNice(8, project.mean_length, reads)

    def test_mean_length_returns_mean_length_of_sequences3(self):
        reads = {
            'Read1': 'atttaatgtgata',
            'Read2': 'agtgtatgatagtacgcgcgc',
        }
        self.assertEqualNice(17, project.mean_length, reads)


@unittest.skipIf(function_not_defined(project, 'get_overlap'), 'get_overlap')
class TestExercise3(AnvProgTestCase):

    def test_get_overlap_1(self):
        self.assertEqualNice("TTTTT", project.get_overlap, "AAAAATTTTT", "TTTTTTTTTT")

    def test_get_overlap_2(self):
        self.assertEqualNice("", project.get_overlap, "TTTTTTTTTT", "AAAAATTTTT")

    def test_get_overlap_3(self):
        self.assertEqualNice("CTTTACCCGGAAGAGC", project.get_overlap, "TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGC", "CTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGG")

    def test_get_overlap_4(self):
        self.assertEqualNice("CGATTCCAGGCTCCCCACGGG", project.get_overlap, "CTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGG", "CGATTCCAGGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCT")

    def test_get_overlap_5(self):
        self.assertEqualNice("", project.get_overlap, "CTTTACCCGGAAGAGCGGGACGCTGCCCTGCGCGATTCCAGGCTCCCCACGGG", "TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGC")

    def test_get_overlap_6(self):
        self.assertEqualNice("CG", project.get_overlap, "TGCGAGGGAAGTGAAGTATTTGACCCTTTACCCGGAAGAGCG", "CGATTCCAGGCTCCCCACGGGGTACCCATAACTTGACAGTAGATCTC")

@unittest.skipIf(function_not_defined(project, 'get_all_overlaps'), 'get_all_overlaps')
class TestExercise4(AnvProgTestCase):

    def test_get_all_overlaps_1(self):
        self.assertEqualNice({'Read1': {'Read2': 5}, 'Read2': {'Read1': 1}},
                             project.get_all_overlaps, 
                             {'Read1': "AAAAATTTTT", 'Read2': "TTTTTTTTTA"})

    def test_get_all_overlaps_2(self):
        self.assertEqualNice(test_overlaps, project.get_all_overlaps, test_reads)


@unittest.skipIf(function_not_defined(project, 'pretty_print'), 'pretty_print')
class TestExercise5(AnvProgTestCase):

    def test_pretty_print_1(self):
        strio = StringIO()
        with redirect_stdout(strio):
            project.pretty_print(test_overlaps)
        self.assertEqual(strio.getvalue(), test_print)


@unittest.skipIf(function_not_defined(project, 'get_left_overlaps'), 'get_left_overlaps')
class TestGetLeftOverlaps(AnvProgTestCase):

    def test_get_left_overlaps_1(self):
        self.assertEqualNice([0, 0, 0, 1, 1], project.get_left_overlaps, test_overlaps, test_first_read)

    def test_get_left_overlaps_2(self):
        self.assertEqualNice([0, 0, 1, 13, 39] , project.get_left_overlaps, test_overlaps, 'Read1')


@unittest.skipIf(function_not_defined(project, 'find_first_read'), 'find_first_read')
class TestExercise6(AnvProgTestCase):

    def test_find_first_read_1(self):
        self.assertEqualNice(test_first_read, project.find_first_read, test_overlaps)


@unittest.skipIf(function_not_defined(project, 'find_key_for_largest_value'), 'find_key_for_largest_value')
class TestExercise7(AnvProgTestCase):
    
    def test_find_key_for_largest_value_1(self):
        self.assertEqualNice('B', project.find_key_for_largest_value, {'A': 3, 'B': 5, 'C': 2})

    def test_find_key_for_largest_value_2(self):
        self.assertEqualNice('Read1', project.find_key_for_largest_value, test_overlaps['Read5'])


@unittest.skipIf(function_not_defined(project, 'find_order_of_reads'), 'find_order_of_reads')
class TestFindOrderOfReads(AnvProgTestCase):
    
    def test_find_order_of_reads_1(self):
        self.assertEqualNice(['A', 'B', 'C'], 
            project.find_order_of_reads, 'A', {'C': {'A': 0, 'B': 2}, 'A': {'B': 15, 'C': 1}, 'B': {'A': 0, 'C': 11}})

    def test_find_order_of_reads_2(self):
        self.assertEqualNice(['Read4', 'Read2', 'Read5', 'Read1', 'Read6', 'Read3'], 
            project.find_order_of_reads, 'Read4', test_overlaps)


@unittest.skipIf(function_not_defined(project, 'reconstruct_sequence'), 'reconstruct_sequence')
class TestExercise8(AnvProgTestCase):
    
    def test_reconstruct_sequence_1(self):
        self.assertEqualNice('AAAAATTTTTTTTTA', project.reconstruct_sequence, ['Read1', 'Read2'], 
            {'Read1': "AAAAATTTTT", 'Read2': "TTTTTTTTTA"}, {'Read1': {'Read2': 5}, 'Read2': {'Read1': 1}})

    def test_reconstruct_sequence_2(self):
        self.assertEqualNice(test_genome, project.reconstruct_sequence, test_read_order, test_reads, test_overlaps)


@unittest.skipIf(function_not_defined(project, 'assemble_genome'), 'assemble_genome')
class TestExercise9(AnvProgTestCase):

    def test_assemble_genome_1(self):
        self.assertEqualNice(test_genome, project.assemble_genome, 'sequencing_reads.txt')


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
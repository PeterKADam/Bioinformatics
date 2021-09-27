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

score_matrix = {'A': {'A': 2, 'T': 0, 'G': 0, 'C': 0},
                'T': {'A': 0, 'T': 2, 'G': 0, 'C': 0},
                'G': {'A': 0, 'T': 0, 'G': 2, 'C': 0},
                'C': {'A': 0, 'T': 0, 'G': 0, 'C': 2},}

gap_score = -2

@unittest.skipIf(function_not_defined(project, 'empty_matrix'), 'empty_matrix')
class TestEmptyMatrix(AnvProgTestCase):

    
    def test_empty_matrix_1(self):
        self.assertEqualNice([[None, None, None, None],
                              [None, None, None, None], 
                              [None, None, None, None]], 
                             project.empty_matrix, 
                             3, 4)

    def test_empty_matrix_2(self):
        self.assertEqualNice([[None, None, None],
                              [None, None, None],
                              [None, None, None],
                              [None, None, None]], 
                             project.empty_matrix, 
                             4, 3)


    def test_empty_matrix_3(self):

        import itertools
        
        m = project.empty_matrix(3, 3)
        message = """
The list of lists returned contain multiple references to the same list. 

When you create the list of lists, you need to generate and add three *separate*
lists. If you add the same list multiple times the sublists in your list of lists
will. They will all be references to of the exact same sublist, and a change to a
value in one sublist will change *all* the sublists. This is obviously not what 
you want. You can try this to see if you did it right: by changing the value of 
one cell to see what happens: 

empty = empty_matrix(3, 4)
empty[0] = 'Mogens'
print(empty)

If this only changed *one* value like below, you are ok:

[['Mogens', None, None, None], [None, None, None, None], [None, None, None, None]]

If it changed the first value in *all* the lists, it means that all your lists are the same.


[['Mogens', None, None, None], ['Mogens', None, None, None], ['Mogens', None, None, None]]
        """

        self.assertTrue(all(x is not y for x, y in itertools.combinations(m, 2)), message)


# @unittest.skipIf(function_not_defined(project, 'prepare_matrix'), 'prepare_matrix')
# class TestPrepareMatrix(AnvProgTestCase):
    
#     def test_prepare_matrix_1(self):
#         self.assertEqualNice([[0, -2, -4, -6],
#                               [-2, None, None, None], 
#                               [-4, None, None, None]], 
#                              project.prepare_matrix, 
#                              3, 4, -2)     

#     def test_prepare_matrix_2(self):
#         self.assertEqualNice([[0, -1, -2, -3],
#                               [-1, None, None, None], 
#                               [-2, None, None, None]], 
#                              project.prepare_matrix, 
#                              3, 4, -1)     

#     def test_prepare_matrix_3(self):
#         self.assertEqualNice([[0, -2, -4],
#                               [-2, None, None], 
#                               [-4, None, None], 
#                               [-6, None, None]], 
#                              project.prepare_matrix, 
#                              4, 3, -2)     

#     def test_prepare_matrix_4(self):
#         self.assertEqualNice([[0, -2, -4],
#                               [-2, None, None], 
#                               [-4, None, None]], 
#                              project.prepare_matrix, 
#                              3, 3, -2)     

@unittest.skipIf(function_not_defined(project, 'fill_matrix'), 'fill_matrix')
class TestFillMatrix(AnvProgTestCase):
    
    def test_fill_matrix_1(self):
       self.assertEqualNice([[0, -2, -4, -6], 
                             [-2, 0, 0, -2], 
                             [-4, -2, 0, 2]],
                             project.fill_matrix, 
                             "AT", "GAT", score_matrix, -2)

    def test_fill_matrix_2(self):
       self.assertEqualNice([[0, -2, -4], [-2, 2, 0], [-4, 0, 2], [-6, -2, 2]],
                             project.fill_matrix, 
                             "GTC", "GC", score_matrix, -2)

@unittest.skipIf(function_not_defined(project, 'get_traceback_arrow'), 'get_traceback_arrow')
class TestGetTracebackArrow(AnvProgTestCase):
    
    def test_get_traceback_arrow_1(self):
       self.assertEqualNice("diagonal",
                            project.get_traceback_arrow,
                            [[0, -1, -2], [-1, 2, 1], [-2, 1, 2], [-3, 0, 3]],
                            3, 2,
                            2, -1)

    def test_get_traceback_arrow_2(self):
       self.assertEqualNice("up",
                            project.get_traceback_arrow,
                            [[0, -1, -2], [-1, 2, 1], [-2, 1, 2], [-3, 0, 3]],
                            2, 1,
                            0, -1)

    def test_get_traceback_arrow_3(self):        
       self.assertEqualNice("left",
                            project.get_traceback_arrow, 
                            [[0, -1, -2, -3], [-1, 2, 1, 0], [-2, 1, 2, 3]],
                            1, 2,
                            0, -1)

@unittest.skipIf(function_not_defined(project, 'trace_back'), 'trace_back')
class TestTraceBack(AnvProgTestCase):
    
    def test_trace_back_1(self):
       self.assertEqualNice(['G-C', 'GTC'],
                            project.trace_back, 
                            'GC', 'GTC',
                            [[0, -1, -2, -3], [-1, 2, 1, 0], [-2, 1, 2, 3]],
                            score_matrix, -1)

    def test_trace_back_2(self):
       self.assertEqualNice(['-AT', 'GAT'],
                            project.trace_back, 
                            'AT', 'GAT',
                            [[0, -1, -2, -3], [-1, 0, 1, 0], [-2, -1, 0, 3]],
                            score_matrix, -1)

    def test_trace_back_3(self):
       self.assertEqualNice(['-AT-AT', 'GATGAT'],
                            project.trace_back, 
                            'ATAT', 'GATGAT',
                            [[0, -1, -2, -3, -4, -5, -6], 
                             [-1, 0, 1, 0, -1, -2, -3],
                             [-2, -1, 0, 3, 2, 1, 0],
                             [-3, -2, 1, 2, 3, 4, 3],
                             [-4, -3, 0, 3, 2, 3, 6]],
                            score_matrix, -1)

@unittest.skipIf(function_not_defined(project, 'align'), 'align')
class TestAlign(AnvProgTestCase):
    
    def test_align_1(self):
       self.assertEqualNice(['G-C', 'GTC'],
                            project.align, 
                            'GC', 'GTC',
                            score_matrix, -1)

    def test_align_2(self):
       self.assertEqualNice(['-AT', 'GAT'],
                            project.align, 
                            'AT', 'GAT',
                            score_matrix, -1)

    def test_align_3(self):
       self.assertEqualNice(['-AT-AT', 'GATGAT'],
                            project.align, 
                            'ATAT', 'GATGAT',
                            score_matrix, -1)


if __name__ == '__main__':
    cases = suiteFactory(*caseFactory())
    if GRADE_MODE:
       failfast=False
    else:
       failfast=True
    runner = AnvProgTestRunner(failfast=failfast)
    test_result = runner.run(cases)
    sys.exit(int(not test_result.wasSuccessful()))
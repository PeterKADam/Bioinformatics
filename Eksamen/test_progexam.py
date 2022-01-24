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

@unittest.skipIf(function_not_defined(project, 'seq_length'), 'seq_length')
class Test_seq_length(AnvProgTestCase):

    def test_seq_length_01(self):
        self.assertEqualNice(
            4,
            project.seq_length, 'ALVM')
    
    def test_seq_length_02(self):
        self.assertEqualNice(
            1,
            project.seq_length, 'M')  

    def test_seq_length_03(self):
        self.assertEqualNice(
            8,
            project.seq_length, 'MALVRGLV')  

@unittest.skipIf(function_not_defined(project, 'same_length'), 'same_length')
class Test_same_length(AnvProgTestCase):

    def test_same_length_01(self):
        self.assertEqualNice(
            True,
            project.same_length, 'ALVM', [41, 97, 76, 74])
    
    def test_same_length_02(self):
        self.assertEqualNice(
            False,
            project.same_length, 'LRN', [97, -14])
    
    def test_same_length_03(self):
        self.assertEqualNice(
            False,
            project.same_length, 'CTHG', [])

@unittest.skipIf(function_not_defined(project, 'aminoacid_counts'), 'aminoacid_counts')
class Test_aminoacid_counts(AnvProgTestCase):

    def test_aminoacid_counts_01(self):
        self.assertEqualNice(
            {'C': 2, 'T': 1, 'G': 1, 'L': 3},
            project.aminoacid_counts, 'CTGLLCL')
    
    def test_aminoacid_counts_02(self):
        self.assertEqualNice(
            {'L': 5},
            project.aminoacid_counts, 'LLLLL')  

    def test_aminoacid_counts_03(self):
        self.assertEqualNice(
            {'C': 1, 'T': 1, 'G': 1, 'L': 1},
            project.aminoacid_counts, 'CTGL')     

@unittest.skipIf(function_not_defined(project, 'mean_hydrophobicity'), 'mean_hydrophobicity')
class Test_mean_hydrophobicity(AnvProgTestCase):

    def test_mean_hydrophobicity_01(self):
        self.assertEqualNice(
            5,
            project.mean_hydrophobicity, [7, 3, 8, 2])
    
    def test_mean_hydrophobicity_02(self):
        self.assertEqualNice(
            5,
            project.mean_hydrophobicity, [5, 5])    
    
    def test_mean_hydrophobicity_03(self):
        self.assertEqualNice(
            0,
            project.mean_hydrophobicity, [5, -5])  

    def test_mean_hydrophobicity_04(self):
        self.assertEqualNice(
            7.5,
            project.mean_hydrophobicity, [6, 9])                                                                 

@unittest.skipIf(function_not_defined(project, 'running_mean'), 'running_mean')
class Test_running_mean(AnvProgTestCase):

    def test_running_mean_01(self):
        self.assertEqualNice(
            [1.0, 2.0, 2.0, 2.0, 1.0],
            project.running_mean, [1, 1, 1, 4, 1, 1, 1], 3)
            
    def test_running_mean_02(self):
        self.assertEqualNice(
            [1.5, 2.5, 3.5, 4.5, 5.5],
            project.running_mean, [1, 2, 3, 4, 5, 6], 2)
        
    def test_running_mean_03(self):
        self.assertEqualNice(
            [5.0, 5.0, 5.0],
            project.running_mean, [5, 5, 5, 5, 5, 5], 4)

    def test_running_mean_04(self):
        self.assertEqualNice(
            [99.0],
            project.running_mean, [99], 1)

    def test_running_mean_05(self):
        self.assertEqualNice(
            [3.0],
            project.running_mean, [3, 3], 2)

    def test_running_mean_06(self):
        self.assertEqualNice(
            [],
            project.running_mean, [3], 2)

@unittest.skipIf(function_not_defined(project, 'find_hydrophobic'), 'find_hydrophobic')
class Test_find_hydrophobic(AnvProgTestCase):

    def test_find_hydrophobic_01(self):
        self.assertEqualNice(
            ['F', 'I', 'L'],
            project.find_hydrophobic, 'FIPNL', [100, 99, -46, -55, 97])
    
    def test_find_hydrophobic_02(self):
        self.assertEqualNice(
            [],
            project.find_hydrophobic, 'SQRPN', [-5, -10, -14, -46, -55]) 

    def test_find_hydrophobic_03(self):
        self.assertEqualNice(
            ['V', 'M', 'Y', 'C', 'A', 'T'],
            project.find_hydrophobic, 'VMYCAT', [76, 74, 63, 49, 41, 13])

    def test_find_hydrophobic_04(self):
        self.assertEqualNice(
            ['H'],
            project.find_hydrophobic, 'HGS', [8, 0, -5])                               

@unittest.skipIf(function_not_defined(project, 'mask_hydrophobic_aa'), 'mask_hydrophobic_aa')
class Test_mask_hydrophobic_aa(AnvProgTestCase):

    def test_mask_hydrophobic_aa_01(self):
        self.assertEqualNice(
            'vmycat',
            project.mask_hydrophobic_aa, 'VMYCAT', [76, 74, 63, 49, 41, 13])
    
    def test_mask_hydrophobic_aa_02(self):
        self.assertEqualNice(
            'SQRPN',
            project.mask_hydrophobic_aa, 'SQRPN', [-5, -10, -14, -46, -55])    

    def test_mask_hydrophobic_aa_03(self):
        self.assertEqualNice(
            'fiPNl',
            project.mask_hydrophobic_aa, 'FIPNL', [100, 99, -46, -55, 97])    

    def test_mask_hydrophobic_aa_04(self):
        self.assertEqualNice(
            'fG',
            project.mask_hydrophobic_aa, 'FG', [100, 0])   

@unittest.skipIf(function_not_defined(project, 'hydrophobic_subseqs'), 'hydrophobic_subseqs')
class Test_hydrophobic_subseqs(AnvProgTestCase):

    def test_hydrophobic_subseqs_01(self):
        self.assertEqualNice(
            ['ILV', 'LMYF', 'W'],
            project.hydrophobic_subseqs, 'ILVSLMYFEW', [99, 97, 76, -5, 97, 74, 63, 100, -31, 97])
    
    def test_hydrophobic_subseqs_02(self):
        self.assertEqualNice(
            ['VMYCAT'],
            project.hydrophobic_subseqs, 'VMYCAT', [76, 74, 63, 49, 41, 13])
    
    def test_hydrophobic_subseqs_03(self):
        self.assertEqualNice(
            [],
            project.hydrophobic_subseqs, 'SQRPN', [-5, -10, -14, -46, -55])
    
    def test_hydrophobic_subseqs_04(self):
        self.assertEqualNice(
            ['V', 'M'],
            project.hydrophobic_subseqs, 'VSM', [76, -5, 74])    

@unittest.skipIf(function_not_defined(project, 'neighbor_hydrophobicity'), 'neighbor_hydrophobicity')
class Test_neighbor_hydrophobicity(AnvProgTestCase):

    def test_neighbor_hydrophobicity_01(self):
        self.assertEqualNice(
            {'G': 45.0, 'F': 0.0, 'Q': 4.0, 'H': -10},
            project.neighbor_hydrophobicity, 'FGQH', [100, 0, -10, 8])
    
    def test_neighbor_hydrophobicity_02(self):
        self.assertEqualNice(
            {'H': 8.0},
            project.neighbor_hydrophobicity, 'HHHHHH', [8, 8, 8, 8, 8, 8])

    def test_neighbor_hydrophobicity_03(self):
        self.assertEqualNice(
            {'G': 8.0, 'H': 0.0},
            project.neighbor_hydrophobicity, 'GHGHGH', [0, 8, 0, 8, 0, 8])

    def test_neighbor_hydrophobicity_04(self):
        self.assertEqualNice(
            {'G': 8.0, 'H': 0.0},
            project.neighbor_hydrophobicity, 'GH', [0, 8])

    def test_neighbor_hydrophobicity_05(self):
        self.assertEqualNice(
            {'V': 0.0, 'G': 83.0, 'L': 0.0},
            project.neighbor_hydrophobicity, 'GVGL', [0, 76, 0, 97])

    # def test_neighbor_hydrophobicity_04(self):
    #     self.assertEqualNice(
    #         {'G': 8.0, 'H': 0.0},
    #         project.neighbor_hydrophobicity, 'QHGH', [-10, 8, 0, 8])

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
    runner.run(cases)
    
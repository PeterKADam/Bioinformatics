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

def read_data(file_name):
    f = open(file_name, 'r')
    sequences = list()
    for line in f:
        seq = line.strip()
        sequences.append(seq)
    f.close()
    return sequences

unknown_list = read_data('unknown_type.txt')

def load_typed_sequences():
    return {'A': read_data('subtypeA.txt'),
            'B': read_data('subtypeB.txt'),
            'C': read_data('subtypeC.txt'),
            'D': read_data('subtypeD.txt') }

typed_data = load_typed_sequences()

@unittest.skipIf(function_not_defined(project, 'sequence_similarity'), 'sequence_similarity')
class TestSequenceSimilarity(AnvProgTestCase):

    # def test_aaa_sequence_similarity_function_exists(self):
    #     self.assertFunctionDefined(project, 'sequence_similarity')

    # def test_aab_sequence_similarity_function_parameters(self):
    #     self.assertFunctionPosParams(project.sequence_similarity, '(seq1, seq2)')

    def test_sequence_similarity_1(self):
        self.assertEqualNice(0.75,
                             project.sequence_similarity, 'AGTC', 'AGTT')

    def test_sequence_similarity_2(self):
        self.assertEqualNice(
            1.0, project.sequence_similarity, 'AAAA', 'AAAA')

    def test_sequence_similarity_3(self):
        self.assertEqualNice(
            0.0, project.sequence_similarity, 'ACGT', 'TGCA')

    def test_sequence_similarity_4(self):
        self.assertEqualNice(1.0, project.sequence_similarity,
                             'ACGTACGTACGT', 'ACGTACGTACGT')

    def test_sequence_similarity_5(self):
        self.assertEqualNice(11 / 12, project.sequence_similarity,
                             'AAAAAAAAAAAA', 'AAAAAAAAAAAT')

    def test_sequence_similarity_6(self):
        self.assertEqualNice(2 / 6, project.sequence_similarity,
                             'BANANA', 'BATMAN')


@unittest.skipIf(function_not_defined(project, 'alignment_similarity'), 'alignment_similarity')
class TestAlignmentSimilarity(AnvProgTestCase):

    # def test_aaa_alignment_similarity_function_exists(self):
    #     self.assertFunctionDefined(project, 'alignment_similarity')

    # def test_aab_alignment_similarity_function_parameters(self):
    #     self.assertFunctionPosParams(project.alignment_similarity, '(seq1, seq2)')

    def test_alignment_similarity_1(self):
        self.assertEqualNice(0.8, project.alignment_similarity,
                             'A-CT-A', 'A-CTTA')

    def test_alignment_similarity_2(self):
        self.assertEqualNice(2 / 7, project.alignment_similarity,
                             'A-A-A-A', 'AA-A-AA')

    def test_alignment_similarity_3(self):
        self.assertEqualNice(2 / 5, project.alignment_similarity,
                             'A-----A',
                             'AA-A-AA')


@unittest.skipIf(function_not_defined(project, 'read_data'), 'read_data')
class TestReadData(AnvProgTestCase):


    def test_read_data_1(self):
        l = project.read_data('subtypeA.txt')        
        self.assertTrue(len(l) == 5 and all(type(x) is str for x in l),
                        'read_data does not return a list of five sequences from subtypeA.txt')

    def test_read_data_2(self):
        l = project.read_data('subtypeB.txt')        
        self.assertTrue(len(l) == 4 and all(type(x) is str for x in l),
                        'read_data does not return a list of four sequences from subtypeB.txt')

    def test_read_data_4(self):
        l = project.read_data('subtypeC.txt')        
        self.assertTrue(len(l) == 4 and all(type(x) is str for x in l),
                        'read_data does not return a list of four sequences from subtypeC.txt')

    def test_read_data_5(self):
        l = project.read_data('subtypeD.txt')        
        self.assertTrue(len(l) == 4 and all(type(x) is str for x in l),
                        'read_data does not return a list of four sequences from subtypeD.txt')

    # def test_bbb_has_defined_subtypeA_list(self):
    #     self.assertTrue(hasattr(project, 'subtypeA_list'),
    #                     'The variable `subtypeA_list` has not been defined.')

    # def test_bbc_has_defined_subtypeB_list(self):
    #     self.assertTrue(hasattr(project, 'subtypeB_list'),
    #                     'The variable `subtypeB_list` has not been defined.')

    # def test_bbd_has_defined_subtypeC_list(self):
    #     self.assertTrue(hasattr(project, 'subtypeC_list'),
    #                     'The variable `subtypeC_list` has not been defined.')

    # def test_bbe_has_defined_subtypeD_list(self):
    #     self.assertTrue(hasattr(project, 'subtypeD_list'),
    #                     'The variable `subtypeD_list` has not been defined.')

    # def test_bbf_has_defined_unknown_list(self):
    #     self.assertTrue(hasattr(project, 'unknown_list'),
    #                     'The variable `unknown_list` has not been defined.')

@unittest.skipIf(function_not_defined(project, 'load_typed_sequences'), 'load_typed_sequences')
class TestLoadTypedSequences(AnvProgTestCase):

    def test_load_typed_sequences_1(self):
        self.assertTrue(isinstance(project.load_typed_sequences(), dict))

    def test_load_typed_sequences_2(self):
        d = project.load_typed_sequences()
        self.assertEqual(len(d), 4)

    def test_load_typed_sequences_3(self):
        d = project.load_typed_sequences()
        for key in ('A', 'B', 'C', 'D'):            
            self.assertTrue(key in d, '{} is not a key in the returned dictionary'.format(key))

        # self.assertIn('A', d)
        # self.assertIn('B', d)
        # self.assertIn('C', d)
        # # self.assertIn('D', d)

    def test_load_typed_sequences_4(self):
        d = project.load_typed_sequences()        
        self.assertTrue(all(type(x) is list for x in d.values()),
            "The values in the dictionary are not all lists")



@unittest.skipIf(function_not_defined(project, 'get_similarities'), 'get_similarities')
class TestGetSimilarities(AnvProgTestCase):

    # def test_aaa_get_similarities_function_exists(self):
    #     self.assertFunctionDefined(project, 'read_data')

    # def test_aab_get_similarities_function_parameters(self):
    #     self.assertFunctionPosParams(
    #         project.get_similarities, '(unknown, typed_sequences)')

    def test_get_similarities_should_return_a_list_size_one_if_typed_sequences_has_size_one(self):
        self.assertEqual(len(project.get_similarities(
            unknown_list[0], typed_data['A'][0:1])), 1)

    def test_get_similarities_should_return_a_list_size_two_if_typed_sequences_has_size_one(self):
        self.assertEqual(len(project.get_similarities(
            unknown_list[0], typed_data['A'][0:2])), 2)

    def test_get_similarities_should_return_a_list_size_five_if_typed_sequences_has_size_one(self):
        self.assertEqual(len(project.get_similarities(
            unknown_list[0], typed_data['A'])), 5)

    def test_get_similarities_should_return_the_similarity_between_the_unknown_sequence_and_the_other_sequences(self):
        self.assertEqual(project.get_similarities(
            'acgt', ['acgt', 'acct', 'tgca']), [1.0, 0.75, 0.0])


@unittest.skipIf(function_not_defined(project, 'get_max_similarities'), 'get_max_similarities')
class TestExercise5(AnvProgTestCase):

    # def test_aaa_get_all_similarities_function_exists(self):
    #     self.assertFunctionDefined(project, 'get_max_similarities')

    # def test_aab_get_all_similarities_function_parameters(self):
    #     self.assertFunctionPosParams(project.get_all_similarities, '(unknown)')

    def test_get_all_similarities_returns_a_dictionary(self):
        self.assertTrue(isinstance(
            project.get_max_similarities(unknown_list[0], typed_data), dict))

    def test_get_all_similarities_returns_a_dictionary_with_four_keys_ABCD(self):
        res = project.get_max_similarities(unknown_list[0], typed_data)
        self.assertEqual(len(res), 4)
        self.assertIn('A', res)
        self.assertIn('B', res)
        self.assertIn('C', res)
        self.assertIn('D', res)

    def test_get_all_similarities_returns_the_correct_similarities(self):
        s = project.get_max_similarities(unknown_list[0], typed_data)
        self.assertAlmostEqual(s['A'], 0.8721742704480066,
                               'get_all_similarities returned the wrong similarity for subtype A.')
        self.assertAlmostEqual(s['B'], 0.8286861234675057,
                               'get_all_similarities returned the wrong similarity for subtype B.')
        self.assertAlmostEqual(s['C'], 0.8232432432432433,
                               'get_all_similarities returned the wrong similarity for subtype C.')
        self.assertAlmostEqual(s['D'], 0.8365436349940816,
                               'get_all_similarities returned the wrong similarity for subtype D.')


@unittest.skipIf(function_not_defined(project, 'predict_subtype'), 'predict_subtype')
class TestPredictSubtype(AnvProgTestCase):

    def test_predict_subtype_1(self):
        self.assertEqual(project.predict_subtype(unknown_list[0], typed_data), 'A')



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

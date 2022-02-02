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

IN_GRADE_MODE = os.getenv('GRADE_MODE')

class NullDevice:

    def write(self, s):
        pass

# Redirect all stdout from the imported module to a null device to not confuse
# the student too much...
try:
    with redirect_stdout(NullDevice()):
        import progexam as project
except:
    print("Python cannot run your code:\n")
    traceback.print_exc(file=sys.stdout)
    print("\nFix that first before you use test script")
    sys.exit(99)


assertion_msg = """The call:

    {func}({args})

returned:

    {actual}

However, it should return:

    {expected}
"""


def function_not_defined(module, func_name):
    return not (hasattr(module, func_name) and callable(getattr(module, func_name)))


def indent(text, indent=4):
    return '\n'.join([(indent * ' ') + line for line in text.splitlines()])


def skip_initial_nonlocal(tb):
    if tb is None:
        return tb
    if os.path.isabs(tb.tb_frame.f_code.co_filename):
        return skip_initial_nonlocal(tb.tb_next)
    return tb


class AnvProgTestResult(TestResult):
    separator = '=' * 70

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = False
        self.dots = True
        self.descriptions = descriptions

        if IN_GRADE_MODE:
            report_file = os.path.splitext(os.path.basename(__file__))[0] + '.csv'
            self.file = open(report_file, 'w')

        match = re.search(r'assignment_(au\d+)_attempt', os.path.basename(os.getcwd()))
        if match:
            self.student_id = match.group(1)
        else:
            self.student_id = 'NA'

    def addError(self, test, err):
        super().addError(test, err)
        errcls, errobj, tb = err
        new_tb = skip_initial_nonlocal(tb)

        if IN_GRADE_MODE:
            self.file.write('{},{},{},{}\n'.format(self.student_id, test.__class__.__name__, test._testMethodName, 'error'))
            self.file.flush()

        self.stream.writeln(
            'ERROR DURING TEST CASE: {}'.format(test._testMethodName))
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
        self.stream.writeln(
            indent('\n'.join(traceback.format_tb(new_tb))))
        self.stream.writeln()
        self.stream.writeln(self.separator)
        self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        _, errobj, tb = err

        if IN_GRADE_MODE:
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

        self.stream.writeln(self.separator)
        self.stream.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)

        if IN_GRADE_MODE:
            self.file.write('{},{},{},{}\n'.format(self.student_id, test.__class__.__name__, test._testMethodName, 'skipped'))
            self.file.flush()

        # self.stream.write(
        #     'ATTENTION! Testing of "{}" were skipped because the function was not defined. '.format(reason))
        # self.stream.writeln(
        #     'This counts as not completing the exercise. Please make sure that this is what you intended!')
        self.stream.writeln(
            'ATTENTION! A test of "{}" was skipped because this function was not defined. '.format(reason))
        self.stream.writeln(
            'Functions not correctly defined are marked as FAILED. Please make sure this is what you intended!')
        self.stream.writeln('')
        self.stream.flush()

    def addExpectedFailure(self, test, err):
        raise NotImplementedError()

    def addUnexpectedSuccess(self, test):
        raise NotImplementedError()


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
        if isinstance(expected, float) or isinstance(actual, float):
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

# def get_number_of_bases(s):
# def count_different_bases(s):
# def reverse_complement(s):
# def count_cpg(s):
# def melting_temp(s):
# def count_kmers(s, k):
# def kmer_profile(s, maxk):
# def has_hairpin(s, k):
# def substitutions(s1, s2):
# def self_comparison(s):
# def better_self_comparison(s, x):

@unittest.skipIf(function_not_defined(project, 'get_number_of_bases'), 'get_number_of_bases')
class Test01_GetNumberOfBasess(AnvProgTestCase):

    # def test_XXXX_1(self):
    #     self.assertTrue(isinstance(
    #         project.XXXX('AATGA'), list))

    # def test_XXXX_2(self):
    #     self.assertTrue(isinstance(project.XXXX(''), list))

    def test_get_number_of_bases_1(self):
        self.assertEqualNice(
            3, project.get_number_of_bases, 'ATG')

    def test_get_number_of_bases_2(self):
        self.assertEqualNice(
            0, project.get_number_of_bases, '')


@unittest.skipIf(function_not_defined(project, 'count_bases'), 'count_bases')
class Test02_CountBases(AnvProgTestCase):

    def test_count_bases_1(self):
        self.assertEqualNice(
            {'A': 1, 'C': 0, 'G': 2, 'T': 1}, project.count_bases, 'ATGG')

    def test_count_bases_2(self):
        self.assertEqualNice(
            {'A': 1, 'T': 1, 'G': 2, 'C': 2}, project.count_bases, 'ATGGCC')

    def test_count_bases_3(self):
        self.assertEqualNice(
            {'A': 0, 'T': 0, 'G': 0, 'C': 0}, project.count_bases, '')


@unittest.skipIf(function_not_defined(project, 'reverse_complement'), 'reverse_complement')
class Test03_ReverseComplement(AnvProgTestCase):

    def test_reverse_complement_1(self):
        self.assertEqualNice(
            'GCAT', project.reverse_complement, 'ATGC')

    def test_reverse_complement_2(self):
        self.assertEqualNice(
            '', project.reverse_complement, '')

    def test_reverse_complement_2(self):
        self.assertEqualNice(
            'TTTTTTT', project.reverse_complement, 'AAAAAAA')


@unittest.skipIf(function_not_defined(project, 'count_cpg'), 'count_cpg')
class Test04_CountCpG(AnvProgTestCase):

    def test_count_cpg_1(self):
        self.assertEqualNice(
            1, project.count_cpg, 'ATCGAT')

    def test_count_cpg_2(self):
        self.assertEqualNice(
            0, project.count_cpg, '')

    def test_count_cpg_3(self):
        self.assertEqualNice(
            0, project.count_cpg, 'AAAAAA')

    def test_count_cpg_4(self):
        self.assertEqualNice(
            4, project.count_cpg, 'CGCGCGCG')

    def test_count_cpg_5(self):
        self.assertEqualNice(
            3, project.count_cpg, 'GCGCGCGC')

@unittest.skipIf(function_not_defined(project, 'melting_temp'), 'melting_temp')
class Test05_MeltingTemp(AnvProgTestCase):

    def test_melting_temp_1(self):
        self.assertEqualNice(
            8, project.melting_temp, 'ATG')

    def test_melting_temp_2(self):
        self.assertEqualNice(
            51.78000000000001, project.melting_temp, 'AAAAATTTTTCCCCCGGGGG')


@unittest.skipIf(function_not_defined(project, 'count_kmers'), 'count_kmers')
class Test06_CountKmers(AnvProgTestCase):

    def test_count_kmers_1(self):
        self.assertEqualNice(
            {'TA': 2, 'AT': 3}, project.count_kmers, 'ATATAT', 2)

    def test_count_kmers_2(self):
        self.assertEqualNice(
            {'AA': 5}, project.count_kmers, 'AAAAAA', 2)

    def test_count_kmers_3(self):
        self.assertEqualNice(
            {'A': 6}, project.count_kmers, 'AAAAAA', 1)

    def test_count_kmers_4(self):
        self.assertEqualNice(
            {}, project.count_kmers, '', 2)

@unittest.skipIf(function_not_defined(project, 'kmer_profile'), 'kmer_profile')
class Test07_KmerProfile(AnvProgTestCase):

    def test_kmer_profile_1(self):
        self.assertEqualNice(
            {2: {'AT': 3, 'TA': 2}, 3: {'ATA': 2, 'TAT': 2}, 4: {'TATA': 1, 'ATAT': 2}, 5: {'TATAT': 1, 'ATATA': 1}}, project.kmer_profile, 'ATATAT', 5)

    def test_kmer_profile_2(self):
        self.assertEqualNice(
            {2: {'AT': 2, 'TA': 2}, 3: {'ATA': 2, 'TAT': 1}, 4: {'TATA': 1, 'ATAT': 1}, 5: {'ATATA': 1}, 6: {}}, project.kmer_profile, 'ATATA', 6)

    def test_kmer_profile_3(self):
        self.assertEqualNice(
            {2: {}}, project.kmer_profile, '', 2)


@unittest.skipIf(function_not_defined(project, 'has_hairpin'), 'has_hairpin')
class Test08_HasHairpin(AnvProgTestCase):

    def test_has_hairpin_1(self):
        self.assertEqualNice(
            True, project.has_hairpin, 'ATATCCCCATAT', 4)

    def test_has_hairpin_2(self):
        self.assertEqualNice(
            False, project.has_hairpin, 'ATATCCATAT', 4)

    def test_has_hairpin_3(self):
        self.assertEqualNice(
            False, project.has_hairpin, 'ATCCCCAT', 4)

    def test_has_hairpin_4(self):
        self.assertEqualNice(
            True, project.has_hairpin, 'ATCCCCAT', 2)

    def test_has_hairpin_5(self):
        self.assertEqualNice(
            True, project.has_hairpin, 'GGGGATATCCCCATAT', 4)


@unittest.skipIf(function_not_defined(project, 'substitutions'), 'substitutions')
class Test09_Substitutions(AnvProgTestCase):

    def test_substitutions_1(self):
        self.assertEqualNice(
            [1, 2], project.substitutions, "AAAAAAA", "AGAAATTA")

    def test_substitutions_2(self):
        self.assertEqualNice(
            [0, 0], project.substitutions, "AAAAAAA", "AAAAAAA")

    def test_substitutions_3(self):
        self.assertEqualNice(
            [0, 0], project.substitutions, "", "")

    def test_substitutions_4(self):
        self.assertEqualNice(
            [3, 0], project.substitutions, "AAA", "GGG")


@unittest.skipIf(function_not_defined(project, 'self_comparison'), 'self_comparison')
class Test10_SelfComparison(AnvProgTestCase):

    def test_self_comparison_1(self):
        self.assertEqualNice(
            [[1, 1, 1, 0, 0, 0, 0], 
             [1, 1, 1, 0, 0, 0, 0], 
             [1, 1, 1, 0, 0, 0, 0], 
             [0, 0, 0, 1, 0, 0, 0], 
             [0, 0, 0, 0, 1, 1, 1], 
             [0, 0, 0, 0, 1, 1, 1], 
             [0, 0, 0, 0, 1, 1, 1]], project.self_comparison, 'AAATGGG')


    def test_self_comparison_2(self):
        self.assertEqualNice(
            [[1, 0, 0, 0],
             [0, 1, 0, 0], 
             [0, 0, 1, 0], 
             [0, 0, 0, 1]], project.self_comparison, 'ATGC')

    def test_self_comparison_3(self):
        self.assertEqualNice(
            [[1, 1, 1, 1],
             [1, 1, 1, 1], 
             [1, 1, 1, 1], 
             [1, 1, 1, 1]], project.self_comparison, 'AAAA')


@unittest.skipIf(function_not_defined(project, 'better_self_comparison'), 'better_self_comparison')
class Test11_BetterSelfComparison(AnvProgTestCase):

    def test_better_self_comparison_1(self):
        self.assertEqualNice(
            [[0, 0, 0, 0, 0, 0, 0], 
             [0, 1, 0, 0, 0, 1, 0], 
             [0, 0, 1, 0, 0, 0, 0], 
             [0, 0, 0, 1, 0, 0, 0], 
             [0, 0, 0, 0, 1, 0, 0], 
             [0, 1, 0, 0, 0, 1, 0], 
             [0, 0, 0, 0, 0, 0, 0]], project.better_self_comparison, 'AAATAAA', 1)


    def test_better_self_comparison_2(self):
        self.assertEqualNice(
            [[0, 0, 0, 0, 0, 0, 0], 
             [0, 1, 1, 1, 1, 1, 0], 
             [0, 1, 1, 1, 1, 1, 0], 
             [0, 1, 1, 1, 1, 1, 0], 
             [0, 1, 1, 1, 1, 1, 0], 
             [0, 1, 1, 1, 1, 1, 0], 
             [0, 0, 0, 0, 0, 0, 0]], project.better_self_comparison, 'AAAAAAA', 1)


    def test_better_self_comparison_3(self):
        self.assertEqualNice(
            [[1, 1, 1, 1, 1, 1, 1], 
             [1, 1, 1, 1, 1, 1, 1], 
             [1, 1, 1, 1, 1, 1, 1], 
             [1, 1, 1, 1, 1, 1, 1], 
             [1, 1, 1, 1, 1, 1, 1], 
             [1, 1, 1, 1, 1, 1, 1], 
             [1, 1, 1, 1, 1, 1, 1]], project.better_self_comparison, 'AAAAAAA', 0)


if __name__ == '__main__':
    if IN_GRADE_MODE:
       unittest.main(failfast=False, testRunner=AnvProgTestRunner)
    else:
       unittest.main(failfast=True, testRunner=AnvProgTestRunner)

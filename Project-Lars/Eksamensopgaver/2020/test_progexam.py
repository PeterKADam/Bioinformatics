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

GRADE_MODE = os.getenv("GRADE_MODE")

PROJECT_NAME = os.path.splitext(os.path.basename(__file__))[0].replace("test_", "")


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

    ln = lambda f: getattr(tc, f).__code__.co_firstlineno
    lncmp = lambda a, b: ln(a) - ln(b)

    test_suite = unittest.TestSuite()
    for tc in testcases:
        test_suite.addTest(unittest.makeSuite(tc, sortUsing=lncmp))

    return test_suite


def caseFactory():
    from inspect import findsource

    g = globals().copy()
    cases = [
        g[obj]
        for obj in g
        if obj.startswith("Test") and issubclass(g[obj], unittest.TestCase)
    ]
    ordered_cases = sorted(cases, key=lambda f: findsource(f)[1])
    return ordered_cases


def function_not_defined(module, func_name):
    return not (hasattr(module, func_name) and callable(getattr(module, func_name)))


def indent(text, indent=4):
    return "\n".join([(indent * " ") + line for line in text.splitlines()])


def skip_initial_nonlocal(tb):
    if tb is None:
        return tb
    if tb.tb_frame.f_code.co_filename.startswith("test_"):
        return skip_initial_nonlocal(tb.tb_next)
    if "unittest" in tb.tb_frame.f_code.co_filename:
        return skip_initial_nonlocal(tb.tb_next)

    return tb


######################################################

from copy import deepcopy


class NonStandardElementError(Exception):
    def __init___(self, dErrArguments):
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)


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
    separator = "=" * 70

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = False
        self.dots = True
        self.descriptions = descriptions

        self.skipped_functions = list()

        if GRADE_MODE:
            report_file = os.path.splitext(os.path.basename(__file__))[0] + ".csv"
            self.file = open(report_file, "w")

        # match = re.search(r'assignment_(au\d+)_attempt', os.path.basename(os.getcwd()))
        # if match:
        #     self.student_id = match.group(1)
        # else:
        #     self.student_id = 'NA'

        blackboard_match = re.search(
            r"assignment_(au\d+)_attempt", os.path.basename(os.getcwd())
        )
        digitalexam_match = re.search(
            r"([^_]+)_\d+_\d+_.+" + PROJECT_NAME, os.path.basename(os.getcwd())
        )

        if blackboard_match:
            self.student_id = blackboard_match.group(1)
        elif digitalexam_match:
            self.student_id = digitalexam_match.group(1)
        else:
            self.student_id = "NA"

    def addSuccess(self, test):
        super().addSuccess(test)

        if GRADE_MODE:
            self.file.write(
                "{},{},{},{}\n".format(
                    self.student_id, test.__class__.__name__, test._testMethodName, "ok"
                )
            )
            self.file.flush()

    def addError(self, test, err):
        super().addError(test, err)
        errcls, errobj, tb = err
        new_tb = skip_initial_nonlocal(tb)

        if GRADE_MODE:
            self.file.write(
                "{},{},{},{}\n".format(
                    self.student_id,
                    test.__class__.__name__,
                    test._testMethodName,
                    "error",
                )
            )
            self.file.flush()

        # self.stream.writeln(
        #     'ERROR DURING TEST CASE: {}'.format(test._testMethodName))
        self.stream.writeln(
            "YOUR CODE FAILED WHILE RUNNING A TEST ({})".format(test._testMethodName)
        )
        self.stream.writeln()
        self.stream.writeln(
            "It means that your function could not be run the way specified in the assignment."
        )
        self.stream.writeln()
        self.stream.writeln("MESSAGE:")
        self.stream.writeln(indent("{}".format(errobj)))
        self.stream.writeln()
        self.stream.writeln("DETAILED:")
        self.stream.writeln(
            indent("Below is a detailed description of where the error occurred")
        )
        self.stream.writeln(
            indent("and what code was run before the error occurred. It is often")
        )
        self.stream.writeln(
            indent("most useful to read this description from the bottom and up.")
        )
        self.stream.writeln()

        # self.stream.writeln(
        #     indent('\n'.join(traceback.format_tb(new_tb))))
        self.stream.writeln(indent("...Skipped frames not relevant to your code..."))
        self.stream.writeln()
        self.stream.writeln(
            indent("".join(traceback.format_exception(errcls, errobj, new_tb)))
        )

        self.stream.writeln()
        self.stream.writeln(self.separator)
        self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        _, errobj, tb = err

        if GRADE_MODE:
            self.file.write(
                "{},{},{},{}\n".format(
                    self.student_id,
                    test.__class__.__name__,
                    test._testMethodName,
                    "failed",
                )
            )
            self.file.flush()

        self.stream.writeln("FAILED TEST CASE: {}".format(test._testMethodName))
        self.stream.writeln()
        self.stream.writeln("MESSAGE:")
        self.stream.writeln(indent(str(errobj)))
        self.stream.writeln()

        if isinstance(errobj, AssertEqualAssertionError):
            self.stream.writeln("EXPECTED:")
            self.stream.writeln(indent(repr(errobj.expected)))
            self.stream.writeln()
            self.stream.writeln("ACTUAL:")
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
            self.file.write(
                "{},{},{},{}\n".format(
                    self.student_id,
                    test.__class__.__name__,
                    test._testMethodName,
                    "skipped",
                )
            )
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
            self.stream.writeln("*" * 57)
            self.stream.writeln("ATTENTION! The following functions are not defined:")
            self.stream.writeln("")
            self.stream.writeln(
                "\n".join("\t{}".format(x) for x in self.skipped_functions)
            )
            self.stream.writeln()
            self.stream.writeln(
                "These functions are either not correctly named (spelled)"
            )
            self.stream.writeln("or not defined at all. They will be marked as FAILED.")
            self.stream.writeln("Check your spelling if this is not what you intend.")
            self.stream.writeln("*" * 57)
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
        args_str = ", ".join(map(repr, self.args))
        if self.kwargs:
            kwargs_str = ", ".join(
                "{}={!r}".format(k, w) for k, w in self.kwargs.items()
            )
            args_str += ", " + kwargs_str
        return assertion_msg.format(
            func=self.func.__name__,
            args=args_str,
            actual=repr(self.actual),
            expected=repr(self.expected),
        )


class AnvProgTestCase(unittest.TestCase):
    def assertFunctionDefined(self, module, name):
        self.assertTrue(hasattr(module, name), msg="'{}' is not defined".format(name))
        self.assertTrue(
            callable(getattr(module, name)), msg="'{}' is not a function".format(name)
        )

    def assertFunctionPosParams(self, func, expected):
        signature = str(inspect.signature(func))
        self.assertTrue(
            expected == signature,
            msg="Wrong names of function parameters\n\n"
            "Correct function definition:\n\n"
            "{}\n\n"
            "Got:\n\n"
            "{}".format(func.__name__ + expected, func.__name__ + signature),
        )

    def assertEqualNice(self, expected, func, *args, **kwargs):
        actual = func(*args, **kwargs)

        if (
            isinstance(expected, dict)
            or isinstance(actual, dict)
            or isinstance(expected, list)
            or isinstance(actual, list)
        ):
            if not compare_datastruct_nice(expected, actual):
                raise AssertEqualNiceAssertionError(
                    actual, expected, func, args, kwargs
                )

        elif isinstance(expected, float) or isinstance(actual, float):
            if abs(expected - actual) > 1e-4:
                raise AssertEqualNiceAssertionError(
                    actual, expected, func, args, kwargs
                )
        elif actual != expected:
            raise AssertEqualNiceAssertionError(actual, expected, func, args, kwargs)

    def assertEqual(self, first, second, msg=None):
        # Suppress diffs for strings.
        if msg is None and isinstance(first, str) and isinstance(second, str):
            msg = "Got '{}' but expected '{}'".format(first, second)

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
            msg = "{} is not true".format(expr)
        if not expr:
            raise AssertionError(msg)

    def assertFalse(self, expr, msg=None):
        # Override super().assertFalse() to suppress the default 'X is not
        # false' output when msg is not None.
        if msg is None:
            msg = "{} is not false".format(expr)
        if expr:
            raise AssertionError(msg)


###############################################################################
#                                                                             #
#                                 TESTS HERE                                  #
#                                                                             #
###############################################################################


@unittest.skipIf(
    function_not_defined(project, "nr_rows_in_matrix"), "nr_rows_in_matrix"
)
class Test_nr_rows_in_matrix(AnvProgTestCase):
    def test_nr_rows_in_matrix_1(self):
        self.assertEqualNice(2, project.nr_rows_in_matrix, [[1, 2], [1, 2]])

    def test_nr_rows_in_matrix_2(self):
        self.assertEqualNice(
            4, project.nr_rows_in_matrix, [[1, 2], [1, 2], [1, 2], [1, 2]]
        )

    def test_nr_rows_in_matrix_3(self):
        self.assertEqualNice(1, project.nr_rows_in_matrix, [[1, 2, 1, 2]])


@unittest.skipIf(function_not_defined(project, "count_stuff"), "count_stuff")
class Test_count_stuff(AnvProgTestCase):
    def test_count_stuff_1(self):
        self.assertEqualNice(
            {"A": 1, "T": 3, "G": 1, "C": 1}, project.count_stuff, "ATGCTT"
        )

    def test_count_stuff_2(self):
        self.assertEqualNice(
            {1: 1, 7: 3, 2: 1, 3: 1}, project.count_stuff, [1, 7, 2, 7, 3, 7]
        )

    def test_count_stuff_3(self):
        self.assertEqualNice({"a": 3, "b": 1, "n": 2}, project.count_stuff, "banana")


@unittest.skipIf(
    function_not_defined(project, "invert_dictionary"), "invert_dictionary"
)
class Test_invert_dictionary(AnvProgTestCase):
    def test_invert_dictionary_1(self):
        self.assertEqualNice(
            {3: "a", 1: "b", 2: "n"},
            project.invert_dictionary,
            {"a": 3, "b": 1, "n": 2},
        )

    def test_invert_dictionary_2(self):
        self.assertEqualNice(
            {"A": "a", "B": "b", "N": "n"},
            project.invert_dictionary,
            {"a": "A", "b": "B", "n": "N"},
        )

    def test_invert_dictionary_3(self):
        self.assertEqualNice(
            {"P": "Preben", "M": "Mogens"},
            project.invert_dictionary,
            {"Preben": "P", "Mogens": "M"},
        )


@unittest.skipIf(
    function_not_defined(project, "count_upper_case_bases"), "count_upper_case_bases"
)
class Test_count_upper_case_bases(AnvProgTestCase):
    def test_count_upper_case_bases_1(self):
        self.assertEqualNice(4, project.count_upper_case_bases, "agtcATGCatgc")

    def test_count_upper_case_bases_2(self):
        self.assertEqualNice(4, project.count_upper_case_bases, "agATgcGCgc")

    def test_count_upper_case_bases_3(self):
        self.assertEqualNice(2, project.count_upper_case_bases, "ATgcgcgc")

    def test_count_upper_case_bases_4(self):
        self.assertEqualNice(0, project.count_upper_case_bases, "atgcgcgc")


@unittest.skipIf(
    function_not_defined(project, "every_second_base"), "every_second_base"
)
class Test_every_second_base(AnvProgTestCase):
    def test_every_second_base_1(self):
        self.assertEqualNice(
            ["A", "A", "A", "A"], project.every_second_base, "ATATATAT"
        )

    def test_every_second_base_2(self):
        self.assertEqualNice(
            ["T", "T", "T", "T"], project.every_second_base, "TATATATA"
        )

    def test_every_second_base_3(self):
        self.assertEqualNice(["G"], project.every_second_base, "GC")

    def test_every_second_base_4(self):
        self.assertEqualNice(["G"], project.every_second_base, "G")


@unittest.skipIf(
    function_not_defined(project, "splice_upper_case"), "splice_upper_case"
)
class Test_splice_upper_case(AnvProgTestCase):
    def test_splice_upper_case_1(self):
        self.assertEqualNice("ATGC", project.splice_upper_case, "agATgcGCgc")

    def test_splice_upper_case_2(self):
        self.assertEqualNice("ATGC", project.splice_upper_case, "ATGC")

    def test_splice_upper_case_3(self):
        self.assertEqualNice("", project.splice_upper_case, "atgc")

    def test_splice_upper_case_4(self):
        self.assertEqualNice("ATGC", project.splice_upper_case, "AaTtGgCc")


@unittest.skipIf(function_not_defined(project, "kmer_locations"), "kmer_locations")
class Test_kmer_locations(AnvProgTestCase):
    def test_kmer_locations_1(self):
        self.assertEqualNice([3, 9], project.kmer_locations, "TCT", "AAATCTAAATCT")

    def test_kmer_locations_2(self):
        self.assertEqualNice([], project.kmer_locations, "TCT", "AAAAAAAAAAAA")

    def test_kmer_locations_3(self):
        self.assertEqualNice([3, 5], project.kmer_locations, "TCT", "AAATCTCTAAAA")

    def test_kmer_locations_4(self):
        self.assertEqualNice([3, 5, 9], project.kmer_locations, "TCT", "AAATCTCTATCT")

    def test_kmer_locations_5(self):
        self.assertEqualNice([4, 10], project.kmer_locations, "CT", "AAATCTAAATCT")


@unittest.skipIf(function_not_defined(project, "kmers_overlap"), "kmers_overlap")
class Test_kmers_overlap(AnvProgTestCase):
    def test_kmers_overlap_1(self):
        self.assertEqualNice(
            True, project.kmers_overlap, "TTAA", "AATT", "CCCCTTAATTCCCC"
        )

    def test_kmers_overlap_2(self):
        self.assertEqualNice(
            False, project.kmers_overlap, "TTAA", "AATT", "CCTTAACCAATTCC"
        )

    def test_kmers_overlap_3(self):
        self.assertEqualNice(
            False, project.kmers_overlap, "TTAA", "AATT", "CCTTAACCCCTTCC"
        )

    def test_kmers_overlap_4(self):
        self.assertEqualNice(
            False, project.kmers_overlap, "TTAA", "AATT", "CCCCCCCCCCCCCC"
        )

    def test_kmers_overlap_5(self):
        self.assertEqualNice(
            True, project.kmers_overlap, "CCCC", "CCCC", "CCCCCCCCCCCCCC"
        )


@unittest.skipIf(function_not_defined(project, "unique_kmers"), "unique_kmers")
class Test_unique_kmers(AnvProgTestCase):
    def test_unique_kmers_1(self):
        self.assertEqualNice(["ATA", "TAT"], project.unique_kmers, "ATATATAT", 3)

    def test_unique_kmers_2(self):
        self.assertEqualNice(["AAA"], project.unique_kmers, "AAAAAAAA", 3)

    def test_unique_kmers_3(self):
        self.assertEqualNice(
            ["AAA", "AAT", "ATT", "TTT"], project.unique_kmers, "AAAATTTT", 3
        )

    def test_unique_kmers_5(self):
        self.assertEqualNice(["A", "T"], project.unique_kmers, "AAAATTTT", 1)

    def test_unique_kmers_6(self):
        self.assertEqualNice(
            ["AAAA", "AAAT", "AATT", "ATTT", "TTTT"],
            project.unique_kmers,
            "AAAATTTT",
            4,
        )


@unittest.skipIf(
    function_not_defined(project, "nr_unique_kmers_shared"), "nr_unique_kmers_shared"
)
class Test_nr_kmers_shared(AnvProgTestCase):
    def test_nr_unique_kmers_shared_1(self):
        self.assertEqualNice(1, project.nr_unique_kmers_shared, "AAAAT", "ATTTT", 2)

    def test_nr_unique_kmers_shared_2(self):
        self.assertEqualNice(2, project.nr_unique_kmers_shared, "GAAAAT", "GATTTT", 2)

    def test_nr_unique_kmers_shared_3(self):
        self.assertEqualNice(0, project.nr_unique_kmers_shared, "GAAAAT", "TTTTTT", 2)

    def test_nr_unique_kmers_shared_4(self):
        self.assertEqualNice(3, project.nr_unique_kmers_shared, "GAAAAT", "GATTTT", 1)

    def test_nr_unique_kmers_shared_5(self):
        self.assertEqualNice(0, project.nr_unique_kmers_shared, "GATTTT", "AAAAAA", 2)


@unittest.skipIf(
    function_not_defined(project, "kmer_sharing_matrix"), "kmer_sharing_matrix"
)
class Test_kmer_sharing_matrix(AnvProgTestCase):
    def test_kmer_sharing_matrix_1(self):
        self.assertEqualNice(
            [[3, 2], [2, 3]], project.kmer_sharing_matrix, ["GAAAAT", "GATTTT"], 2
        )

    def test_kmer_sharing_matrix_2(self):
        self.assertEqualNice(
            [[1, 0], [0, 1]], project.kmer_sharing_matrix, ["AAAAAA", "TTTTTT"], 4
        )

    def test_kmer_sharing_matrix_3(self):
        self.assertEqualNice(
            [[3, 2, 1], [2, 3, 0], [1, 0, 1]],
            project.kmer_sharing_matrix,
            ["GAAAAT", "GATTTT", "AAAAAA"],
            2,
        )

    def test_kmer_sharing_matrix_4(self):
        self.assertEqualNice(
            [[3, 3, 1], [3, 3, 1], [1, 1, 1]],
            project.kmer_sharing_matrix,
            ["GAAAAT", "GATTTT", "AAAAAA"],
            1,
        )

    def test_kmer_sharing_matrix_5(self):
        self.assertEqualNice(
            [[3, 0, 1], [0, 3, 0], [1, 0, 1]],
            project.kmer_sharing_matrix,
            ["GAAAAT", "GATTTT", "AAAAAA"],
            3,
        )


if __name__ == "__main__":
    # if GRADE_MODE:
    #    unittest.main(failfast=False, testRunner=AnvProgTestRunner)
    # else:
    #    unittest.main(failfast=True, testRunner=AnvProgTestRunner)
    cases = suiteFactory(*caseFactory())
    if GRADE_MODE:
        failfast = False
    else:
        failfast = True
    runner = AnvProgTestRunner(failfast=failfast)
    runner.run(cases)


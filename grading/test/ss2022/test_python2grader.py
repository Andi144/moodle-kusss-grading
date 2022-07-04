import pandas as pd

from graders.ss2022.python2grader import Python2Grader
from test.abstractgradertest import AbstractGraderTest

COLUMNS = [f"Assignment: Exercise {i + 1} (Real)" for i in range(6)] + \
          ["Quiz: Exam (Real)", "Quiz: Retry Exam (Real)", "Quiz: Retry Exam 2 (Real)"] + \
          ["expected_grade"]

FULL_POINTS_A1 = [5, 15, 15]
# ignore bonus points of assignment 2 (ex5: 35+10, ex6: 10)
FULL_POINTS_A2 = [20, 35, 0]
FULL_POINTS_A = FULL_POINTS_A1 + FULL_POINTS_A2
FULL_POINTS_E = [10, 10, 10]


class Python2GraderTest(AbstractGraderTest):
    
    def get_grader_class(self) -> type:
        return Python2Grader
    
    #
    # tests based on exams
    #

    # noinspection PyTypeChecker
    def test_create_grading_file_no_exam(self):
        # assignments but no exam = 5
        self.assert_equal_grades(pd.DataFrame([
            FULL_POINTS_A + ["-", "-", "-"] + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_exam_threshold_negative(self):
        self.assert_equal_grades(pd.DataFrame([
            # exam 1
            FULL_POINTS_A + [0, "-", "-"] + [5],
            FULL_POINTS_A + [4.99, "-", "-"] + [5],
            # exam 2
            FULL_POINTS_A + ["-", 0, "-"] + [5],
            FULL_POINTS_A + ["-", 4.99, "-"] + [5],
            # exam 3
            FULL_POINTS_A + ["-", "-", 0] + [5],
            FULL_POINTS_A + ["-", "-", 4.99] + [5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_exam_threshold_positive(self):
        # full assignment points means 90/100, so if the exam is positive, it's a "very good" (1)
        points = pd.DataFrame([
            # exam 1
            FULL_POINTS_A + [5, "-", "-", 1],
            # exam 2
            FULL_POINTS_A + ["-", 5, "-", 1],
            # exam 3
            FULL_POINTS_A + ["-", "-", 5, 1],
        ], columns=COLUMNS)
        self.assert_equal_grades(points)
    
    def test_create_grading_file_multiple_exams(self):
        # latest exam should take precedence
        self.assert_equal_grades(pd.DataFrame([
            FULL_POINTS_A + [10, 0, "-"] + [5],
            FULL_POINTS_A + [0, 10, "-"] + [1],
            FULL_POINTS_A + [10, "-", 0] + [5],
            FULL_POINTS_A + [0, "-", 10] + [1],
            FULL_POINTS_A + ["-", 10, 0] + [5],
            FULL_POINTS_A + ["-", 0, 10] + [1],
            FULL_POINTS_A + [10, 0, 0] + [5],
            FULL_POINTS_A + [0, 10, 0] + [5],
            FULL_POINTS_A + [10, 10, 0] + [5],
            FULL_POINTS_A + [10, 0, 10] + [1],
            FULL_POINTS_A + [0, 10, 10] + [1],
            FULL_POINTS_A + [10, 10, 10] + [1],
        ], columns=COLUMNS))
    
    #
    # tests based on assignments
    #
    
    # noinspection PyTypeChecker
    def test_create_grading_file_individual_assignments_threshold_negative(self):
        # * 0.24 = 24% = fail because of 25% threshold
        self.assert_equal_grades(pd.DataFrame([
            # a1
            [0] * len(FULL_POINTS_A1) + FULL_POINTS_A2 + FULL_POINTS_E + [5],
            ["-"] * len(FULL_POINTS_A1) + FULL_POINTS_A2 + FULL_POINTS_E + [5],
            [sum(FULL_POINTS_A1) * 0.24 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) + FULL_POINTS_A2 +
            FULL_POINTS_E + [5],
            # a2
            FULL_POINTS_A1 + [0] * len(FULL_POINTS_A2) + FULL_POINTS_E + [5],
            FULL_POINTS_A1 + ["-"] * len(FULL_POINTS_A2) + FULL_POINTS_E + [5],
            FULL_POINTS_A1 + [sum(FULL_POINTS_A2) * 0.24 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_E + [5],
            # a1 + a2
            [0] * len(FULL_POINTS_A) + FULL_POINTS_E + [5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_combined_assignments_threshold_negative(self):
        self.assert_equal_grades(pd.DataFrame([
            # all assignments with 49% each
            [sum(FULL_POINTS_A1) * 0.49 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.49 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_E + [5],
            # mixed percentages with >= 25% (=passed) ---> combined < 50%
            [sum(FULL_POINTS_A1) * 0.25 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.25 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_E + [5],
            [sum(FULL_POINTS_A1) * 0.75 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.3 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_E + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_assignments_total_positive(self):
        self.assert_equal_grades(pd.DataFrame([
            # all assignments with 50% each
            [sum(FULL_POINTS_A1) * 0.5 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.5 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_E + [4],
            # first assignment with full points, second with 40% (=passed) ---> combined > 50%
            FULL_POINTS_A1 +
            [sum(FULL_POINTS_A2) * 0.4 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_E + [3],
            # second assignment with full points, first with 40% (=passed) ---> combined > 50%
            [sum(FULL_POINTS_A1) * 0.4 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            FULL_POINTS_A2 + FULL_POINTS_E + [2],
            # full points
            FULL_POINTS_A + FULL_POINTS_E + [1],
        ], columns=COLUMNS))

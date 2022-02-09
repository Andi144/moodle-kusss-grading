import pandas as pd

from graders.ws2021.python1grader import Python1Grader
from test.ws2021.abstractgradertest import AbstractGraderTest

COLUMNS = [f"Assignment: Exercise {i + 1} (Real)" for i in range(21)] + \
          ["Quiz: Exam 1 (Real)", "Quiz: Exam 2 (Real)", "Quiz: Retry Exam (Real)"] + \
          ["expected_grade"]

FULL_POINTS_A1 = [25, 25, 50, 50]
# ignore bonus points of assignment 2 (last 0 -> 50)
FULL_POINTS_A2 = [20, 20, 20, 20, 20, 20, 55, 25, 50, 50, 0]
# ignore bonus points of assignment 3 (last two 0 -> 20, 30)
FULL_POINTS_A3 = [110, 110, 80, 50, 0, 0]
FULL_POINTS_A = FULL_POINTS_A1 + FULL_POINTS_A2 + FULL_POINTS_A3
FULL_POINTS_Q = [10, 10, "-"]


class Python1GraderTest(AbstractGraderTest):
    
    def get_grader_class(self) -> type:
        return Python1Grader
    
    #
    # tests based on quizzes
    #
    
    def test_create_grading_file_q1q2_threshold_negative(self):
        self.assert_equal_grades(pd.DataFrame([
            # q1
            FULL_POINTS_A + [0, 10, "-"] + [5],
            FULL_POINTS_A + [3.9, 10, "-"] + [5],
            FULL_POINTS_A + ["-", 10, "-"] + [5],
            # q2
            FULL_POINTS_A + [10, 0, "-"] + [5],
            FULL_POINTS_A + [10, 3.9, "-"] + [5],
            FULL_POINTS_A + [10, "-", "-"] + [5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_q1q2_total_negative(self):
        self.assert_equal_grades(pd.DataFrame([
            FULL_POINTS_A + [4, 5.9, "-"] + [5],
            FULL_POINTS_A + [4.9, 5, "-"] + [5],
            FULL_POINTS_A + [5.9, 4, "-"] + [5],
            FULL_POINTS_A + [5, 4.9, "-"] + [5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_q1q2_total_positive(self):
        self.assert_equal_grades(pd.DataFrame([
            FULL_POINTS_A + [4, 6, "-"] + [1],
            FULL_POINTS_A + [6, 4, "-"] + [1],
            FULL_POINTS_A + [5, 5, "-"] + [1],
            FULL_POINTS_A + [10, 10, "-"] + [1],
        ], columns=COLUMNS))
    
    def test_create_grading_file_qretry_negative(self):
        # noinspection PyTypeChecker
        self.assert_equal_grades(pd.DataFrame([
            # should be independent of q1 + q2
            FULL_POINTS_A + ["-", "-", 9.9] + [5],
            FULL_POINTS_A + ["-", 10, 9.9] + [5],
            FULL_POINTS_A + [10, "-", 9.9] + [5],
            FULL_POINTS_A + [3.9, 10, 9.9] + [5],
            FULL_POINTS_A + [10, 3.9, 9.9] + [5],
            FULL_POINTS_A + [10, 10, 9.9] + [5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_qretry_positive(self):
        self.assert_equal_grades(pd.DataFrame([
            # should be independent of q1 + q2
            FULL_POINTS_A + ["-", "-", 10] + [1],
            FULL_POINTS_A + ["-", 3.9, 10] + [1],
            FULL_POINTS_A + ["-", 10, 10] + [1],
            FULL_POINTS_A + [3.9, "-", 10] + [1],
            FULL_POINTS_A + [10, "-", 10] + [1],
            FULL_POINTS_A + [3.9, 10, 10] + [1],
            FULL_POINTS_A + [10, 3.9, 10] + [1],
            FULL_POINTS_A + [10, 10, 10] + [1],
            FULL_POINTS_A + ["-", "-", 20] + [1],
            FULL_POINTS_A + ["-", 10, 20] + [1],
            FULL_POINTS_A + [10, "-", 20] + [1],
            FULL_POINTS_A + [3.9, 10, 20] + [1],
            FULL_POINTS_A + [10, 3.9, 20] + [1],
            FULL_POINTS_A + [10, 10, 20] + [1],
        ], columns=COLUMNS))
    
    #
    # tests based on assignments
    #
    
    # noinspection PyTypeChecker
    def test_create_grading_file_individual_assignments_threshold_negative(self):
        # * 0.24 = 24% = fail because of 25% threshold
        self.assert_equal_grades(pd.DataFrame([
            # a1
            [0] * len(FULL_POINTS_A1) + FULL_POINTS_A2 + FULL_POINTS_A3 + FULL_POINTS_Q + [5],
            ["-"] * len(FULL_POINTS_A1) + FULL_POINTS_A2 + FULL_POINTS_A3 + FULL_POINTS_Q + [5],
            [sum(FULL_POINTS_A1) * 0.24 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            FULL_POINTS_A2 + FULL_POINTS_A3 + FULL_POINTS_Q + [5],
            # a2
            FULL_POINTS_A1 + [0] * len(FULL_POINTS_A2) + FULL_POINTS_A3 + FULL_POINTS_Q + [5],
            FULL_POINTS_A1 + ["-"] * len(FULL_POINTS_A2) + FULL_POINTS_A3 + FULL_POINTS_Q + [5],
            FULL_POINTS_A1 + [sum(FULL_POINTS_A2) * 0.24 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_A3 + FULL_POINTS_Q + [5],
            # a3
            FULL_POINTS_A1 + FULL_POINTS_A2 + [0] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [5],
            FULL_POINTS_A1 + FULL_POINTS_A2 + ["-"] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [5],
            FULL_POINTS_A1 + FULL_POINTS_A2 +
            [sum(FULL_POINTS_A3) * 0.24 / len(FULL_POINTS_A3)] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [5],
            # a1 + a2 + a3
            [0] * len(FULL_POINTS_A) + FULL_POINTS_Q + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_combined_assignments_threshold_negative(self):
        self.assert_equal_grades(pd.DataFrame([
            # all assignments with 49% each
            [sum(FULL_POINTS_A1) * 0.49 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.49 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            [sum(FULL_POINTS_A3) * 0.49 / len(FULL_POINTS_A3)] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [5],
            # first assignment with full points, other two with 25% (=passed) ---> combined < 50%
            FULL_POINTS_A1 +
            [sum(FULL_POINTS_A2) * 0.25 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            [sum(FULL_POINTS_A3) * 0.25 / len(FULL_POINTS_A3)] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [5],
            # mixed percentages with >= 25% (=passed) ---> combined < 50%
            [sum(FULL_POINTS_A1) * 0.75 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.3 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            [sum(FULL_POINTS_A3) * 0.55 / len(FULL_POINTS_A3)] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_assignments_total_positive(self):
        self.assert_equal_grades(pd.DataFrame([
            # all assignments with 50% each
            [sum(FULL_POINTS_A1) * 0.5 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.5 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            [sum(FULL_POINTS_A3) * 0.5 / len(FULL_POINTS_A3)] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [4],
            # first assignment with full points, other two with 40% (=passed) ---> combined > 50%
            FULL_POINTS_A1 +
            [sum(FULL_POINTS_A2) * 0.4 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            [sum(FULL_POINTS_A3) * 0.4 / len(FULL_POINTS_A3)] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [4],
            # second assignment with full points, other two with 40% (=passed) ---> combined > 50%
            [sum(FULL_POINTS_A1) * 0.4 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            FULL_POINTS_A2 +
            [sum(FULL_POINTS_A3) * 0.4 / len(FULL_POINTS_A3)] * len(FULL_POINTS_A3) + FULL_POINTS_Q + [3],
            # third assignment with full points, other two with 40% (=passed) ---> combined > 50%
            [sum(FULL_POINTS_A1) * 0.4 / len(FULL_POINTS_A1)] * len(FULL_POINTS_A1) +
            [sum(FULL_POINTS_A2) * 0.4 / len(FULL_POINTS_A2)] * len(FULL_POINTS_A2) +
            FULL_POINTS_A3 + FULL_POINTS_Q + [3],
            # full points
            FULL_POINTS_A + FULL_POINTS_Q + [1],
        ], columns=COLUMNS))

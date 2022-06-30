import pandas as pd

from graders.ws2021.handson1lecturegrader import HandsOn1LectureGrader
from test.abstractgradertest import AbstractGraderTest

QRETRY_COL = "Quiz: Retry Exam (Real)"
COLUMNS = ["Quiz: Exam 1 (Real)", "Quiz: Exam 2 (Real)", QRETRY_COL, "expected_grade"]


class HandsOn1LectureGraderTest(AbstractGraderTest):
    
    def get_grader_class(self) -> type:
        return HandsOn1LectureGrader
    
    def test_create_grading_file_q1q2_threshold_negative(self):
        points = pd.DataFrame([
            # q1
            [0, 100, "-", 5],
            [39, 100, "-", 5],
            ["-", 100, "-", 5],
            # q2
            [100, 0, "-", 5],
            [100, 39, "-", 5],
            [100, "-", "-", 5],
        ], columns=COLUMNS)
        self.assert_equal_grades(points)
        self.assert_equal_grades(points.drop(columns=QRETRY_COL))
    
    def test_create_grading_file_q1q2_total_negative(self):
        points = pd.DataFrame([
            [40, 59, "-", 5],
            [49, 50, "-", 5],
            [59, 40, "-", 5],
            [50, 49, "-", 5],
        ], columns=COLUMNS)
        self.assert_equal_grades(points)
        self.assert_equal_grades(points.drop(columns=QRETRY_COL))
    
    def test_create_grading_file_q1q2_total_positive(self):
        points = pd.DataFrame([
            [40, 60, "-", 4],
            [60, 40, "-", 4],
            [50, 50, "-", 4],
            [100, 100, "-", 1],
        ], columns=COLUMNS)
        self.assert_equal_grades(points)
        self.assert_equal_grades(points.drop(columns=QRETRY_COL))
    
    def test_create_grading_file_qretry_negative(self):
        self.assert_equal_grades(pd.DataFrame([
            # should be independent of q1 + q2
            ["-", "-", 99, 5],
            ["-", 100, 99, 5],
            [100, "-", 99, 5],
            [39, 100, 99, 5],
            [100, 39, 99, 5],
            [100, 100, 99, 5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_qretry_positive(self):
        self.assert_equal_grades(pd.DataFrame([
            # should be independent of q1 + q2
            ["-", "-", 100, 4],
            ["-", 39, 100, 4],
            ["-", 100, 100, 4],
            [39, "-", 100, 4],
            [100, "-", 100, 4],
            [39, 100, 100, 4],
            [100, 39, 100, 4],
            [100, 100, 100, 4],
            ["-", "-", 200, 1],
            ["-", 100, 200, 1],
            [100, "-", 200, 1],
            [39, 100, 200, 1],
            [100, 39, 200, 1],
            [100, 100, 200, 1],
        ], columns=COLUMNS))

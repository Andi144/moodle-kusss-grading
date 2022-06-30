import pandas as pd

from graders.ss2022.handson2lecturegrader import HandsOn2LectureGrader
from test.abstractgradertest import AbstractGraderTest

COLUMNS = ["Quiz: Exam (Real)", "Quiz: Retry Exam (Real)", "Quiz: Retry Exam 2 (Real)", "expected_grade"]


class HandsOn2LectureGraderTest(AbstractGraderTest):
    
    def get_grader_class(self) -> type:
        return HandsOn2LectureGrader
    
    def test_create_grading_file_threshold_negative(self):
        # a point difference < 0.1 to the positive threshold is rounded up
        points = pd.DataFrame([
            # exam 1 (considering the +0.5 bonus points)
            [0, "-", "-", 5],  # actual: 0.5 points
            [19, "-", "-", 5],  # actual: 19.5 points
            [19.4, "-", "-", 5],  # actual: 19.9 points
            # exam 2
            ["-", 0, "-", 5],
            ["-", 19, "-", 5],
            ["-", 19.9, "-", 5],
            # exam 3
            ["-", "-", 0, 5],
            ["-", "-", 19, 5],
            ["-", "-", 19.9, 5],
        ], columns=COLUMNS)
        self.assert_equal_grades(points)
    
    def test_create_grading_file_threshold_positive(self):
        # a point difference < 0.1 to the positive threshold is rounded up
        points = pd.DataFrame([
            # exam 1 (considering the +0.5 bonus points)
            [19.4001, "-", "-", 4],  # actual: 19.91 points --> rounded to 20 points
            [19.5, "-", "-", 4],  # actual: 20 points
            # exam 2
            ["-", 19.9001, "-", 4],  # rounded to 20 points
            ["-", 20, "-", 4],
            # exam 3
            ["-", "-", 19.9001, 4],  # rounded to 20 points
            ["-", "-", 20, 4],
        ], columns=COLUMNS)
        self.assert_equal_grades(points)
    
    def test_create_grading_file_multiple_exams(self):
        # latest exam should take precedence
        points = pd.DataFrame([
            [40, 0, "-", 5],
            [0, 40, "-", 1],
            [40, "-", 0, 5],
            [0, "-", 40, 1],
            ["-", 40, 0, 5],
            ["-", 0, 40, 1],
            [40, 0, 0, 5],
            [0, 40, 0, 5],
            [40, 40, 0, 5],
            [40, 0, 40, 1],
            [0, 40, 40, 1],
            [40, 40, 40, 1],
        ], columns=COLUMNS)
        self.assert_equal_grades(points)

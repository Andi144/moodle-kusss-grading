import pandas as pd

from graders.ws2021.handson1exercisegrader import HandsOn1ExerciseGrader
from test.abstractgradertest import AbstractGraderTest

COLUMNS = [f"Assignment: Assignment {i + 1} (Real)" for i in range(7)] + ["expected_grade"]


class HandsOn1ExerciseGraderTest(AbstractGraderTest):
    
    def get_grader_class(self) -> type:
        return HandsOn1ExerciseGrader
    
    def test_create_grading_file_at_least_two_missing_assignments(self):
        self.assert_equal_grades(pd.DataFrame([
            # either no missing
            [100, 100, 100, 100, 100, "-", "-", 5],
            [100, 100, 100, 100, "-", "-", "-", 5],
            [100, 100, 100, "-", "-", "-", "-", 5],
            [100, 100, "-", "-", "-", "-", "-", 5],
            [100, "-", "-", "-", "-", "-", "-", 5],
            [100, "-", "-", "-", "-", "-", "-", 5],
            # or graded with 0 points
            [100, 100, 100, 100, 100, 0, 0, 5],
            [100, 100, 100, 100, 0, 0, 0, 5],
            [100, 100, 100, 0, 0, 0, 0, 5],
            [100, 100, 0, 0, 0, 0, 0, 5],
            [100, 0, 0, 0, 0, 0, 0, 5],
            [100, 0, 0, 0, 0, 0, 0, 5],
            # mixed and randomized
            [0, 100, 0, 0, 100, "-", 100, 5],
            ["-", 100, 100, 100, 0, 100, 100, 5],
            [100, 0, "-", "-", 100, 0, 100, 5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_too_few_points(self):
        self.assert_equal_grades(pd.DataFrame([
            [50, 50, 50, 50, 50, 50, 49, 5],
            [0, 1, 1, 1, 1, 1, 1, 5],
            [100, 100, 100, 40, 4, 5, 0, 5],
            [24, "-", 86, 23, 97, 12, 10, 5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_positive(self):
        self.assert_equal_grades(pd.DataFrame([
            [50, 50, 50, 50, 50, 50, 50, 4],
            [100, 100, 100, 40, 4, 5, 1, 4],
            [100, 100, 100, 40, 5, 5, 0, 4],
            [100, 100, 100, 100, 100, 100, 100, 1],
            [100, 100, 100, 100, 100, 100, 0, 2],
            ["-", 90, 10, 2, 100, 97, 78, 4],
        ], columns=COLUMNS))

import numpy as np
import pandas as pd

from graders.ss2023.python2exercisegrader import Python2ExerciseGrader
from test.abstractgradertest import AbstractGraderTest

COLUMNS = [f"Assignment: Assignment {i + 1} (Real)" for i in range(6)] + \
          ["Assignment: Assignment 7 (Project) (Real)", "Assignment: Assignment 8 (Bonus) (Real)"] + \
          ["Quiz: Exam (Real)", "Quiz: Retry Exam (Real)", "Quiz: Retry Exam 2 (Real)"] + \
          ["expected_grade"]
FULL_POINTS_A = [100] * 6 + [400, 0]
assert sum(FULL_POINTS_A) == 1000
FULL_POINTS_A_WITH_BONUS = [100] * 6 + [500, 50]
assert sum(FULL_POINTS_A_WITH_BONUS) == 1150
FULL_POINTS_E = [100, "", ""]


class Python2ExerciseGraderTest(AbstractGraderTest):
    
    def get_grader_class(self) -> type:
        return Python2ExerciseGrader
    
    #
    # tests based on exam
    #
    
    # noinspection PyTypeChecker
    def test_create_grading_file_no_exam(self):
        # assignments but no exam = 5
        self.assert_equal_grades(pd.DataFrame([
            FULL_POINTS_A + ["-", "-", "-"] + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_threshold_negative(self):
        self.assert_equal_grades(pd.DataFrame([
            FULL_POINTS_A + [0, "-", "-"] + [5],
            FULL_POINTS_A + [49, "-", "-"] + [5],
            FULL_POINTS_A + [49.9, "-", "-"] + [5],
            # exam 2
            FULL_POINTS_A + ["-", 0, "-"] + [5],
            FULL_POINTS_A + ["-", 49, "-"] + [5],
            FULL_POINTS_A + ["-", 49.9, "-"] + [5],
            # exam 3
            FULL_POINTS_A + ["-", "-", 0] + [5],
            FULL_POINTS_A + ["-", "-", 49] + [5],
            FULL_POINTS_A + ["-", "-", 49.9] + [5],
        ], columns=COLUMNS))
    
    def test_create_grading_file_exam_threshold_positive(self):
        # full assignment points means 1000/1100, so if the exam is positive, it's a "very good" (1)
        # with bonus points, its 1150/1100, so "very good" (1) even more so
        self.assert_equal_grades(pd.DataFrame([
            # exam 1
            FULL_POINTS_A + [50, "-", "-"] + [1],
            FULL_POINTS_A_WITH_BONUS + [50, "-", "-"] + [1],
            # exam 2
            FULL_POINTS_A + ["-", 50, "-"] + [1],
            FULL_POINTS_A_WITH_BONUS + ["-", 50, "-"] + [1],
            # exam 3
            FULL_POINTS_A + ["-", "-", 50] + [1],
            FULL_POINTS_A_WITH_BONUS + ["-", "-", 50] + [1],
        ], columns=COLUMNS))
    
    def test_create_grading_file_multiple_exams(self):
        # latest exam should take precedence
        self.assert_equal_grades(pd.DataFrame([
            FULL_POINTS_A + [100, 0, "-"] + [5],
            FULL_POINTS_A + [0, 100, "-"] + [1],
            FULL_POINTS_A + [100, "-", 0] + [5],
            FULL_POINTS_A + [0, "-", 100] + [1],
            FULL_POINTS_A + ["-", 100, 0] + [5],
            FULL_POINTS_A + ["-", 0, 100] + [1],
            FULL_POINTS_A + [100, 0, 0] + [5],
            FULL_POINTS_A + [0, 100, 0] + [5],
            FULL_POINTS_A + [100, 100, 0] + [5],
            FULL_POINTS_A + [100, 0, 100] + [1],
            FULL_POINTS_A + [0, 100, 100] + [1],
            FULL_POINTS_A + [100, 100, 100] + [1],
        ], columns=COLUMNS))
    
    #
    # tests based on assignments
    #
    
    def test_create_grading_file_individual_assignments_threshold_negative(self):
        # >= 3 means failing (bonus points should not change anything)
        assignments = [[0] * i + FULL_POINTS_A[i:] + FULL_POINTS_E + [5]
                       for i in range(3, len(FULL_POINTS_A) + 1)]
        assignments += [[0] * i + FULL_POINTS_A_WITH_BONUS[i:] + FULL_POINTS_E + [5]
                        for i in range(3, len(FULL_POINTS_A_WITH_BONUS) + 1)]
        self.assert_equal_grades(pd.DataFrame(assignments, columns=COLUMNS))
    
    def test_create_grading_file_combined_assignments_threshold_negative(self):
        # bonus exercise should not change anything but the project bonus can
        self.assert_equal_grades(pd.DataFrame([
            # without bonus: all assignments with 49% each
            (np.array(FULL_POINTS_A) * 0.49).tolist() + FULL_POINTS_E + [5],
            # with bonus (project and bonus exercise): all assignments with 49% each except for the project where we
            # must set the percentage to about 39% to ultimately end up with < 200 points = < 50% of the regular points
            (np.array(FULL_POINTS_A_WITH_BONUS[:6]) * 0.49).tolist() + [FULL_POINTS_A_WITH_BONUS[6] * 0.39] + (np.array(FULL_POINTS_A_WITH_BONUS[7:]) * 0.49).tolist() + FULL_POINTS_E + [5],
            # mixed percentages with >= 25% (=passed) ---> combined < 50% (without and with bonus)
            (np.array(FULL_POINTS_A) * 0.25).tolist() + FULL_POINTS_E + [5],
            (np.array(FULL_POINTS_A_WITH_BONUS) * 0.25).tolist() + FULL_POINTS_E + [5],
            (np.array(FULL_POINTS_A[:4]) * 0.6).tolist() + (np.array(FULL_POINTS_A[4:]) * 0.25).tolist() + FULL_POINTS_E + [5],
            (np.array(FULL_POINTS_A_WITH_BONUS[:4]) * 0.6).tolist() + (np.array(FULL_POINTS_A_WITH_BONUS[4:]) * 0.25).tolist() + FULL_POINTS_E + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_assignments_total_positive(self):
        self.assert_equal_grades(pd.DataFrame([
            # all assignments with 50% each (without and with bonus)
            (np.array(FULL_POINTS_A) * 0.5).tolist() + FULL_POINTS_E + [4],
            (np.array(FULL_POINTS_A_WITH_BONUS) * 0.5).tolist() + FULL_POINTS_E + [4],
            # mixed assignments: first 5 with >= 25% (=passed), rest (1 regular, project, bonus) with 75%
            # ---> combined >= 50% (without and with bonus)
            (np.array(FULL_POINTS_A[:5]) * 0.25).tolist() + (np.array(FULL_POINTS_A[5:]) * 0.75).tolist() + FULL_POINTS_E + [4],
            (np.array(FULL_POINTS_A_WITH_BONUS[:5]) * 0.25).tolist() + (np.array(FULL_POINTS_A_WITH_BONUS[5:]) * 0.75).tolist() + FULL_POINTS_E + [3],
            # two assignments dropped, i.e., 0 points (without and with bonus)
            [0, 0] + FULL_POINTS_A[2:] + FULL_POINTS_E + [2],
            ["-", "-"] + FULL_POINTS_A[2:] + FULL_POINTS_E + [2],
            [0, 0] + FULL_POINTS_A_WITH_BONUS[2:] + FULL_POINTS_E + [1],
            ["-", "-"] + FULL_POINTS_A_WITH_BONUS[2:] + FULL_POINTS_E + [1],
        ], columns=COLUMNS))
    
    def test_create_grading_file_bonus_assignment(self):
        # bonus points should change the grades
        self.assert_equal_grades(pd.DataFrame([
            # 1000 * 0.58 (assignments with 0 bonus) + 100 = 680 -> /1100 ~ 62% -> "4"
            [sum(FULL_POINTS_A) * 0.58 / len(FULL_POINTS_A)] * len(FULL_POINTS_A) + FULL_POINTS_E + [4],
            # 1150 * 0.58 (assignments with 150 bonus) + 100 = 767 -> /1100 ~ 70% -> "3"
            [sum(FULL_POINTS_A_WITH_BONUS) * 0.58 / len(FULL_POINTS_A_WITH_BONUS)] * len(FULL_POINTS_A_WITH_BONUS) + FULL_POINTS_E + [3],
        ], columns=COLUMNS))
    
    def test_create_grading_file_no_project(self):
        no_project = list(FULL_POINTS_A)
        no_project[6] = 0
        no_project_with_bonus = list(FULL_POINTS_A_WITH_BONUS)
        no_project_with_bonus[6] = 0
        self.assert_equal_grades(pd.DataFrame([
            no_project + FULL_POINTS_E + [3],
            no_project_with_bonus + FULL_POINTS_E + [3],
        ], columns=COLUMNS))

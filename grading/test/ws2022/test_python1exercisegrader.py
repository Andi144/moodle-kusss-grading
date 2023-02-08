import pandas as pd

from graders.ws2022.python1exercisegrader import Python1ExerciseGrader
from test.abstractgradertest import AbstractGraderTest

COLUMNS = [f"Assignment: Assignment {i + 1} (Real)" for i in range(10)] + \
          ["Assignment: Assignment 11 (Bonus) (Real)"] + \
          ["Quiz: Exam (Real)", "Quiz: Retry Exam (Real)", "Quiz: Retry Exam 2 (Real)"] + \
          ["expected_grade"]
FULL_POINTS_A_WITHOUT_BONUS = [100] * 10
FULL_POINTS_A = FULL_POINTS_A_WITHOUT_BONUS + [50]
FULL_POINTS_E = [100, "", ""]


class Python1ExerciseGraderTest(AbstractGraderTest):
    
    def get_grader_class(self) -> type:
        return Python1ExerciseGrader
    
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
            # exam 1 (considering the +0.5 bonus points)
            FULL_POINTS_A + [0, "-", "-"] + [5],  # actual: 0.5 points
            FULL_POINTS_A + [49, "-", "-"] + [5],  # actual: 49.5 points
            FULL_POINTS_A + [49.4, "-", "-"] + [5],  # actual: 49.9 points
            # exam 2
            FULL_POINTS_A + ["-", 0, "-"] + [5],
            FULL_POINTS_A + ["-", 49, "-"] + [5],
            FULL_POINTS_A + ["-", 49.9, "-"] + [5],
            # exam 3
            FULL_POINTS_A + ["-", "-", 0] + [5],
            FULL_POINTS_A + ["-", "-", 49] + [5],
            FULL_POINTS_A + ["-", "-", 49.9] + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_exam_threshold_positive(self):
        # full assignment points means 1050/1100, so if the exam is positive, it's a "very good" (1)
        self.assert_equal_grades(pd.DataFrame([
            # exam 1 (considering the +0.5 bonus points)
            FULL_POINTS_A + [49.5, "-", "-"] + [1],
            FULL_POINTS_A + [50, "-", "-"] + [1],
            # exam 2
            FULL_POINTS_A + ["-", 50, "-"] + [1],
            # exam 3
            FULL_POINTS_A + ["-", "-", 50] + [1],
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
        # >= 3 means failing
        assignments = [[0] * i + FULL_POINTS_A_WITHOUT_BONUS[i:] + [50] + FULL_POINTS_E + [5]
                       for i in range(3, len(FULL_POINTS_A_WITHOUT_BONUS) + 1)]
        self.assert_equal_grades(pd.DataFrame(assignments, columns=COLUMNS))
    
    def test_create_grading_file_combined_assignments_threshold_negative(self):
        # bonus points should not change anything
        self.assert_equal_grades(pd.DataFrame([
            # all assignments with 49% each (with and without bonus)
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.49 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [50] + FULL_POINTS_E + [5],
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.49 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [0] + FULL_POINTS_E + [5],
            # mixed percentages with >= 25% (=passed) ---> combined < 50% (with and without bonus)
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.25 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [50] + FULL_POINTS_E + [5],
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.25 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [0] + FULL_POINTS_E + [5],
            [sum(FULL_POINTS_A_WITHOUT_BONUS[:4]) * 0.75 / len(FULL_POINTS_A_WITHOUT_BONUS[:4])] * len(FULL_POINTS_A_WITHOUT_BONUS[:4]) + [sum(FULL_POINTS_A_WITHOUT_BONUS[4:]) * 0.3 / len(FULL_POINTS_A_WITHOUT_BONUS[4:])] * len(FULL_POINTS_A_WITHOUT_BONUS[4:]) + [50] + FULL_POINTS_E + [5],
            [sum(FULL_POINTS_A_WITHOUT_BONUS[:4]) * 0.75 / len(FULL_POINTS_A_WITHOUT_BONUS[:4])] * len(FULL_POINTS_A_WITHOUT_BONUS[:4]) + [sum(FULL_POINTS_A_WITHOUT_BONUS[4:]) * 0.3 / len(FULL_POINTS_A_WITHOUT_BONUS[4:])] * len(FULL_POINTS_A_WITHOUT_BONUS[4:]) + [0] + FULL_POINTS_E + [5],
        ], columns=COLUMNS))
    
    # noinspection PyTypeChecker
    def test_create_grading_file_assignments_total_positive(self):
        # bonus points should not change anything for these specific assignment points
        self.assert_equal_grades(pd.DataFrame([
            # all assignments with 50% each (with and without bonus)
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.5 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [50] + FULL_POINTS_E + [4],
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.5 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [0] + FULL_POINTS_E + [4],
            # mixed assignments with >= 25% (=passed), rest all points ---> combined >= 50% (with and without bonus)
            [sum(FULL_POINTS_A_WITHOUT_BONUS[:5]) * 0.75 / len(FULL_POINTS_A_WITHOUT_BONUS[:5])] * len(FULL_POINTS_A_WITHOUT_BONUS[:5]) + [sum(FULL_POINTS_A_WITHOUT_BONUS[5:]) * 0.3 / len(FULL_POINTS_A_WITHOUT_BONUS[5:])] * len(FULL_POINTS_A_WITHOUT_BONUS[5:]) + [50] + FULL_POINTS_E + [4],
            [sum(FULL_POINTS_A_WITHOUT_BONUS[:5]) * 0.75 / len(FULL_POINTS_A_WITHOUT_BONUS[:5])] * len(FULL_POINTS_A_WITHOUT_BONUS[:5]) + [sum(FULL_POINTS_A_WITHOUT_BONUS[5:]) * 0.3 / len(FULL_POINTS_A_WITHOUT_BONUS[5:])] * len(FULL_POINTS_A_WITHOUT_BONUS[5:]) + [0] + FULL_POINTS_E + [4],
            # two assignments dropped, i.e., 0 points (with and without bonus)
            [0, 0] + FULL_POINTS_A_WITHOUT_BONUS[2:] + [50] + FULL_POINTS_E + [2],
            ["-", "-"] + FULL_POINTS_A_WITHOUT_BONUS[2:] + [50] + FULL_POINTS_E + [2],
            [0, 0] + FULL_POINTS_A_WITHOUT_BONUS[2:] + [0] + FULL_POINTS_E + [2],
            ["-", "-"] + FULL_POINTS_A_WITHOUT_BONUS[2:] + [0] + FULL_POINTS_E + [2],
        ], columns=COLUMNS))
    
    def test_create_grading_file_bonus_assignment(self):
        # bonus points should change the grades
        self.assert_equal_grades(pd.DataFrame([
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.58 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [50] + FULL_POINTS_E + [3],  # 10 * 58 (assignments) + 100(.5) (exam (1)) + 50 (bonus) = 730(.5) -> /1100 ~ 66% -> "3"
            [sum(FULL_POINTS_A_WITHOUT_BONUS) * 0.58 / len(FULL_POINTS_A_WITHOUT_BONUS)] * len(FULL_POINTS_A_WITHOUT_BONUS) + [0] + FULL_POINTS_E + [4],  # 10 * 58 (assignments) + 100(.5) (exam (1)) + 0 (bonus) = 680(.5) -> /1100 ~ 62% -> "4"
        ], columns=COLUMNS))

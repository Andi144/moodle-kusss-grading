import os
import unittest

import pandas as pd

from graders.ws2021.handson1lecturegrader import HandsOn1LectureGrader

MOODLE_FILE = "moodle_file.csv"
KUSSS_PARTICIPANTS_FILE = "kusss_participants_file.csv"
GRADING_FILE = "grading.csv"


class HandsOn1LectureGraderTest(unittest.TestCase):
    
    def tearDown(self):
        # fail silently if the files could not be found
        def silent_remove(file):
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
        
        silent_remove(MOODLE_FILE)
        silent_remove(KUSSS_PARTICIPANTS_FILE)
        silent_remove(GRADING_FILE)
    
    def test_create_grading_file_q1q2_threshold_negative(self):
        # columns: q1, q2, qretry, expected grade
        self.assert_equal_grades(pd.DataFrame([
            # q1
            [0, 100, "-", 5],
            [39, 100, "-", 5],
            ["-", 100, "-", 5],
            # q2
            [100, 0, "-", 5],
            [100, 39, "-", 5],
            [100, "-", "-", 5],
        ]))
    
    def test_create_grading_file_q1q2_total_negative(self):
        # columns: q1, q2, qretry, expected grade
        self.assert_equal_grades(pd.DataFrame([
            [40, 59, "-", 5],
            [49, 50, "-", 5],
            [59, 40, "-", 5],
            [50, 49, "-", 5],
        ]))
    
    def test_create_grading_file_q1q2_total_positive(self):
        # columns: q1, q2, qretry, expected grade
        self.assert_equal_grades(pd.DataFrame([
            [40, 60, "-", 4],
            [60, 40, "-", 4],
            [50, 50, "-", 4],
            [100, 100, "-", 1],
        ]))
    
    def test_create_grading_file_qretry_negative(self):
        # columns: q1, q2, qretry, expected grade
        self.assert_equal_grades(pd.DataFrame([
            # should be independent of q1 + q2
            ["-", "-", 99, 5],
            ["-", 100, 99, 5],
            [100, "-", 99, 5],
            [39, 100, 99, 5],
            [100, 39, 99, 5],
            [100, 100, 99, 5],
        ]))
    
    def test_create_grading_file_qretry_positive(self):
        # columns: q1, q2, qretry, expected grade
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
        ]))
    
    def assert_equal_grades(self, points: pd.DataFrame, moodle_file: str = MOODLE_FILE,
                            kusss_participants_file: str = KUSSS_PARTICIPANTS_FILE, grading_file: str = GRADING_FILE):
        df = HandsOn1LectureGraderTest.create_moodle_file_with_points(points, moodle_file)
        HandsOn1LectureGraderTest.create_matching_kusss_participants_file(df, kusss_participants_file)
        
        grader = HandsOn1LectureGrader(moodle_file, verbose=False)
        gdf = grader.create_grading_file(kusss_participants_file, grading_file=grading_file)
        # use more detailed assertion checking instead of faster but less detailed global assertion
        # self.assertTrue(gdf["grade"].equals(points["expected_grade"]))
        for i, (expected_grade, actual_grade) in enumerate(zip(points.iloc[:, 3], gdf["grade"])):
            self.assertEqual(expected_grade, actual_grade, msg=f"\n{gdf.iloc[i]}")
    
    @staticmethod
    def create_moodle_file_with_points(points: pd.DataFrame, moodle_file: str):
        df = points.copy()
        df.columns = ["Quiz: Exam 1 (Real)", "Quiz: Exam 2 (Real)", "Quiz: Retry Exam (Real)", "expected_grade"]
        df["First name"] = "A"
        df["Surname"] = "B"
        df["ID number"] = range(len(points))
        df.to_csv(moodle_file, index=False)
        return df
    
    @staticmethod
    def create_matching_kusss_participants_file(moodle_df: pd.DataFrame, kusss_participants_file: str):
        df = pd.DataFrame()
        df["Matrikelnummer"] = moodle_df["ID number"].apply(lambda x: f"k{x}")
        df["SKZ"] = 123
        df.to_csv(kusss_participants_file, sep=";", index=False)

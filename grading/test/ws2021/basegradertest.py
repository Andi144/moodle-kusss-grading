import os
import unittest

import pandas as pd

MOODLE_FILE = "moodle_file.csv"
KUSSS_PARTICIPANTS_FILE = "kusss_participants_file.csv"
GRADING_FILE = "grading.csv"


class BaseGraderTest(unittest.TestCase):
    
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
    
    def assert_equal_grades(self, points: pd.DataFrame, moodle_file: str = MOODLE_FILE,
                            kusss_participants_file: str = KUSSS_PARTICIPANTS_FILE, grading_file: str = GRADING_FILE,
                            grader_init_kwargs: dict = None, grader_create_grading_file_kwargs: dict = None):
        """
        Checks whether the concrete grader (see method `get_grader_class`) results in the same
        grades as specified by the given ``points`` pd.DataFrame. This points dataframe must
        have all required columns needed to calculate the grade with the concrete grader and
        in addition, the last column must contain the expected grade. The column names must be
        provided by the method ``get_columns``.
        
        :param points: The pd.DataFrame containing the points and, in the last column, the
            expected grade that the respective points should result in.
        :param moodle_file: The temporary moodle CSV file. Unless a different file is specified,
            the file will be deleted after each test case.
        :param kusss_participants_file: The temporary KUSSS participants CSV file. Unless a
            different file is specified, the file will be deleted after each test case.
        :param grading_file: The temporary output grading CSV file. Unless a different file is
            specified, the file will be deleted after each test case.
        :param grader_init_kwargs: Additional keyword arguments that are passed to the ``__init__``
            method when instantiating the concrete grader class (as given by `get_grader_class`).
        :param grader_create_grading_file_kwargs: Additional keyword arguments that are passed to
            the ``create_grading_file`` method of the instantiated grader.
        """
        if grader_init_kwargs is None:
            grader_init_kwargs = dict()
        if grader_create_grading_file_kwargs is None:
            grader_create_grading_file_kwargs = dict()
        
        df = BaseGraderTest.create_moodle_file_with_points(points, self.get_columns(), moodle_file)
        BaseGraderTest.create_matching_kusss_participants_file(df, kusss_participants_file)
        
        grader = self.get_grader_class()(moodle_file, verbose=False, **grader_init_kwargs)
        gdf = grader.create_grading_file(kusss_participants_file, grading_file=grading_file,
                                         **grader_create_grading_file_kwargs)
        
        # use more detailed assertion checking instead of faster but less detailed global assertion
        # self.assertTrue(gdf["grade"].equals(points["expected_grade"]))
        for i, (expected_grade, actual_grade) in enumerate(zip(points.iloc[:, -1], gdf["grade"])):
            self.assertEqual(expected_grade, actual_grade, msg=f"\n{gdf.iloc[i]}")
    
    def get_columns(self) -> list[str]:
        """
        Returns the list of column names of the ``points`` pd.DataFrame which is passed
        to the ``assert_equal_grades`` method (number of columns must be identical).
        """
        raise NotImplementedError("test subclass must return the columns of the 'points' pd.DataFrame which is "
                                  "passed to the 'assert_equal_grades' method")
    
    def get_grader_class(self) -> type:
        """
        Returns the class/type of the concrete grader which should be instantiated in
        each test method, i.e., the grader to be tested.
        """
        raise NotImplementedError("test subclass must return the concrete grader class/type which should be "
                                  "instantiated in each test method")
    
    @staticmethod
    def create_moodle_file_with_points(points: pd.DataFrame, columns: list[str], moodle_file: str) -> pd.DataFrame:
        df = points.copy()
        df.columns = columns
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

from functools import reduce
from typing import Union, Iterable

import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 24
MAX_EXAM_POINTS = 90


class SW1ExerciseGrader(Grader):
    
    def __init__(self, moodle_file: str, exam_files: Union[str, list[str]], exam_sep: str = "\t",
                 exam_matr_id_col: str = "Matr.Nr.", exam_points_col: str = "Summe", exam_decimal: str = ",",
                 exam_encoding="utf8", bonus_assignment_words: Iterable = None, **kwargs):
        """
        Initializes a new SW1ExerciseGrader object.
        
        :param moodle_file: The path to the CSV input file that contains the grading
            information, i.e., the points for assignments (exported via Moodle).
        :param exam_files: Either a single string that indicates the path of the exam CSV
            input file, or a list of strings that indicate multiple paths of exam CSV input
            files. If it is a list, then the order is in chronologically ascending order,
            i.e., the most recent exam result is the file specified last.
        :param exam_sep: The separator character of the exam CSV input file(s). Default: "\t"
        :param exam_matr_id_col: The column name of the exam CSV input file(s) that
            contains the matriculation ID. Default: "Matrikelnummer"
        :param exam_points_col: The column name of the exam CSV input file(s) that
            contains the points of the exam. Default: "Summe"
        :param exam_decimal: The decimal separator character when reading the points from
            the exam CSV input file(s). Default: ","
        :param exam_encoding: The encoding to use when reading each file specified by
            ``exam_files``. Default: "utf8"
        :param bonus_assignment_words: A collection of case-insensitive words that indicate
            to treat an assignment column as bonus assignment column if any word of this
            collection is contained within this column. Default: None = ["bonus"], i.e.,
            every assignment column is treated as a bonus assignment column which contains
            "bonus" (case-insensitive)
        :param kwargs: Additional keyword arguments that are passed to ``Grader.__init__``.
        """
        super().__init__(moodle_file, **kwargs)
        
        if isinstance(exam_files, str):
            exam_files = [exam_files]
        if bonus_assignment_words is None:
            bonus_assignment_words = ["bonus"]
        bonus_assignment_words = [w.lower() for w in bonus_assignment_words]
        
        # read separate exam CSVs (one for each exam) and merge with self.df
        def read_exam_file(index: int, file: str):
            df = pd.read_csv(file, sep=exam_sep, usecols=[exam_matr_id_col, exam_points_col],
                             decimal=exam_decimal, encoding=exam_encoding)
            return df.rename(columns={exam_points_col: f"Exam {index}"})
        
        # use the same order as specified in the input exam list, i.e., the last exam file
        # represents the most recent exam
        edfs = [read_exam_file(i, f) for i, f in enumerate(exam_files)]
        exam_df = reduce(lambda left, right: pd.merge(left, right, on=[exam_matr_id_col], how="outer"), edfs)
        util.check_matr_id_format(exam_df[exam_matr_id_col])
        
        self.df = self.df.merge(exam_df, left_on="ID number", right_on=exam_matr_id_col, how="left")
        self._print(f"size after merging with exam results {exam_df.shape}: {self.df.shape}")
        # update to the quiz columns
        assert len(self.quiz_cols) == 0
        self.quiz_cols = [c for c in exam_df.columns if c != exam_matr_id_col]
        
        # split default assignments into mandatory and bonus assignments
        self.mandatory_assignment_cols = []
        self.bonus_assignment_cols = []
        for c in self.assignment_cols:
            if any([w in c.lower() for w in bonus_assignment_words]):
                self.bonus_assignment_cols.append(c)
            else:
                self.mandatory_assignment_cols.append(c)
        
        # drop all with < 3 mandatory assignment submissions, i.e., keep rows with >= 3 mandatory submissions
        len_before = len(self.df)
        self.df.dropna(thresh=3, subset=self.mandatory_assignment_cols, inplace=True)
        if len_before != len(self.df):
            self._print(f"dropped {len_before - len(self.df)} entries due to fewer than 3 mandatory submissions")
        
        # replace NaN points with 0 to make things easier when calculating the grade
        self.df[self.assignment_cols] = self.df[self.assignment_cols].fillna(0)
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        # at least 8 mandatory assignments must be "successful", i.e., >= 8 points
        if (row[self.mandatory_assignment_cols] >= 8).sum() < 8:
            return pd.Series([5, "fewer than 8 successful assignments"])
        # get most recent exam (if it exists)
        exams = row[self.quiz_cols].dropna()
        if len(exams) == 0:
            return pd.Series([5, "exam missing"])
        scaled_exam_points = MAX_POINTS * exams.iloc[-1] / MAX_EXAM_POINTS
        if scaled_exam_points < MAX_POINTS * 0.5:
            return pd.Series([5, "exam negative"])
        scaled_assignment_points = row[self.assignment_cols].sum() / len(self.mandatory_assignment_cols)
        return util.create_grade(scaled_assignment_points * 0.8 + scaled_exam_points * 0.2, MAX_POINTS)


if __name__ == "__main__":
    parser = util.get_grading_args_parser()
    parser.add_argument("-ef", "--exam_files", type=str, nargs="+", required=True,
                        help="CSV export files containing the exam results. If multiple files are specified, then "
                             "the order is in chronologically ascending order, i.e., the most recent exam result "
                             "is the file specified last.")
    args = parser.parse_args()
    grader = SW1ExerciseGrader(args.moodle_file, args.exam_files)
    gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file)
    gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)

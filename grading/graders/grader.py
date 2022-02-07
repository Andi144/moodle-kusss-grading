import os.path
import re
import warnings
from typing import Iterable, Union, Sequence

import numpy as np
import pandas as pd

MOODLE_DE_TO_EN_FULL = {
    "Vorname": "First name",
    "Nachname": "Surname",
    "ID-Nummer": "ID number",
    "E-Mail-Adresse": "Email address",
    "Zuletzt aus diesem Kurs geladen": "Last downloaded from this course"
}

MOODLE_DE_TO_EN_START = {
    "Aufgabe": "Assignment",
    "Test": "Quiz",
    "Kurs gesamt": "Course total",
}

MOODLE_DE_TO_EN_END = {
    "Punkte": "Real",
    "Prozentsatz": "Percentage",
}


class Grader:
    
    def __init__(self, moodle_file: str, ignore_assignment_words: Iterable = None, ignore_quiz_words: Iterable = None,
                 encoding: str = "utf8", verbose: bool = True):
        """
        Initializes a new Grader object.
        
        :param moodle_file: The path to the CSV input file that contains the grading
            information, i.e., the points for assignments and quizzes (exported via Moodle).
        :param ignore_assignment_words: A collection of words that indicate to drop an
            assignment column if any word of this collection is contained within this column.
            Default: [], i.e., every assignment column is kept
        :param ignore_quiz_words: A collection of words that indicate to drop a quiz
            column if any word of this collection is contained within this column.
            Default: ["Dummy"], i.e., every quiz column is dropped which contains "Dummy"
        :param encoding: The encoding to use when reading ``moodle_file``. Default: "utf8"
        :param verbose: Whether to print additional output information. Default: True
        """
        self.verbose = verbose
        if ignore_assignment_words is None:
            ignore_assignment_words = []
        if ignore_quiz_words is None:
            ignore_quiz_words = ["Dummy"]
        
        df = pd.read_csv(moodle_file, na_values="-", encoding=encoding)
        self._print(f"original size: {df.shape}")
        self.original_df = df.copy()
        df = self._to_en(df)
        # TODO: parameterize
        cols_to_drop = [c for c in df.columns if c.startswith("Course total")] + ["Last downloaded from this course"]
        df.drop(columns=cols_to_drop, inplace=True)
        
        # TODO: parameterize
        self.id_cols = ["First name", "Surname", "ID number"]
        self.assignment_cols = [c for c in df.columns if c.startswith("Assignment:") and
                                all([w not in c for w in ignore_assignment_words])]
        self.quiz_cols = [c for c in df.columns if c.startswith("Quiz:") and
                          all([w not in c for w in ignore_quiz_words])]
        # order columns (not necessary but nicer (debugging) output)
        df = df[self.id_cols + self.assignment_cols + self.quiz_cols]
        self._print(f"size after filtering columns: {df.shape}")
        
        # check if there are invalid matriculation ID numbers (e.g., due to having manually
        # added a student to Moodle who is not a registered KUSSS student); if there are, then
        # pandas could not convert them to np.int64 (should then be str, i.e., pandas object)
        if df["ID number"].dtype != np.int64:
            invalid = df[df["ID number"].str.contains(r"\D", regex=True)]
            if len(invalid) > 0:
                df.drop(invalid.index, inplace=True)
                df["ID number"] = df["ID number"].astype(np.int64)  # should now work
                self._print(f"dropped {len(invalid)} entries due to invalid matriculation IDs; new size: {df.shape}")
                warnings.warn(f"the following entries were dropped due to invalid matriculation IDs:\n"
                              f"{invalid[self.id_cols]}")
        
        # basic DataFrame is now finished at this point
        self.df = df
        # course-specific setup and adjustments (overridden in subclasses, if required)
        self._print("applying course-specific setup and adjustments...")
        self._course_setup()
        self._print(f"size after applying course-specific setup and adjustments: {self.df.shape}")
        if len(self.df) == 0:
            raise ValueError("no entries remain after dropping, cannot create Grader object")
    
    def _print(self, msg):
        if self.verbose:
            print(msg)
    
    def _to_en(self, df: pd.DataFrame):
        self._print("translating columns to English...")
        # quick check if it is already English
        for c in df.columns:
            if c in MOODLE_DE_TO_EN_FULL.values():
                self._print("columns appear to be already in English")
                return df
        
        new_columns = []
        for c in df.columns:
            # for whatever reason, Moodle inserts non-breaking spaces when exporting in German
            c = c.replace("\xa0", " ")
            original_c = c
            
            if c in MOODLE_DE_TO_EN_FULL:
                # direct replacement
                c = MOODLE_DE_TO_EN_FULL[c]
            else:
                # partial replacement
                for start_de, start_en in MOODLE_DE_TO_EN_START.items():
                    if c.startswith(start_de):
                        c = c.replace(start_de, start_en, 1)
                for end_de, end_en in MOODLE_DE_TO_EN_END.items():
                    c = re.sub(rf"\({end_de}\)$", f"({end_en})", c)
            
            if c == original_c:
                raise ValueError(f"could not translate column '{c}' into English")
            else:
                new_columns.append(c)
        
        assert len(df.columns) == len(new_columns)
        new_df = df.copy()
        new_df.columns = new_columns
        return new_df
    
    def _course_setup(self):
        """
        This method is called for setting up and adjusting the ``self.df`` pd.DataFrame,
        which might be important to create and calculate additional data/columns that
        can then be conveniently used in the grading method ``self.create_grade_row``.
        
        Per default, this method excludes/drops all students without any submission (i.e.,
        all NaN for assignments and quizzes), which means that those students will not be
        graded at the end (rather than getting a negative grade).
        
        Subclasses are encouraged to change this behavior, if required.
        """
        len_before = len(self.df)
        self.df.dropna(how="all", subset=self.assignment_cols + self.quiz_cols, inplace=True)
        self._print(f"dropped {len_before - len(self.df)} entries due to all NaN (no participation at all)")
    
    def create_grading_file(self, kusss_participants_files: Union[str, list[str]],
                            input_sep: str = ";", matr_id_col: str = "Matrikelnummer", study_id_col: str = "SKZ",
                            output_sep: str = ";", header: bool = False, grading_file: str = None,
                            cols_to_export: Sequence = None, input_encoding: str = "ANSI",
                            output_encoding: str = "utf8") -> pd.DataFrame:
        """
        Creates a grading CSV file that can be uploaded to KUSSS based on the CSV input
        file(s) that contain the participants/students of some course(s) (exported via KUSSS).
        
        :param kusss_participants_files: Either a single string that indicates the path
            of the participants CSV input file, or a list of strings that indicate multiple
            paths of participants CSV input files. If it is a list, the participants will
            simply be merged, thereby dropping duplicate entries, where a duplicate entry
            is determined on the tuple (``matr_id_col``, ``study_id_col``).
        :param input_sep: The separator character of the participants CSV input file(s).
            Default: ";"
        :param matr_id_col: The column name of the participants CSV input file(s) that
            contains the matriculation ID. Default: "Matrikelnummer"
        :param study_id_col: The column name of the participants CSV input file(s) that
            contains the study ID. Default: "SKZ"
        :param output_sep: The separator character of the grading CSV output file.
            Default: ";"
        :param header: Whether to add a header to the grading CSV output file.
            Default: False
        :param grading_file: If not None, specifies the path where the grading CSV output
            will be stored. Otherwise, the grading file will be stored at the same location
            as the input file (or as the first input file if multiple files were specified).
            Moreover, the default file name will be "grading.csv". Default: None
        :param cols_to_export: The columns to export to the grading CSV output file. Default:
            [``matr_id_col``, ``study_id_col``, "grade"]
        :param input_encoding: The encoding to use when reading each file specified by
            ``kusss_participants_files``. Default: "ANSI"
        :param output_encoding: The encoding to use when writing ``grading_file``. Default: "utf8"
        :return: The final pd.DataFrame that contains all information including grades and
            the reasons for these grades.
        """
        if isinstance(kusss_participants_files, str):
            kusss_participants_files = [kusss_participants_files]
        kdfs = [pd.read_csv(f, sep=input_sep, usecols=[matr_id_col, study_id_col], encoding=input_encoding)
                for f in kusss_participants_files]
        
        # check duplicate entries (students who are found multiple times)
        full_kdf = pd.concat(kdfs, ignore_index=True)
        kdf = full_kdf.copy().drop_duplicates()
        diff = full_kdf[full_kdf.duplicated()].drop_duplicates()
        if len(diff) > 0:
            warnings.warn(f"the following {len(diff)} duplicate entries were dropped (might be OK, e.g., if a "
                          f"student was unregistered from one course but the export still contains an entry):\n{diff}")
        
        kdf[matr_id_col] = kdf[matr_id_col].str.replace("k", "").astype(np.int64)
        # skips those that are not registered in this particular KUSSS course
        df = self.df.merge(kdf, left_on="ID number", right_on=matr_id_col)
        self._print(f"size after merging with KUSSS participants {kdf.shape}: {df.shape}")
        
        # apply the actual grading logic (implemented in concrete course subclasses)
        df[["grade", "grade_reason"]] = df.apply(self._create_grade_row, axis=1)
        
        if grading_file is None:
            grading_file = os.path.join(os.path.split(kusss_participants_files[0])[0], "grading.csv")
        # default format requirements for KUSSS grading import: "matriculationID;studyID;grade"
        if cols_to_export is None:
            cols_to_export = [matr_id_col, study_id_col, "grade"]
        df[cols_to_export].to_csv(grading_file, sep=output_sep, index=False, header=header, encoding=output_encoding)
        self._print(f"KUSSS grading file ({len(df)} grades) written to: '{grading_file}'")
        
        return df
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        """
        This method is called for each row in ``self.df`` and expects a pd.Series object
        of size 2 to be returned. The first entry of this series must be the grade (type:
        np.int64), the second entry must be the reason for this grade (type: str, i.e.,
        pandas object), which might simply be am empty string if there is no special
        reason for this grade.
        
        :param row: The row (one of ``self.df``) to calculate the grade for.
        :return: A pd.Series object where the first entry is the grade (type: np.int64) and
            the second entry the reason (type: str, i.e., pandas object) for this grade.
        """
        raise NotImplementedError("must be implemented in subclass")

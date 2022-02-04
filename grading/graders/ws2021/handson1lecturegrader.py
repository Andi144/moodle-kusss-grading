import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS_Q1 = 100
MAX_POINTS_Q2 = 100
MAX_POINTS_ALL_Q = MAX_POINTS_Q1 + MAX_POINTS_Q2
MAX_POINTS_QRETRY = MAX_POINTS_ALL_Q

THRESHOLD_INDIVIDUAL_Q = 0.4


class HandsOn1LectureGrader(Grader):
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        quiz1_cols = [c for c in self.quiz_cols if "Exam 1 " in c]
        quiz2_cols = [c for c in self.quiz_cols if "Exam 2 " in c]
        quizretry_cols = [c for c in self.quiz_cols if "Retry Exam " in c]
        assert len(quiz1_cols) == 1 and len(quiz2_cols) == 1 and len(quizretry_cols) == 1
        quiz1_col = quiz1_cols[0]
        quiz2_col = quiz2_cols[0]
        quizretry_col = quizretry_cols[0]
        
        if np.isnan(row[quizretry_col]):
            if row[quiz1_col] < THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q2 or \
                    row[quiz2_col] < THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q2:
                return pd.Series([5, "individual quiz thresholds not reached"])
            total = row[quiz1_col] + row[quiz2_col]
        else:
            total = row[quizretry_col]
        
        if total >= 87.5:
            return pd.Series([1, ""])
        if total >= 75:
            return pd.Series([2, ""])
        if total >= 62.5:
            return pd.Series([3, ""])
        if total >= 50:
            return pd.Series([4, ""])
        return pd.Series([5, ""])


if __name__ == "__main__":
    args = util.get_grading_args()
    grader = HandsOn1LectureGrader(args.moodle_file)
    grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file)

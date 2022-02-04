import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS_Q1 = 100
MAX_POINTS_Q2 = 100
MAX_POINTS = MAX_POINTS_Q1 + MAX_POINTS_Q2

THRESHOLD_INDIVIDUAL_Q = 0.4


class HandsOn1LectureGrader(Grader):
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        quiz1_cols = [c for c in self.quiz_cols if "Exam 1 " in c]
        quiz2_cols = [c for c in self.quiz_cols if "Exam 2 " in c]
        quizretry_cols = [c for c in self.quiz_cols if "Retry Exam " in c]
        assert len(quiz1_cols) == 1 and len(quiz2_cols) == 1 and len(quizretry_cols) == 1
        quiz1 = row[quiz1_cols[0]]
        quiz2 = row[quiz2_cols[0]]
        quizretry = row[quizretry_cols[0]]
        
        if np.isnan(quizretry):
            if quiz1 >= THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q2 and quiz2 >= THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q2:
                total = quiz1 + quiz2
            else:
                return pd.Series([5, "individual quiz thresholds not reached"])
        else:
            total = quizretry
        
        # ensure that total is scaled to percent
        total = 100 * total / MAX_POINTS
        
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

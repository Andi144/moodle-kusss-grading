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
        e11 = row["Quiz: Exam 1 (Real)"]
        e12 = row["Quiz: Exam 2 (Real)"]
        e2 = row["Quiz: Retry Exam (Real)"]
        # since the second retry exam was added later, it is not part of the
        # earlier Moodle CSV exports (which would then lead to a crash here)
        e3 = row["Quiz: Retry Exam 2 (Real)"] if "Quiz: Retry Exam 2 (Real)" in row else np.nan
        
        # most recent exam takes precedence
        if not np.isnan(e3):
            total = e3
        elif not np.isnan(e2):
            total = e2
        else:
            if e11 >= THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q2 and e12 >= THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q2:
                total = e11 + e12
            else:
                return pd.Series([5, "individual exam thresholds not reached"])
        
        return util.create_grade(total, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "handson1")
    grader = HandsOn1LectureGrader(args.moodle_file)
    # gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file)
    # only create grades for students who participated in the retry exam
    gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file,
                                         row_filter=lambda row: not np.isnan(row["Quiz: Retry Exam 2 (Real)"]))
    gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)

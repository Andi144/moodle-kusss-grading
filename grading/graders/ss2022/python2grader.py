import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS_EXAM = 10
MAX_POINTS_A1 = 35
MAX_POINTS_A2 = 55  # 20 bonus points not counted (10 from ex5, 10 from ex6)
MAX_POINTS_ALL_A = MAX_POINTS_A1 + MAX_POINTS_A2
MAX_POINTS = MAX_POINTS_EXAM + MAX_POINTS_ALL_A

THRESHOLD_EXAM = 0.5
THRESHOLD_INDIVIDUAL_A = 0.25
THRESHOLD_ALL_A = 0.5


class Python2Grader(Grader):
    
    def _process_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super()._process_entries(df)
        a1_cols = [c for c in self.assignment_cols if any([f"Exercise {i} " in c for i in range(1, 3 + 1)])]
        a2_cols = [c for c in self.assignment_cols if any([f"Exercise {i} " in c for i in range(4, 6 + 1)])]
        df["a1_total"] = df[a1_cols].sum(axis=1)
        df["a2_total"] = df[a2_cols].sum(axis=1)
        return df
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        # assignments processing (if students already failed the course via some
        # assignment rule, there is no need to even look at the exam, since it
        # will not make a difference anymore, i.e., assignment fails are a
        # "hard" fail (unchangeable grade 5), while exam fails are a "soft" fail
        # (can be potentially corrected by a retry exam)
        a1_points = row["a1_total"]
        a2_points = row["a2_total"]
        if a1_points < MAX_POINTS_A1 * THRESHOLD_INDIVIDUAL_A:
            return pd.Series([5, "assignment 1 threshold not reached"])
        if a2_points < MAX_POINTS_A2 * THRESHOLD_INDIVIDUAL_A:
            return pd.Series([5, "assignment 2 threshold not reached"])
        if a1_points + a2_points < MAX_POINTS_ALL_A * THRESHOLD_ALL_A:
            return pd.Series([5, "total assignment threshold not reached"])
        
        # exam processing
        e1 = row["Quiz: Exam (Real)"]
        e2 = row["Quiz: Retry Exam (Real)"]
        e3 = row["Quiz: Retry Exam 2 (Real)"]
        # most recent exam takes precedence
        if not np.isnan(e3):
            e_points = e3
        elif not np.isnan(e2):
            e_points = e2
        elif not np.isnan(e1):
            e_points = e1
        else:
            return pd.Series([5, "no exam participation"])
        if e_points < MAX_POINTS_EXAM * THRESHOLD_EXAM:
            return pd.Series([5, "exam threshold not reached"])
        
        return util.create_grade(e_points + a1_points + a2_points, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "python2")
    assert args.grading_file is None, "not supported since all KUSSS participants files are treated individually"
    grader = Python2Grader(args.moodle_file)
    for kusss_participants_file in args.kusss_participants_files:
        try:
            # regular; below is creating grades only for retry exam participants
            # gdf, gf = grader.create_grading_file(kusss_participants_file)
            gdf, gf = grader.create_grading_file(kusss_participants_file,
                                                 row_filter=lambda row: not np.isnan(row["Quiz: Retry Exam (Real)"]))
            gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)
        except ValueError as e:
            print(f"### ignore file '{kusss_participants_file}' because of '{e}'")
        print()

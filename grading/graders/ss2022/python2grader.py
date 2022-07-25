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
    
    def _course_setup(self):
        super()._course_setup()
        a1_cols = [c for c in self.assignment_cols if any([f"Exercise {i} " in c for i in range(1, 3 + 1)])]
        a2_cols = [c for c in self.assignment_cols if any([f"Exercise {i} " in c for i in range(4, 6 + 1)])]
        self.df["a1_total"] = self.df[a1_cols].sum(axis=1)
        self.df["a2_total"] = self.df[a2_cols].sum(axis=1)
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
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
        
        # assignments processing
        a1_points = row["a1_total"]
        a2_points = row["a2_total"]
        if a1_points < MAX_POINTS_A1 * THRESHOLD_INDIVIDUAL_A:
            return pd.Series([5, "assignment 1 threshold not reached"])
        if a2_points < MAX_POINTS_A2 * THRESHOLD_INDIVIDUAL_A:
            return pd.Series([5, "assignment 2 threshold not reached"])
        if a1_points + a2_points < MAX_POINTS_ALL_A * THRESHOLD_ALL_A:
            return pd.Series([5, "total assignment threshold not reached"])
        
        return util.create_grade(e_points + a1_points + a2_points, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "python2")
    grader = Python2Grader(args.moodle_file)
    gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file)
    gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)

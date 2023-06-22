import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS_EXAM = 100
# all assignments have 100 points (except the bonus assignment (50) and the project (400) which we can ignore here)
MAX_POINTS_A = 100
N_ASSIGNMENTS = 6
MAX_POINTS_PROJECT = 400  # ignore the optional 50 or 100 bonus points here
MAX_POINTS_ALL_A = N_ASSIGNMENTS * MAX_POINTS_A + MAX_POINTS_PROJECT
assert MAX_POINTS_ALL_A == 1000
MAX_POINTS = MAX_POINTS_EXAM + MAX_POINTS_ALL_A
assert MAX_POINTS == 1100
MAX_N_ASSIGNMENTS_FAILED = 2  # max number of allowed assignment fails (includes the project)

THRESHOLD_EXAM = 0.5
THRESHOLD_INDIVIDUAL_A = 0.25
THRESHOLD_ALL_A = 0.5


class Python2ExerciseGrader(Grader):
    
    def _process_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        len_before = len(df)
        df.dropna(how="all", subset=self.assignment_cols, inplace=True)
        if len_before != len(df):
            self._print(f"dropped {len_before - len(df)} entries due to all assignments being NaN (no participation in "
                        f"the assignments at all)")
        return df
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        # assignments processing (if students already failed the course via some assignment rule, there is no need to
        # even look at the exam, since it will not make a difference anymore, i.e., assignment fails are a "hard" fail
        # (unchangeable grade 5), while exam fails are a "soft" fail (can be potentially corrected by a retry exam)
        points = 0
        n_failed = 0
        for i in range(N_ASSIGNMENTS):
            a_points = row[f"Assignment: Assignment {i + 1} (Real)"]
            if np.isnan(a_points):
                a_points = 0
            points += a_points
            if a_points < MAX_POINTS_A * THRESHOLD_INDIVIDUAL_A:
                n_failed += 1
        # special check for project because of the special assignment name
        project_points = row[f"Assignment: Assignment 7 (Project) (Real)"]
        if np.isnan(project_points):
            project_points = 0
        if project_points < MAX_POINTS_PROJECT * THRESHOLD_INDIVIDUAL_A:
            n_failed += 1
        if n_failed > MAX_N_ASSIGNMENTS_FAILED:
            return pd.Series([5, f"more than {MAX_N_ASSIGNMENTS_FAILED} individual assignment thresholds not reached"])
        a_points = points + project_points
        if a_points < MAX_POINTS_ALL_A * THRESHOLD_ALL_A:
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
        
        # only now add bonus points (after all requirement checks from above)
        bonus_points = row["Assignment: Assignment 8 (Bonus) (Real)"]
        if not np.isnan(bonus_points):
            a_points += bonus_points
        
        return util.create_grade(e_points + a_points, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "python2")
    assert args.grading_file is None, "not supported since all KUSSS participants files are treated individually"
    grader = Python2ExerciseGrader(args.moodle_file)
    for kusss_participants_file in args.kusss_participants_files:
        try:
            gdf, gf = grader.create_grading_file(kusss_participants_file)
            gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)
        except ValueError as e:
            print(f"### ignore file '{kusss_participants_file}' because of '{e}'")
        print()

import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 700  # 7 assignments with 100 points each


# TODO: code duplication (ws2021)
class HandsOn1ExerciseGrader(Grader):
    
    # TODO: code duplication in python1exercisegrader (could move to common superclass, e.g., ExerciseGrader)
    def _process_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        len_before = len(df)
        df.dropna(how="all", subset=self.assignment_cols, inplace=True)
        if len_before != len(df):
            self._print(f"dropped {len_before - len(df)} entries due to all assignments being NaN (no participation in "
                        f"the assignments at all)")
        return df
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        # only one assignment can be skipped or graded with 0 points
        # replace 0 points with NaN to make things easier with pd.Series.isna()
        assignment_points = row[self.assignment_cols].replace(0, np.nan)
        if assignment_points.isna().sum() > 1:
            return pd.Series([5, "more than 1 assignment skipped/graded with 0 points"])
        return util.create_grade(assignment_points.sum(), MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "handson1")
    assert args.grading_file is None, "not supported since all KUSSS participants files are treated individually"
    grader = HandsOn1ExerciseGrader(args.moodle_file)
    for kusss_participants_file in args.kusss_participants_files:
        try:
            gdf, gf = grader.create_grading_file(kusss_participants_file)
            gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)
        except ValueError as e:
            print(f"### ignore file '{kusss_participants_file}' because of '{e}'")
        print()

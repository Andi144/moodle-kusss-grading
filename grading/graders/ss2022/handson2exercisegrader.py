import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 600  # 6 assignments with 100 points each


# TODO: Except for MAX_POINTS = 600 instead of 700, this code is identical to
#  ws2021.handson1exercisegrader. Maybe extract to common base class where the
#  maximum number of points (and/or number of assignments) can be parameterized.
class HandsOn2ExerciseGrader(Grader):
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        # only one assignment can be skipped or graded with 0 points
        # replace 0 points with NaN to make things easier with pd.Series.isna()
        assignment_points = row[self.assignment_cols].replace(0, np.nan)
        if assignment_points.isna().sum() > 1:
            return pd.Series([5, "more than 1 assignment skipped/graded with 0 points"])
        return util.create_grade(assignment_points.sum(), MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    grader = HandsOn2ExerciseGrader(args.moodle_file)
    gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file)
    gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)

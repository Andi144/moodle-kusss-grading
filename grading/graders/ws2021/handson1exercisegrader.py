import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 700  # 7 assignments with 100 points each


class HandsOn1ExerciseGrader(Grader):
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        # only one assignment can be skipped or graded with 0 points
        # replace 0 points with NaN to make things easier with pd.Series.isna()
        assignment_points = row[self.assignment_cols].replace(0, np.nan)
        if assignment_points.isna().sum() > 1:
            return pd.Series([5, "more than 1 assignment skipped/graded with 0 points"])
        return util.create_grade(assignment_points.sum(), MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args()
    grader = HandsOn1ExerciseGrader(args.moodle_file)
    gdf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file)
    gdf.to_csv(args.grading_file.replace(".csv", "_FULL.csv"))

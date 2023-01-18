import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 40


class HandsOn2LectureGrader(Grader):
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        e1 = row["Quiz: Exam (Real)"]
        e2 = row["Quiz: Retry Exam (Real)"]
        e3 = row["Quiz: Retry Exam 2 (Real)"]
        # most recent exam takes precedence
        if not np.isnan(e3):
            points = e3
        elif not np.isnan(e2):
            points = e2
        else:
            assert not np.isnan(e1)
            points = e1 + 0.5  # global 0.5 bonus points
        # if points are very close (< 0.1 difference) to the next full integer points,
        # round up, which might help some cases to switch over to the next grade; e.g.:
        # points = 34.95 ("Good") --> diff = 0.05 < 0.1 --> round to 35 ("Very Good")
        # (example is based on the default grading percentages of util.create_grade)
        decimals = points % 1
        if 1 - decimals < 0.1:
            points = round(points)
        return util.create_grade(points, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "handson2")
    grader = HandsOn2LectureGrader(args.moodle_file)
    gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file,
                                         row_filter=lambda row: (~row[grader.quiz_cols].isna()).any())
    gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)

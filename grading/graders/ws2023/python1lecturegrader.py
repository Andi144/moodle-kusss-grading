import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 100


class Python1LectureGrader(Grader):
    
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        e1 = row["Quiz: Exam (Real)"]
        e2 = row["Quiz: Retry Exam (Real)"]
        e3 = row["Quiz: Retry Exam 2 (Real)"]
        # most recent exam takes precedence
        if not np.isnan(e3):
            points = e3
        elif not np.isnan(e2):
            # +(2.5 / 3) points due to misleading answer in one question
            points = e2 + (2.5 / 3)
        else:
            assert not np.isnan(e1)
            # +(2.5 / 3) points due to misleading answer in one question
            points = e1 + (2.5 / 3)
        return util.create_grade(points, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "python1")
    grader = Python1LectureGrader(args.moodle_file)
    gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file,
                                         row_filter=lambda row: (~row[grader.quiz_cols].isna()).any(),
                                         warn_if_not_found_in_kusss_participants=True)
    gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)

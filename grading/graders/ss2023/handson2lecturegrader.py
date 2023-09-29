import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS = 100


class HandsOn2LectureGrader(Grader):
    
    # TODO: identical code to, e.g., Python2LectureGrader (should extract to common base class, maybe with template
    #  method to include optional bonus points for each of the three exams)
    def _create_grade_row(self, row: pd.Series) -> pd.Series:
        e1 = row["Quiz: Exam (Real)"]
        e2 = row["Quiz: Retry Exam (Real)"]
        e3 = row["Quiz: Retry Exam 2 (Real)"]
        # most recent exam takes precedence
        if not np.isnan(e3):
            points = e3
        elif not np.isnan(e2):
            # Bonus points since one question/answer covered a topic that was only presented in the exercise (LeakyReLU)
            points = e2 + 0.625
        else:
            assert not np.isnan(e1)
            points = e1
        return util.create_grade(points, MAX_POINTS)


if __name__ == "__main__":
    args = util.get_grading_args_parser().parse_args()
    util.args_sanity_check(args.moodle_file, args.kusss_participants_files, "handson2")
    grader = HandsOn2LectureGrader(args.moodle_file)
    gdf, gf = grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file,
                                         row_filter=lambda row: (~row[grader.quiz_cols].isna()).any(),
                                         warn_if_not_found_in_kusss_participants=True)
    gdf.to_csv(gf.replace(".csv", "_FULL.csv"), index=False)

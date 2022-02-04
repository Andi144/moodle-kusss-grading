import numpy as np
import pandas as pd

from graders import util
from graders.grader import Grader

MAX_POINTS_A1 = 15
MAX_POINTS_A2 = 30  # 5 bonus points not counted
MAX_POINTS_A3 = 35  # 5 bonus points not counted
MAX_POINTS_ALL_A = MAX_POINTS_A1 + MAX_POINTS_A2 + MAX_POINTS_A3
MAX_POINTS_Q1 = 10
MAX_POINTS_Q2 = 10
MAX_POINTS_ALL_Q = MAX_POINTS_Q1 + MAX_POINTS_Q2
MAX_POINTS_QRETRY = MAX_POINTS_ALL_Q

THRESHOLD_INDIVIDUAL_A = 0.25
THRESHOLD_ALL_A = 0.5
THRESHOLD_INDIVIDUAL_Q = 0.4
THRESHOLD_INDIVIDUAL_QRETRY = 0.5
THRESHOLD_ALL_Q = 0.5


class Python1Grader(Grader):
    
    def _course_setup(self):
        super()._course_setup()
        # Moodle exercise points are scaled by a factor of 10
        self.df[self.assignment_cols] /= 10
        # points are no properly and consistently scaled
        self._assignment_setup()
        self._quiz_setup()
    
    def _assignment_setup(self):
        assignment1_cols = [c for c in self.assignment_cols if any([f"Exercise {i} " in c for i in range(1, 4 + 1)])]
        assignment2_cols = [c for c in self.assignment_cols if any([f"Exercise {i} " in c for i in range(5, 15 + 1)])]
        assignment3_cols = [c for c in self.assignment_cols if any([f"Exercise {i} " in c for i in range(16, 21 + 1)])]
        
        assignments = [
            (assignment1_cols, "a1", MAX_POINTS_A1, THRESHOLD_INDIVIDUAL_A),
            (assignment2_cols, "a2", MAX_POINTS_A2, THRESHOLD_INDIVIDUAL_A),
            (assignment3_cols, "a3", MAX_POINTS_A3, THRESHOLD_INDIVIDUAL_A)
        ]
        
        # passed-flag for each assignment
        for cols, name, max_points, threshold in assignments:
            self.df[f"{name}_passed"] = self.df[cols].sum(axis=1) >= threshold * max_points
        
        # total points of all assignments (all exercises)
        self.df["a_total"] = self.df[self.assignment_cols].sum(axis=1)
    
    def _quiz_setup(self):
        quiz1_cols = [c for c in self.quiz_cols if "Exam 1 " in c]
        quiz2_cols = [c for c in self.quiz_cols if "Exam 2 " in c]
        quizretry_cols = [c for c in self.quiz_cols if "Retry Exam " in c]
        assert len(quiz1_cols) == 1 and len(quiz2_cols) == 1 and len(quizretry_cols) == 1
        quiz1_col = quiz1_cols[0]
        quiz2_col = quiz2_cols[0]
        quizretry_col = quizretry_cols[0]
        
        def create_quiz_passed_row(row):
            # exam check: q1 >= 40% and q2 >= 40% OR qretry >= 50% if qretry is not NaN
            if np.isnan(row[quizretry_col]):
                return (row[quiz1_col] >= THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q1) and \
                       (row[quiz2_col] >= THRESHOLD_INDIVIDUAL_Q * MAX_POINTS_Q2)
            return row[quizretry_col] >= THRESHOLD_INDIVIDUAL_QRETRY * MAX_POINTS_QRETRY
        
        # passed-flag for the exams (includes proper handling of normal exams and retry exam)
        self.df["q_passed"] = self.df[self.quiz_cols].apply(create_quiz_passed_row, axis=1)
        
        def create_quiz_total_row(row):
            # total points: q1 + q2 OR qretry if qretry is not NaN
            if np.isnan(row[quizretry_col]):
                return row[[quiz1_col, quiz2_col]].sum()
            return row[quizretry_col]
        
        # total points of exams (includes proper handling of normal exams and retry exam)
        self.df["q_total"] = self.df[self.quiz_cols].apply(create_quiz_total_row, axis=1)
    
    def _create_grade_row(self, row) -> pd.Series:
        if not row["a1_passed"] or not row["a2_passed"] or not row["a3_passed"]:
            return pd.Series([5, "individual assignment thresholds not reached"])
        if not row["q_passed"]:
            return pd.Series([5, "individual quiz thresholds not reached"])
        if row["a_total"] < THRESHOLD_ALL_A * MAX_POINTS_ALL_A:
            return pd.Series([5, "total assignment threshold not reached"])
        if row["q_total"] < THRESHOLD_ALL_Q * MAX_POINTS_ALL_Q:
            return pd.Series([5, "total quiz threshold not reached"])
        total = row["a_total"] + row["q_total"]
        # regular grades, no need for special reason
        if total >= 87.5:
            return pd.Series([1, ""])
        if total >= 75:
            return pd.Series([2, ""])
        if total >= 62.5:
            return pd.Series([3, ""])
        if total >= 50:
            return pd.Series([4, ""])
        raise AssertionError("negative grade cases should have already been handled")


if __name__ == "__main__":
    args = util.get_grading_args()
    grader = Python1Grader(args.moodle_file)
    grader.create_grading_file(args.kusss_participants_files, grading_file=args.grading_file)

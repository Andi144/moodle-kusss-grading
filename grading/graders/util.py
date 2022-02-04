import argparse

import pandas as pd


def create_grade(points, max_points, grading: dict = None) -> pd.Series:
    """
    Creates a grade object based on the percentage of achieved points, given the
    absolute ``points`` and the absolute ``max_points``. Which grade is returned
    is determined by the ``grading`` scheme that contains lower percentage thresholds
    for each particular grade from 1 ("Sehr gut"/"Very good") to 4 ("Genügend"/
    "Sufficient"). The grading percentages are checked from best grade (1) to worst
    grade (4) in sequential order, returning the grade that matches first when checking
    whether the percentage of the achieved points is greater or equal than the grading
    percentage, or if nothing matches, the grade 5 ("Nicht genügend"/"Not sufficient")
    is returned. Example:
    
        points = 17
        max_points = 24
        grading = {1: 0.875, 2: 0.75, 3: 0.625, 4: 0.50}
        
        percentage = points / max_points = 17 / 24 = 0.7083333
        check grades from 1 to 4 and return first that matches with percentage >= grading[i],
        or return 5 if none match:
            percentage >= grading[1] ---> 0.7083333 >= 0.875 ---> no match, check next
            percentage >= grading[2] ---> 0.7083333 >= 0.75  ---> no match, check next
            percentage >= grading[3] ---> 0.7083333 >= 0.625 ---> match, return grade 3
    
    The returned object is the one required by ``grader._create_grade_row(row)``, i.e.,
    a pd.Series object with two entries, where the first entry is the grade and the
    second is the reason for this grade. The reason is always the empty string, i.e.,
    there is no particular reason.
    
    :param points: The absolute points that were achieved.
    :param max_points: The absolute maximum points that can be achieved.
    :param grading: A dictionary containing the grading scheme. The keys are the grades
        as integers from 1 (best grade) to 4 (worst grade), and the values are the
        corresponding lower percentage thresholds, i.e., the minimum percentage in order
        to get the respective grades. Specifying an additional key for the grade 5 is
        unnecessary, as this grade is automatically returned if none of the other grades
        match. Default: {1: 0.875, 2: 0.75, 3: 0.625, 4: 0.50}
    :return: A pd.Series object where the first entry is the grade (type: np.int64) and
        the second entry the reason (type: str, i.e., pandas object) for this grade,
        which is always the empty string (i.e., no particular reason).
    """
    if grading is None:
        grading = {1: 0.875, 2: 0.75, 3: 0.625, 4: 0.50}
    total = points / max_points
    if total >= grading[1]:
        return pd.Series([1, ""])
    if total >= grading[2]:
        return pd.Series([2, ""])
    if total >= grading[3]:
        return pd.Series([3, ""])
    if total >= grading[4]:
        return pd.Series([4, ""])
    return pd.Series([5, ""])


def get_grading_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-mf", "--moodle_file", type=str, required=True,
                        help="Moodle CSV export file.")
    parser.add_argument("-kpf", "--kusss_participants_files", type=str, nargs="+", required=True,
                        help="KUSSS participants CSV export files.")
    parser.add_argument("-gf", "--grading_file", type=str, default=None,
                        help="The output CSV file where the grades will be stored.")
    return parser.parse_args()

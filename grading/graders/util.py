import argparse
import re
import warnings
from decimal import Decimal, ROUND_UP

import pandas as pd


def create_grade(points, max_points, grading: dict = None, round_ndec: int = 2) -> pd.Series:
    """
    Creates a grade object based on the percentage of achieved points, given the
    absolute ``points`` and the absolute ``max_points``. Which grade is returned
    is determined by the ``grading`` scheme that contains lower percentage thresholds
    for each particular grade from 1 ("Sehr gut"/"Very good") to 4 ("Genügend"/
    "Sufficient"). The grading percentages are checked from best grade (1) to worst
    grade (4) in sequential order, returning the grade that matches first when checking
    whether the percentage of the achieved points is greater or equal than the grading
    percentage, or if nothing matches, the grade 5 ("Nicht genügend"/"Not sufficient")
    is returned. The percentage is rounded to ``round_ndec`` decimal places (2 by default)
    before checking against the grading thresholds. Example:
    
        points = 17
        max_points = 24
        grading = {1: 0.875, 2: 0.75, 3: 0.625, 4: 0.50}
        
        percentage = points / max_points = 17 / 24 = 0.7083333
        percentage rounded to 2 (default) decimal places = 0.71
        check grades from 1 to 4 and return first that matches with percentage >= grading[i],
        or return 5 if none match:
            percentage >= grading[1] ---> 0.71 >= 0.875 ---> no match, check next
            percentage >= grading[2] ---> 0.71 >= 0.75  ---> no match, check next
            percentage >= grading[3] ---> 0.71 >= 0.625 ---> match, return grade 3
    
    The returned object is the one required by ``grader._create_grade_row(row)``, i.e.,
    a pd.Series object with two entries, where the first entry is the grade and the
    second is the reason for this grade. The reason is always the empty string for all
    grades specified in ``grading``, i.e., there is no particular reason, and for the
    grade 5, the reason is "total threshold not reached".
    
    :param points: The absolute points that were achieved.
    :param max_points: The absolute maximum points that can be achieved.
    :param grading: A dictionary containing the grading scheme. The keys are the grades
        as integers from 1 (best grade) to 4 (worst grade), and the values are the
        corresponding lower percentage thresholds, i.e., the minimum percentage in order
        to get the respective grades. Specifying an additional key for the grade 5 is
        unnecessary, as this grade is automatically returned if none of the other grades
        match. Default: {1: 0.875, 2: 0.75, 3: 0.625, 4: 0.50}
    :param round_ndec: The number of decimal places for rounding the calculated percentage.
        Default: 2
    :return: A pd.Series object where the first entry is the grade (type: np.int64) and
        the second entry the reason (type: str, i.e., pandas object) for this grade.
    """
    # TODO: better parameterization: "grading" should be an arbitrarily sized sequence
    #  where each entry contains: [0] the grade, [1] the lower threshold, [2] the reason;
    #  this sequence is then simply checked sequentially (possibly with a parameterized
    #  default value if none of "grading" match, or, raising some exception)
    if grading is None:
        grading = {1: 0.875, 2: 0.75, 3: 0.625, 4: 0.50}
    total = Decimal(points) / max_points
    total = total.quantize(Decimal(".01"), rounding=ROUND_UP)
    if total >= grading[1]:
        return pd.Series([1, ""])
    if total >= grading[2]:
        return pd.Series([2, ""])
    if total >= grading[3]:
        return pd.Series([3, ""])
    if total >= grading[4]:
        return pd.Series([4, ""])
    return pd.Series([5, "total threshold not reached"])


def check_matr_id_format(s: pd.Series):
    """
    Checks if the specified pd.Series object contains matriculation IDs in the
    following format: "k<MATR_ID>", where <MATR_ID> is an 8-digit number. No
    other leading or trailing characters are allowed. If an invalid format is
    encountered, a ValueError is raised.
    
    :param s: The pd.Series that contains matriculation IDs.
    """
    if s.dtype != object or s.apply(lambda x: re.match(r"k\d{8}$", x) is None).any():
        raise ValueError(f"series does not contain valid ('k<8-digit-matr-id>') matriculation IDs: {s}")


def get_grading_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-mf", "--moodle_file", type=str, required=True,
                        help="Moodle CSV export file.")
    parser.add_argument("-kpf", "--kusss_participants_files", type=str, nargs="+", required=True,
                        help="KUSSS participants CSV export files.")
    parser.add_argument("-gf", "--grading_file", type=str, default=None,
                        help="The output CSV file where the grades will be stored.")
    return parser


def args_sanity_check(moodle_file: str, kusss_participants_files: list, common_expectation: str = None,
                      moodle_file_expectation: str = None, kusss_participants_file_expectation: str = None,
                      raise_error: bool = False):
    """
    Performs a simple sanity check based on whether the string ``xyz_expectation`` is contained
    in ``xyz``, e.g., if ``moodle_file_expectation`` is contained in ``moodle_file``. This function
    is useful to quickly check if the script was potentially called with incorrect arguments.
    
    :param moodle_file: The name of the Moodle file (see function ``get_grading_args_parser``).
    :param kusss_participants_files: The names of the KUSSS participants files (see function
        ``get_grading_args_parser``).
    :param common_expectation: What to expect in ``moodle_file`` as well as in each name of the
        files in ``kusss_participants_files``. If None, no check is performed. Default: None
    :param moodle_file_expectation: What to expect in ``moodle_file``. If None, no check is
        performed. Default: None
    :param kusss_participants_file_expectation: What to expect in each name of the files in
        ``kusss_participants_files``. If None, no check is performed. Default: None
    :param raise_error: If True, raise a ValueError, otherwise, only a warning is issued.
        Default: False
    """
    
    def expectation_check(expectation, actual):
        if expectation is not None and expectation not in actual:
            msg = f"'{expectation}' does not appear in '{actual}', perhaps wrong script argument?"
            if raise_error:
                raise ValueError(msg)
            else:
                warnings.warn(msg)
    
    if common_expectation is None and moodle_file_expectation is None and kusss_participants_file_expectation is None:
        warnings.warn("'args_sanity_check' is called with all expectation parameters set to None, which is a no-op")
    
    expectation_check(common_expectation, moodle_file)
    expectation_check(moodle_file_expectation, moodle_file)
    for kpf in kusss_participants_files:
        expectation_check(common_expectation, kpf)
        expectation_check(kusss_participants_file_expectation, kpf)

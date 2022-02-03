import argparse


def get_grading_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-mf", "--moodle_file", type=str, required=True,
                        help="Moodle CSV export file.")
    parser.add_argument("-kpf", "--kusss_participants_files", type=str, nargs="+", required=True,
                        help="KUSSS participants CSV export files.")
    parser.add_argument("-gf", "--grading_file", type=str, default=None,
                        help="The output CSV file where the grades will be stored.")
    return parser.parse_args()

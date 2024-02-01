import argparse

import pandas as pd


def print_counts_by_skz(participant_files: list[str], grading_files: list[str]):
    dfs = [pd.read_csv(pf, sep=";", header=0, names=["id", "skz"]) for pf in participant_files]
    pdf = pd.concat(dfs).drop_duplicates()
    # merge all files and keep last entry in case of duplicates = most recent entry if list is ordered
    dfs = [pd.read_csv(gf, sep=";", names=["id", "skz", "grade", "extInfo", "intInfo"]) for gf in grading_files]
    gdf = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["id", "skz"], keep="last")

    print(f"===== Number of registered students (total = {len(pdf)}) grouped by SKZ =====")
    p_counts = pdf.groupby("skz").count()
    p_counts.columns = ["count"]
    p_counts.sort_values("count", inplace=True)
    p_counts["percent"] = 100 * p_counts["count"] / p_counts["count"].sum()
    print(p_counts)
    
    print(f"\n===== Number of graded students (total = {len(gdf)}) grouped by SKZ =====")
    g_counts = gdf.groupby("skz")[["id"]].count()
    g_counts.columns = ["count"]
    g_counts.sort_values("count", inplace=True)
    g_counts["percent"] = 100 * g_counts["count"] / g_counts["count"].sum()
    print(g_counts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--participant_files", nargs="+", type=str, required=True,
                        help="The KUSSS participant CSV files. Duplicate entries are removed automatically.")
    parser.add_argument("--grading_files", nargs="+", type=str, required=True,
                        help="The output CSV files where the grades are stored. In case of duplicate entries, "
                             "the file specified last takes precedence, i.e., the order of this list matters.")
    args = parser.parse_args()
    print_counts_by_skz(args.participant_files, args.grading_files)

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def chunks(seq, n):
    """Yield successive n-sized chunks from seq."""
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def line_breaking(s: str, line_len: int, max_len: int = None, max_line_breaks: int = None):
    if line_len <= 0:
        raise ValueError(f"'line_len' must be > 0 (was {line_len})")
    if max_len is not None and max_len <= 0:
        raise ValueError(f"'max_len' must be > 0 (was {max_len})")
    if max_line_breaks is not None and max_line_breaks <= 0:
        raise ValueError(f"'max_line_breaks' must be > 0 (was {max_line_breaks})")
    
    words = s.split(" ")
    split_words = []
    
    for word in words:
        if len(word) > line_len:
            splits = [c for c in chunks(word, line_len - 1)]  # -1 because of the additional splitting dash character
            for i, split in enumerate(splits):
                if i == len(splits) - 1:
                    split_words.append(split)
                else:
                    split_words.append(split + "-")
        else:
            split_words.append(word)
    
    line = ""
    lines = []
    skipped_lines = False
    
    for word in split_words:
        if len(line) == 0:
            line += word
        elif len(line) + 1 + len(word) > line_len:  # +1 because of the separating space character
            if max_line_breaks is None or len(lines) < max_line_breaks:
                lines.append(line)
                line = word
            else:
                skipped_lines = True
                break
        else:
            line += " " + word
    lines.append(line)
    
    skip_indicator = "..."
    if skipped_lines:
        # this means we left the loop early and skipped the remaining words
        last_line = lines[-1]
        diff = len(last_line) + len(skip_indicator) - line_len
        if diff > 0:
            last_line = last_line[:-diff] + skip_indicator
        else:
            last_line += skip_indicator
        lines[-1] = last_line
    
    new_s = "\n".join(lines)
    if max_len is not None and len(new_s) > max_len:
        # TODO: should leave loop early when max_len is reached instead of processing everything and then slicing
        return new_s[:max_len - len(skip_indicator)] + skip_indicator
    return new_s


def plot_grade_hist(grading_files: list[str], skz: str = None):
    # merge all files and keep last entry in case of duplicates = most recent entry if list is ordered
    dfs = [pd.read_csv(gf, sep=";", names=["id", "skz", "grade", "extInfo", "intInfo"]) for gf in grading_files]
    df = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["id", "skz"], keep="last")
    if skz is not None:
        df = df[df["skz"] == skz]
        if len(df) == 0:
            raise ValueError(f"no entries found for specified SKZ = {skz}")
    df["reason"] = ": " + df["extInfo"]  # only adds ": " for non-NaN values
    df["reason"].fillna("", inplace=True)
    df["grade_detail"] = (df["grade"].astype(str) + df["reason"]).apply(line_breaking, line_len=20, max_line_breaks=2)
    df.sort_values("grade_detail", inplace=True)
    
    def _plot_grade_hist(ax: plt.Axes, x: str, rotate: float = None):
        grade_is_str = df[x].dtype == object
        ax_twin = ax.twinx()
        sns.histplot(data=df, x=x, discrete=True, ax=ax, color="bisque")
        if not grade_is_str:
            ax.set_xticks(range(1, 6))
        counts = [len(group_df) for _, group_df in df.groupby(x)]
        # shift count labels by 1% of max (so there is some space between the bars and the labels)
        y_offset = 0.01 * max(counts)
        for i, (grade, group_df) in enumerate(df.groupby(x)):
            x_pos = i if grade_is_str else grade
            y_pos = len(group_df) + y_offset
            ax.text(x_pos, y_pos, f"{len(group_df)} ({len(group_df) / len(df):.1%})", ha="center")
        max_percent = max([100 * c / len(df) for c in counts])
        # plot an invisible vertical line to automatically get the correct y-ticks
        x_pos = np.mean(ax.get_xticks())
        ax_twin.plot([x_pos, x_pos], [0, max_percent], alpha=0)
        ax_twin.set_ylim(0, ax_twin.get_ylim()[1])
        ax_twin.set_ylabel("Percent")
        if rotate is not None:
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        ax.set_xlabel("")
    
    # type hints to enable PyCharm suggestions and code completion
    fig: plt.Figure
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(14, 6))
    _plot_grade_hist(ax1, "grade")
    _plot_grade_hist(ax2, "grade_detail", rotate=45)
    title = "\n".join([os.path.split(os.path.dirname(gf))[1] + "/" + os.path.basename(gf) for gf in grading_files])
    title += f"\nGrades (count = {len(df)}; median = {df['grade'].median():.1f}; mean = {df['grade'].mean():.2f})"
    if skz is not None:
        title += f" for SKZ = {skz}"
    fig.suptitle(title)
    fig.tight_layout()
    
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("grading_files", nargs="+", type=str,
                        help="The output CSV files where the grades are stored. In case of duplicate entries, "
                             "the file specified last takes precedence, i.e., the order of this list matters.")
    parser.add_argument("--skz", type=int,
                        help="Restrict the output to only include students with this study identification (SKZ).")
    args = parser.parse_args()
    plot_grade_hist(args.grading_files, args.skz)

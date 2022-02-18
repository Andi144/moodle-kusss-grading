import argparse
import os

import matplotlib.pyplot as plt
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


def plot_grade_hist(grading_file: str):
    df = pd.read_csv(grading_file, sep=";", names=["id", "skz", "grade", "reason"])
    df["reason"] = ": " + df["reason"]  # only adds ": " for non-NaN values
    df["reason"].fillna("", inplace=True)
    df["grade_detail"] = (df["grade"].astype(str) + df["reason"]).apply(line_breaking, line_len=20, max_line_breaks=2)
    df.sort_values("grade_detail", inplace=True)
    
    # type hints to enable PyCharm suggestions and code completion
    fig: plt.Figure
    ax1: plt.Axes
    ax2: plt.Axes
    
    fig, (ax1, ax3) = plt.subplots(ncols=2, figsize=(14, 6))
    
    ax2 = ax1.twinx()
    sns.histplot(data=df, x="grade", discrete=True, ax=ax1, color="bisque")
    sns.histplot(data=df, x="grade", discrete=True, ax=ax2, color="bisque", stat="percent")
    ax1.grid(axis="y", linestyle="--", color="gray")
    ax2.grid(axis="y", linestyle="--", color="coral")
    ax1.tick_params(axis="y", colors="gray")
    ax2.tick_params(axis="y", colors="coral")
    ax1.yaxis.label.set_color("gray")
    ax2.yaxis.label.set_color("coral")
    ax1.set_title(f"Grade (median = {df['grade'].median():.1f}; mean = {df['grade'].mean():.2f})")
    ax1.set_xlabel("")
    
    ax4 = ax3.twinx()
    sns.histplot(data=df, x="grade_detail", discrete=True, ax=ax3, color="bisque")
    sns.histplot(data=df, x="grade_detail", discrete=True, ax=ax4, color="bisque", stat="percent")
    ax3.grid(axis="y", linestyle="--", color="gray")
    ax4.grid(axis="y", linestyle="--", color="coral")
    ax3.tick_params(axis="y", colors="gray")
    ax4.tick_params(axis="y", colors="coral")
    ax3.yaxis.label.set_color("gray")
    ax4.yaxis.label.set_color("coral")
    plt.setp(ax3.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    ax3.set_title("Detailed Grade")
    ax3.set_xlabel("")
    
    fig.suptitle(os.path.basename(os.path.splitext(grading_file)[0]))
    fig.tight_layout()
    
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("grading_file", type=str, help="The output CSV file where the grades are stored.")
    args = parser.parse_args()
    plot_grade_hist(args.grading_file)

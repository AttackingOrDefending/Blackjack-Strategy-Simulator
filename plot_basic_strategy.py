"""Plots basic strategy in clean graphs (without expected profit)."""
from utils import list_range_str
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv
import argparse


def plot_csv(filename: str) -> None:
    """
    Plot the basic strategy.

    :param filename: The file where the basic strategy is stored.
    """
    no_ace_table = [["" for _ in range(12)] for _ in range(22)]
    ace_table = [["" for _ in range(12)] for _ in range(22)]
    split_table = [["" for _ in range(12)] for _ in range(12)]
    with open(filename, newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            identifier = row[0]
            hand_value = int(identifier[1:])
            column = 1
            if identifier.startswith("n"):
                for dealer_up_card in range(2, 12):
                    no_ace_table[hand_value][dealer_up_card] = row[column]
                    column += 1
            elif identifier.startswith("a"):
                for dealer_up_card in range(2, 12):
                    ace_table[hand_value][dealer_up_card] = row[column]
                    column += 1
            elif identifier.startswith("s"):
                for dealer_up_card in range(2, 12):
                    split_table[hand_value][dealer_up_card] = row[column]
                    column += 1
            else:
                raise ValueError

    fig, ax = plt.subplots(dpi=200)

    fig.patch.set_visible(False)
    fig.set_size_inches(6, 4.8)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.yaxis.set_label_coords(-0.12, 0)

    no_ace_colors: list[list[str]] = [[] for _ in range(18)]
    for hand_value in range(4, 22):
        for dealer_up_card in range(2, 12):
            if no_ace_table[hand_value][dealer_up_card].startswith("s"):
                no_ace_colors[hand_value - 4].append("y")
            elif no_ace_table[hand_value][dealer_up_card].startswith("h"):
                no_ace_colors[hand_value - 4].append("w")
            elif no_ace_table[hand_value][dealer_up_card].startswith("d"):
                no_ace_colors[hand_value - 4].append("g")
            elif no_ace_table[hand_value][dealer_up_card].startswith("p"):
                no_ace_colors[hand_value - 4].append("c")
            elif no_ace_table[hand_value][dealer_up_card].startswith("u"):
                no_ace_colors[hand_value - 4].append("r")
            elif no_ace_table[hand_value][dealer_up_card].startswith("i"):
                no_ace_colors[hand_value - 4].append("maroon")

    no_ace_table = list(map(lambda table_row: list(map(lambda action: action.capitalize(), table_row[2:])), no_ace_table[4:]))

    table = ax.table(cellText=no_ace_table, cellColours=no_ace_colors, colLabels=list_range_str(2, 12),
                     rowLabels=list_range_str(4, 22), loc='center', cellLoc='center')
    table.scale(1, 1.1)

    ax.set_title("Hard totals")
    ax.set_xlabel("Dealer Up Card")
    ax.set_ylabel("Player Cards")
    ax.xaxis.tick_top()

    handles = [patches.Rectangle((0, 0), .1, .1, facecolor=color, edgecolor='k', lw=.6)
               for color in ["y", "w", "g", "c", "r", "maroon"]]
    ax.legend(handles, ["Stand", "Hit", "Double", "Split", "Surrender", "Insurance"], fontsize="xx-small",
              bbox_to_anchor=(0.5, -0.14), ncol=6, loc=8)

    plt.tight_layout()

    fig2, ax2 = plt.subplots(dpi=200)

    fig2.patch.set_visible(False)
    fig2.set_size_inches(6, 3.2)
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.yaxis.set_label_coords(-0.12, 0)

    ace_colors: list[list[str]] = [[] for _ in range(10)]
    for hand_value in range(12, 22):
        for dealer_up_card in range(2, 12):
            if ace_table[hand_value][dealer_up_card].startswith("s"):
                ace_colors[hand_value - 12].append("y")
            elif ace_table[hand_value][dealer_up_card].startswith("h"):
                ace_colors[hand_value - 12].append("w")
            elif ace_table[hand_value][dealer_up_card].startswith("d"):
                ace_colors[hand_value - 12].append("g")
            elif ace_table[hand_value][dealer_up_card].startswith("p"):
                ace_colors[hand_value - 12].append("c")
            elif ace_table[hand_value][dealer_up_card].startswith("u"):
                ace_colors[hand_value - 12].append("r")
            elif ace_table[hand_value][dealer_up_card].startswith("i"):
                ace_colors[hand_value - 12].append("maroon")

    ace_table = list(map(lambda table_row: list(map(lambda action: action.capitalize(), table_row[2:])), ace_table[12:]))

    row_labels = ["A,A"] + [f"A,{card}" for card in range(2, 11)]
    table = ax2.table(cellText=ace_table, cellColours=ace_colors, colLabels=list_range_str(2, 12),
                      rowLabels=row_labels, loc='center', cellLoc='center')
    table.scale(1, 1.25)

    ax2.set_title("Soft totals")
    ax2.set_xlabel("Dealer Up Card")
    ax2.set_ylabel("Player Cards")
    ax2.xaxis.tick_top()

    handles = [patches.Rectangle((0, 0), .1, .1, facecolor=color, edgecolor='k', lw=.6)
               for color in ["y", "w", "g", "c", "r", "maroon"]]
    ax2.legend(handles, ["Stand", "Hit", "Double", "Split", "Surrender", "Insurance"], fontsize="xx-small",
               bbox_to_anchor=(0.5, -0.23), ncol=6, loc=8)

    plt.tight_layout()

    fig3, ax3 = plt.subplots(dpi=200)

    fig3.patch.set_visible(False)
    fig3.set_size_inches(6, 3.2)
    ax3.set_yticklabels([])
    ax3.set_xticklabels([])
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    ax3.spines['left'].set_visible(False)
    ax3.yaxis.set_label_coords(-0.12, 0)

    split_colors: list[list[str]] = [[] for _ in range(10)]
    for card in range(2, 12):
        for dealer_up_card in range(2, 12):
            if split_table[card][dealer_up_card].startswith("s"):
                split_colors[card - 2].append("y")
            elif split_table[card][dealer_up_card].startswith("h"):
                split_colors[card - 2].append("w")
            elif split_table[card][dealer_up_card].startswith("d"):
                split_colors[card - 2].append("g")
            elif split_table[card][dealer_up_card].startswith("p"):
                split_colors[card - 2].append("c")
            elif split_table[card][dealer_up_card].startswith("u"):
                split_colors[card - 2].append("r")
            elif split_table[card][dealer_up_card].startswith("i"):
                split_colors[card - 2].append("maroon")

    split_table = list(map(lambda table_row: list(map(lambda action: action.capitalize(), table_row[2:])), split_table[2:]))

    row_labels = [f"{card},{card}" for card in range(2, 11)] + ["A,A"]

    table = ax3.table(cellText=split_table, cellColours=split_colors, colLabels=list_range_str(2, 12),
                      rowLabels=row_labels, loc='center', cellLoc='center')
    table.scale(1, 1.25)

    ax3.set_title("Pair Splitting")
    ax3.set_xlabel("Dealer Up Card")
    ax3.set_ylabel("Player Cards")
    ax3.xaxis.tick_top()

    handles = [patches.Rectangle((0, 0), .1, .1, facecolor=color, edgecolor='k', lw=.6)
               for color in ["y", "w", "g", "c", "r", "maroon"]]
    ax3.legend(handles, ["Stand", "Hit", "Double", "Split", "Surrender", "Insurance"], fontsize="xx-small",
               bbox_to_anchor=(0.5, -0.23), ncol=6, loc=8)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Plot Basic Strategy',
                                     description='Plot basic strategy to clean and easy to understand table.')
    parser.add_argument("-f", "--filename", help='The filename where the basic strategy is stored.', required=True)
    args = parser.parse_args()

    plot_csv(args.filename)

"""The three visualizations defined in the design spec, section 6.

Reads the query results in output/queries/ and writes PNGs to output/charts/.
Run after analyze.py.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # no GUI needed; write straight to file
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config

# Colour-blind-safe, and ordered so "good" outcomes sit at the bottom of the stack.
DISPOSITIONS = [
    ("completion_rate", "Completed", "#2E7D32"),
    ("transfer_out_rate", "Transferred out", "#1565C0"),
    ("still_enrolled_rate", "Still enrolled", "#F9A825"),
    ("unknown_outcome_rate", "Outcome unknown", "#9E9E9E"),
]

COHORT_YEAR = "2015-16"    # when the OM cohort entered
CURRENT_YEAR = "2023-24"   # most recent cost data


def _label(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["label"] = df.unitid.map(config.SHORT_NAMES)
    df["sector"] = df.iclevel.map({1: "Four-year", 2: "Two-year"})
    return df


def viz1_outcomes() -> None:
    """Stacked dispositions per institution, with completion-or-transfer marked."""
    df = _label(pd.read_csv(config.QUERIES / "q1.csv"))
    df = df.sort_values(["iclevel", "completion_rate"], ascending=[True, False])

    fig, ax = plt.subplots(figsize=(11, 6.5))
    bottom = pd.Series(0.0, index=df.index)
    for col, name, colour in DISPOSITIONS:
        ax.bar(df.label, df[col], bottom=bottom, label=name, color=colour,
               edgecolor="white", linewidth=0.8)
        bottom += df[col]

    # Mark where completion-or-transfer lands on each bar.
    for x, (_, row) in enumerate(df.iterrows()):
        ax.plot([x - 0.42, x + 0.42],
                [row.completion_or_transfer_rate] * 2,
                color="black", linewidth=2, linestyle="--", zorder=5)
        ax.annotate(f"{row.completion_or_transfer_rate:.0%}",
                    (x, row.completion_or_transfer_rate),
                    textcoords="offset points", xytext=(0, 5),
                    ha="center", fontsize=9, fontweight="bold", zorder=6)

    ax.set_ylim(0, 1)
    ax.set_ylabel("Share of entering cohort")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_title(
        "Eight-year outcomes for first-time, full-time entering students\n"
        "IPEDS Outcome Measures, 2023 final release. "
        "Dashed line = completed or transferred.",
        fontsize=12, pad=14,
    )
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(config.CHARTS / "1_outcomes.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def viz2_cost() -> None:
    """Current living-cost composition, plus the full eleven-year trend."""
    series = _label(pd.read_csv(config.QUERIES / "q2.csv"))
    current = series[series.academic_year == CURRENT_YEAR].sort_values("living_cost_total")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    ax1.barh(current.label, current.food_housing, color="#1565C0", label="Food & housing")
    ax1.barh(current.label, current.other_expenses, left=current.food_housing,
             color="#90CAF9", label="Other expenses")
    for y, (_, row) in enumerate(current.iterrows()):
        ax1.annotate(f"${row.living_cost_total:,.0f}",
                     (row.living_cost_total, y), xytext=(6, 0),
                     textcoords="offset points", va="center", fontsize=9)
    ax1.set_xlabel("Annual living expenses (USD)")
    ax1.set_title(f"Cost of attendance: living expenses, {CURRENT_YEAR}\n"
                  "Off campus, not with family. Excludes tuition and fees.",
                  fontsize=11)
    ax1.legend(frameon=False, loc="lower right")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.set_xlim(0, current.living_cost_total.max() * 1.18)

    years = sorted(series.academic_year.unique())
    for label, grp in series.groupby("label"):
        grp = grp.set_index("academic_year").reindex(years)
        ax2.plot(years, grp.living_cost_total, marker="o", markersize=4,
                 linewidth=2, label=label)
    ax2.axvline(years.index(COHORT_YEAR), color="black", linestyle=":", linewidth=1.5)
    # Anchored to the baseline, not the top: the outlier note below occupies the
    # upper-left corner and the two labels would otherwise overlap.
    ax2.annotate("cohort enrolled", (years.index(COHORT_YEAR), ax2.get_ylim()[0]),
                 xytext=(6, 12), textcoords="offset points",
                 fontsize=9, style="italic")
    ax2.set_ylabel("Living expenses (USD)")
    ax2.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    # Flag the 2013-14 Arkansas Northeastern figure rather than dropping it: a 43%
    # single-year fall is a reporting artifact, not a real change in local costs.
    outlier = series[(series.label == "Ark. Northeastern")
                     & (series.academic_year == "2013-14")]
    if not outlier.empty:
        value = outlier.living_cost_total.iloc[0]
        ax2.annotate("suspected reporting error\n(43% fall the following year)",
                     (0, value), xytext=(28, -6), textcoords="offset points",
                     fontsize=8, style="italic", color="#B71C1C",
                     arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=1))

    ax2.set_title("Cost of attendance: living expenses, 2013-14 to 2023-24\n"
                  "Institution-reported. Flat stretches indicate estimates not "
                  "updated annually.", fontsize=11)
    ax2.legend(frameon=False, fontsize=8, ncol=2)
    ax2.tick_params(axis="x", rotation=45, labelsize=8)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(config.CHARTS / "2_cost_of_living.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def viz3_combined() -> None:
    """Completion against living cost, at two different cost years.

    The two panels use identical completion rates and differ only in which year's
    cost data supplies the x-axis. They disagree about the direction of the
    relationship, which is the point: at n=5 the apparent association is an
    artifact of an arbitrary choice, not a finding. No trend line is fitted.
    """
    df = _label(pd.read_csv(config.QUERIES / "q3.csv"))

    panels = [
        ("living_cost_2015_16", f"Living expenses when the cohort enrolled ({COHORT_YEAR})"),
        ("living_cost_2023_24", f"Living expenses today ({CURRENT_YEAR})"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), sharey=True)

    for ax, (cost_col, panel_title) in zip(axes, panels):
        r = df[cost_col].corr(df.completion_rate)
        for _, row in df.iterrows():
            four_year = row.iclevel == 1
            ax.scatter(row[cost_col], row.completion_rate, s=190, zorder=3,
                       marker="o" if four_year else "s",
                       color="#2E7D32" if four_year else "#1565C0",
                       edgecolor="white", linewidth=1.5)
            ax.annotate(f"{row.label}\n{row.completion_rate:.1%}",
                        (row[cost_col], row.completion_rate),
                        textcoords="offset points", xytext=(10, -4), fontsize=8.5)
        ax.set_xlabel("Cost of attendance: annual living expenses (USD)")
        ax.xaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}k")
        ax.set_xlim(df[cost_col].min() * 0.90, df[cost_col].max() * 1.16)
        ax.grid(alpha=0.25, zorder=0)
        ax.spines[["top", "right"]].set_visible(False)
        direction = "higher cost, lower completion" if r < 0 else "higher cost, higher completion"
        ax.set_title(f"{panel_title}\nr = {r:+.2f}  ({direction})", fontsize=11)

    axes[0].set_ylabel("Eight-year completion rate")
    axes[0].yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    axes[0].set_ylim(0.20, 0.68)

    fig.suptitle(
        "The same institutions, the same completion rates — opposite conclusions\n"
        "Circles = four-year, squares = two-year. Only the cost year differs between "
        "panels.\nNo trend fitted: at n=5 the correlation is an artifact of which year "
        "is chosen, not a finding.",
        fontsize=12.5, y=1.06,
    )
    fig.tight_layout()
    fig.savefig(config.CHARTS / "3_combined.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def viz4_cost_shift() -> None:
    """Dumbbell chart: both cost years and completion in a single view.

    Each institution is one horizontal segment running from its 2015-16 living
    expenses to its 2023-24 figure, held at its (single, unchanging) completion
    rate. Completion is a property of ONE cohort -- students who entered in
    2015-16 and were measured in 2023 -- so it has no time series of its own.
    Only the horizontal position moves, which is precisely why the correlation
    between cost and completion reverses sign depending on the year chosen.
    """
    df = _label(pd.read_csv(config.QUERIES / "q3.csv")).sort_values("completion_rate")

    fig, ax = plt.subplots(figsize=(12, 7))
    for _, row in df.iterrows():
        four_year = row.iclevel == 1
        colour = "#2E7D32" if four_year else "#1565C0"
        y = row.completion_rate

        ax.annotate(
            "", xy=(row.living_cost_2023_24, y), xytext=(row.living_cost_2015_16, y),
            arrowprops=dict(arrowstyle="-|>", color=colour, lw=2, alpha=0.55),
        )
        ax.scatter(row.living_cost_2015_16, y, s=110, zorder=3, color="white",
                   edgecolor=colour, linewidth=2,
                   marker="o" if four_year else "s")
        ax.scatter(row.living_cost_2023_24, y, s=150, zorder=3, color=colour,
                   edgecolor="white", linewidth=1.5,
                   marker="o" if four_year else "s")

        change = (row.living_cost_2023_24 - row.living_cost_2015_16) / row.living_cost_2015_16
        ax.annotate(f"{row.label} — {row.completion_rate:.1%} completion  (+{change:.0%})",
                    (row.living_cost_2023_24, y), textcoords="offset points",
                    xytext=(12, -3), fontsize=9, va="center")

    ax.set_xlabel("Cost of attendance: annual living expenses (USD)")
    ax.set_ylabel("Eight-year completion rate (single cohort, unchanging)")
    ax.xaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}k")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_xlim(df.living_cost_2015_16.min() * 0.92,
                df.living_cost_2023_24.max() * 1.30)
    ax.set_ylim(0.24, 0.63)
    ax.grid(alpha=0.25, axis="x", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(
        "Living expenses moved; completion did not\n"
        "Hollow marker = 2015-16 (cohort entry), solid = 2023-24. Circles = four-year, "
        "squares = two-year.\nCompletion describes one cohort and has no time series, so "
        "each institution moves only sideways.",
        fontsize=12, pad=14,
    )
    fig.tight_layout()
    fig.savefig(config.CHARTS / "4_cost_shift.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def viz5_cohort_trend() -> None:
    """Completion across eight entering cohorts, 2009-10 to 2016-17."""
    df = _label(pd.read_csv(config.QUERIES / "q5.csv"))
    years = sorted(df.cohort_year.unique())

    fig, ax = plt.subplots(figsize=(12, 6.5))
    for label, grp in df.groupby("label"):
        grp = grp.sort_values("cohort_year")
        four_year = grp.iclevel.iloc[0] == 1
        ax.plot(grp.cohort_year, grp.completion_pct, marker="o", markersize=6,
                linewidth=2.5 if four_year else 2,
                linestyle="-" if four_year else "--",
                label=f"{label} ({'4yr' if four_year else '2yr'})")
        last = grp.iloc[-1]
        change = last.completion_pct - grp.iloc[0].completion_pct
        ax.annotate(f"{label}  {last.completion_pct:.1f}%  ({change:+.1f} pts)",
                    (len(years) - 1, last.completion_pct),
                    textcoords="offset points", xytext=(10, -3), fontsize=9,
                    va="center")

    ax.set_xlabel("Entering cohort (academic year)")
    ax.set_ylabel("Eight-year completion rate")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.set_xlim(-0.3, len(years) + 2.6)
    ax.grid(alpha=0.25, axis="y")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(
        "Completion improved at every institution, and most at the community colleges\n"
        "Each point is a separate entering cohort measured at its own eight-year "
        "status point.\nSolid = four-year, dashed = two-year.",
        fontsize=12, pad=14,
    )
    fig.tight_layout()
    fig.savefig(config.CHARTS / "5_cohort_trend.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def viz6_within_institution() -> None:
    """Cost at entry against completion, within each institution across cohorts.

    Demonstrates Simpson's paradox: pooled across institutions the correlation is
    negative, but within four of the five it is positive. Neither is evidence that
    cost affects completion -- within institutions both variables simply trend
    upward over a decade.
    """
    df = _label(pd.read_csv(config.QUERIES / "q6.csv")).dropna(subset=["living_cost_at_entry"])
    labels = sorted(df.label.unique())

    fig, axes = plt.subplots(1, len(labels), figsize=(18, 4.6), sharey=True)
    for ax, label in zip(axes, labels):
        grp = df[df.label == label].sort_values("cohort_year")
        four_year = grp.iclevel.iloc[0] == 1
        colour = "#2E7D32" if four_year else "#1565C0"
        r = grp.living_cost_at_entry.corr(grp.completion_pct)

        ax.plot(grp.living_cost_at_entry, grp.completion_pct,
                color=colour, alpha=0.35, linewidth=1.2, zorder=2)
        ax.scatter(grp.living_cost_at_entry, grp.completion_pct,
                   c=range(len(grp)), cmap="viridis", s=70, zorder=3,
                   edgecolor="white", linewidth=1)
        ax.set_title(f"{label}\nr = {r:+.2f}  (n={len(grp)})", fontsize=10.5)
        ax.set_xlabel("Living expenses at entry")
        # Narrow ranges need one decimal, or every tick rounds to the same "$15k".
        ax.xaxis.set_major_locator(MaxNLocator(3))
        ax.xaxis.set_major_formatter(lambda v, _: f"${v/1000:,.1f}k")
        ax.tick_params(axis="x", labelsize=8.5)
        ax.grid(alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("Eight-year completion rate")
    axes[0].yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")

    pooled = df.living_cost_at_entry.corr(df.completion_pct)
    fig.suptitle(
        f"Within institutions the correlation is mostly positive; pooled across them it is "
        f"negative (r = {pooled:+.2f})\n"
        "Simpson's paradox. Neither figure is evidence about cost: within each institution, "
        "expenses and completion\nsimply both rose over the decade. Marker colour runs dark "
        "(2009-10) to light (2016-17).",
        fontsize=12, y=1.14,
    )
    fig.tight_layout()
    fig.savefig(config.CHARTS / "6_within_institution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def viz7_trajectory() -> None:
    """Two-dimensional dumbbell: where each institution started and finished.

    The single-cohort version of this chart (viz4) could only move horizontally,
    because completion was one fixed number per institution. With eight cohorts
    both axes move, so each institution traces a genuine trajectory from its first
    cohort to its last.

    Start points differ: UT Martin reported no living expenses before 2012-13, so
    its trajectory begins there rather than at 2009-10. The label states each
    institution's actual span rather than implying a common baseline.
    """
    df = _label(pd.read_csv(config.QUERIES / "q6.csv")).dropna(subset=["living_cost_at_entry"])

    # Manual label placement: Murray State, Ark. Northeastern and UT Martin finish in
    # a tight cluster. Ark. Northeastern is labelled to the LEFT of its marker --
    # placing it right put the text underneath UT Martin's marker, which obscured a
    # digit of its completion figure.
    # (dx, dy, horizontal alignment)
    OFFSETS = {
        "Murray State": (16, 10, "left"),
        "Ark. Northeastern": (-18, 16, "right"),
        "UT Martin": (16, -16, "left"),
        "Dyersburg State": (16, 0, "left"),
        "Jackson State": (16, 0, "left"),
    }

    fig, ax = plt.subplots(figsize=(12.5, 7.5))
    for label, grp in df.groupby("label"):
        grp = grp.sort_values("cohort_year")
        start, end = grp.iloc[0], grp.iloc[-1]
        four_year = start.iclevel == 1
        colour = "#2E7D32" if four_year else "#1565C0"
        marker = "o" if four_year else "s"

        # Faint trace of every intermediate cohort, so the path is visible and the
        # arrow is not mistaken for a straight-line journey.
        ax.plot(grp.living_cost_at_entry, grp.completion_pct,
                color=colour, alpha=0.16, linewidth=1.0, zorder=2)
        ax.annotate("", xy=(end.living_cost_at_entry, end.completion_pct),
                    xytext=(start.living_cost_at_entry, start.completion_pct),
                    arrowprops=dict(arrowstyle="-|>", color=colour, lw=2.2, alpha=0.6))
        ax.scatter(start.living_cost_at_entry, start.completion_pct, s=115, zorder=3,
                   color="white", edgecolor=colour, linewidth=2, marker=marker)
        ax.scatter(end.living_cost_at_entry, end.completion_pct, s=165, zorder=3,
                   color=colour, edgecolor="white", linewidth=1.5, marker=marker)

        d_completion = end.completion_pct - start.completion_pct
        d_cost = (end.living_cost_at_entry - start.living_cost_at_entry) / start.living_cost_at_entry
        dx, dy, ha = OFFSETS.get(label, (16, 0, "left"))
        ax.annotate(
            f"{label}\n{start.cohort_year} → {end.cohort_year}\n"
            f"completion {d_completion:+.1f} pts, cost {d_cost:+.0%}",
            (end.living_cost_at_entry, end.completion_pct),
            textcoords="offset points", xytext=(dx, dy),
            fontsize=8.5, va="center", ha=ha,
        )

    ax.set_xlabel("Cost of attendance: living expenses in the cohort's entry year (USD)")
    ax.set_ylabel("Eight-year completion rate")
    ax.xaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}k")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.set_xlim(df.living_cost_at_entry.min() * 0.90,
                df.living_cost_at_entry.max() * 1.34)
    ax.set_ylim(10, 66)
    ax.grid(alpha=0.22, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    # Arkansas Northeastern's reported living expenses fall 43% between 2013-14 and
    # 2014-15 -- both figures from the same source file, so this is a change in how
    # the institution calculates the estimate, not a change in local costs. Its
    # arrow spans that break, so its horizontal movement is a reporting artifact
    # and must be labelled as such rather than read as a cost decline.
    ark = df[df.label == "Ark. Northeastern"].sort_values("cohort_year")
    if not ark.empty:
        mid = ark[ark.cohort_year == "2013-14"]
        if not mid.empty:
            m = mid.iloc[0]
            ax.annotate("reporting basis changed here\n(43% fall in one year)",
                        (m.living_cost_at_entry, m.completion_pct),
                        xytext=(-30, -46), textcoords="offset points",
                        fontsize=8, style="italic", color="#B71C1C", ha="center",
                        arrowprops=dict(arrowstyle="->", color="#B71C1C", lw=1))

    ax.set_title(
        "Completion rose at all five institutions; costs rose at the four with "
        "consistent reporting\n"
        "Arkansas Northeastern appears to move LEFT only because it changed how it "
        "calculates living\nexpenses partway through — its arrow spans that break and "
        "should not be read as a cost decline.\n"
        "Hollow marker = first cohort, solid = last. Circles = four-year, squares = "
        "two-year.",
        fontsize=11.5, pad=14,
    )
    fig.tight_layout()
    fig.savefig(config.CHARTS / "7_trajectory.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    config.CHARTS.mkdir(parents=True, exist_ok=True)
    viz1_outcomes()
    viz2_cost()
    viz3_combined()
    viz4_cost_shift()
    viz5_cohort_trend()
    viz6_within_institution()
    viz7_trajectory()
    print(f"wrote 7 charts to {config.CHARTS}")

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT_DIR / "files" / "input"
OUTPUT_DIR = ROOT_DIR / "files" / "output"
PLOTS_DIR = ROOT_DIR / "files" / "plots"


def load_data(input_dir: Path | str = INPUT_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    input_path = Path(input_dir)
    drivers_path = input_path / "drivers.csv"
    timesheet_path = input_path / "timesheet.csv"

    drivers = pd.read_csv(drivers_path)
    timesheet = pd.read_csv(timesheet_path)
    return drivers, timesheet


def aggregate_driver_summary(drivers: pd.DataFrame, timesheet: pd.DataFrame) -> pd.DataFrame:
    summary = (
        timesheet.groupby("driverId", as_index=False)
        .agg(
            total_hours=("hours-logged", "sum"),
            total_miles=("miles-logged", "sum"),
            weeks_worked=("week", "count"),
            average_hours=("hours-logged", "mean"),
            average_miles=("miles-logged", "mean"),
        )
    )

    summary["average_hours"] = summary["average_hours"].round(2)
    summary["average_miles"] = summary["average_miles"].round(2)

    summary = summary.merge(drivers, on="driverId", how="left")

    column_order = [
        "driverId",
        "name",
        "ssn",
        "location",
        "certified",
        "wage-plan",
        "weeks_worked",
        "total_hours",
        "total_miles",
        "average_hours",
        "average_miles",
    ]

    return summary[column_order]


def create_plot(summary: pd.DataFrame, plots_dir: Path | str = PLOTS_DIR) -> Path:
    plot_path = Path(plots_dir) / "top10_drivers.png"
    top10 = summary.sort_values("total_miles", ascending=False).head(10)

    plt.style.use("seaborn-v0_8")
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(top10["name"].iloc[::-1], top10["total_miles"].iloc[::-1], color="#1f77b4")
    ax.set_title("Top 10 Drivers by Total Miles")
    ax.set_xlabel("Total Miles")
    ax.set_ylabel("Driver")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    return plot_path


def generate_reports(
    input_dir: Path | str = INPUT_DIR,
    output_dir: Path | str = OUTPUT_DIR,
    plots_dir: Path | str = PLOTS_DIR,
) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    plot_path = Path(plots_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    plot_path.mkdir(parents=True, exist_ok=True)

    drivers, timesheet = load_data(input_dir)
    summary = aggregate_driver_summary(drivers, timesheet)

    summary_file = output_path / "summary.csv"
    summary.to_csv(summary_file, index=False)
    created_plot = create_plot(summary, plots_dir)
    return summary_file, created_plot


if __name__ == "__main__":
    generate_reports()

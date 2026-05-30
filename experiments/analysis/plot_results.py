from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "results" / "raw"
PLOTS_DIR = ROOT / "results" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def save_line_plot(df: pd.DataFrame, title: str, output_path: Path) -> None:
    plt.figure(figsize=(8, 5))
    for model in sorted(df["model"].unique()):
        sub = df[df["model"] == model].sort_values("task_count")
        plt.plot(sub["task_count"], sub["wall_time_s"], marker="o", label=model)
    plt.xlabel("task_count")
    plt.ylabel("avg wall_time_s")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_sleep_io():
    path = RAW_DIR / "sleep_io_results.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    grouped = (
        df.groupby(["model", "task_count", "delay_ms"], as_index=False)["wall_time_s"]
        .mean()
    )

    for delay_ms in sorted(grouped["delay_ms"].dropna().unique()):
        sub = grouped[grouped["delay_ms"] == delay_ms]
        save_line_plot(
            sub,
            f"Sleep I/O Benchmark ({delay_ms} ms)",
            PLOTS_DIR / f"sleep_io_wall_time_{delay_ms}ms.png"
        )


def plot_http_local():
    path = RAW_DIR / "http_local_results.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    grouped = (
        df.groupby(["model", "task_count", "delay_ms"], as_index=False)["wall_time_s"]
        .mean()
    )

    for delay_ms in sorted(grouped["delay_ms"].dropna().unique()):
        sub = grouped[grouped["delay_ms"] == delay_ms]
        save_line_plot(
            sub,
            f"Local HTTP Benchmark ({delay_ms} ms)",
            PLOTS_DIR / f"http_local_wall_time_{delay_ms}ms.png"
        )


def plot_cpu_bound():
    path = RAW_DIR / "cpu_bound_results.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    grouped = (
        df.groupby(["model", "task_count", "work_n"], as_index=False)["wall_time_s"]
        .mean()
    )

    for work_n in sorted(grouped["work_n"].dropna().unique()):
        sub = grouped[grouped["work_n"] == work_n]
        save_line_plot(
            sub,
            f"CPU-bound Benchmark (work_n={int(work_n)})",
            PLOTS_DIR / f"cpu_bound_wall_time_work_{int(work_n)}.png"
        )


def main():
    plot_sleep_io()
    plot_http_local()
    plot_cpu_bound()
    print("plots generated.")


if __name__ == "__main__":
    main()
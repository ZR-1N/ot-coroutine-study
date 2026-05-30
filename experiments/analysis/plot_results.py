from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "results" / "raw"
PLOTS_DIR = ROOT / "results" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_sleep_io():
    df = pd.read_csv(RAW_DIR / "sleep_io_results.csv")
    grouped = df.groupby(["model", "task_count"], as_index=False)["wall_time_s"].mean()

    plt.figure(figsize=(8, 5))
    for model in grouped["model"].unique():
        sub = grouped[grouped["model"] == model]
        plt.plot(sub["task_count"], sub["wall_time_s"], marker="o", label=model)
    plt.xlabel("task_count")
    plt.ylabel("avg wall_time_s")
    plt.title("Sleep I/O Benchmark")
    plt.legend()
    plt.grid(True)
    plt.savefig(PLOTS_DIR / "sleep_io_wall_time.png", dpi=200, bbox_inches="tight")
    plt.close()


def plot_http_local():
    df = pd.read_csv(RAW_DIR / "http_local_results.csv")
    grouped = df.groupby(["model", "task_count"], as_index=False)["wall_time_s"].mean()

    plt.figure(figsize=(8, 5))
    for model in grouped["model"].unique():
        sub = grouped[grouped["model"] == model]
        plt.plot(sub["task_count"], sub["wall_time_s"], marker="o", label=model)
    plt.xlabel("task_count")
    plt.ylabel("avg wall_time_s")
    plt.title("Local HTTP Benchmark")
    plt.legend()
    plt.grid(True)
    plt.savefig(PLOTS_DIR / "http_local_wall_time.png", dpi=200, bbox_inches="tight")
    plt.close()


def plot_cpu_bound():
    df = pd.read_csv(RAW_DIR / "cpu_bound_results.csv")
    grouped = df.groupby(["model", "task_count"], as_index=False)["wall_time_s"].mean()

    plt.figure(figsize=(8, 5))
    for model in grouped["model"].unique():
        sub = grouped[grouped["model"] == model]
        plt.plot(sub["task_count"], sub["wall_time_s"], marker="o", label=model)
    plt.xlabel("task_count")
    plt.ylabel("avg wall_time_s")
    plt.title("CPU-bound Benchmark")
    plt.legend()
    plt.grid(True)
    plt.savefig(PLOTS_DIR / "cpu_bound_wall_time.png", dpi=200, bbox_inches="tight")
    plt.close()


def main():
    if (RAW_DIR / "sleep_io_results.csv").exists():
        plot_sleep_io()
    if (RAW_DIR / "http_local_results.csv").exists():
        plot_http_local()
    if (RAW_DIR / "cpu_bound_results.csv").exists():
        plot_cpu_bound()
    print("plots generated.")


if __name__ == "__main__":
    main()
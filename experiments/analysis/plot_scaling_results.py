from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "results" / "raw"
PLOTS_DIR = ROOT / "results" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def save_line_plot(df: pd.DataFrame, xcol: str, ycol: str, title: str, ylabel: str, output_path: Path):
    plt.figure(figsize=(8, 5))
    for model in sorted(df["model"].unique()):
        sub = df[df["model"] == model].sort_values(xcol)
        plt.plot(sub[xcol], sub[ycol], marker="o", label=model)
    plt.xlabel(xcol)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()


def plot_python_scaling():
    path = RAW_DIR / "python_scaling_results.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    grouped = (
        df.groupby(["model", "concurrency"], as_index=False)
        .agg({
            "qps": "mean",
            "p95_latency_ms": "mean",
            "peak_rss_mb": "mean"
        })
    )

    save_line_plot(
        grouped, "concurrency", "qps",
        "Python Scaling Benchmark: QPS",
        "QPS",
        PLOTS_DIR / "python_scaling_qps.png"
    )

    save_line_plot(
        grouped, "concurrency", "p95_latency_ms",
        "Python Scaling Benchmark: P95 Latency",
        "P95 Latency (ms)",
        PLOTS_DIR / "python_scaling_p95.png"
    )

    save_line_plot(
        grouped, "concurrency", "peak_rss_mb",
        "Python Scaling Benchmark: Peak RSS",
        "Peak RSS (MB)",
        PLOTS_DIR / "python_scaling_memory.png"
    )


def plot_java_scaling():
    path = RAW_DIR / "java_scaling_results.csv"
    if not path.exists():
        return

    df = pd.read_csv(path)
    grouped = (
        df.groupby(["model", "concurrency"], as_index=False)
        .agg({
            "qps": "mean",
            "p95_latency_ms": "mean",
            "peak_used_memory_mb": "mean"
        })
    )

    save_line_plot(
        grouped, "concurrency", "qps",
        "Java Scaling Benchmark: QPS",
        "QPS",
        PLOTS_DIR / "java_scaling_qps.png"
    )

    save_line_plot(
        grouped, "concurrency", "p95_latency_ms",
        "Java Scaling Benchmark: P95 Latency",
        "P95 Latency (ms)",
        PLOTS_DIR / "java_scaling_p95.png"
    )

    save_line_plot(
        grouped, "concurrency", "peak_used_memory_mb",
        "Java Scaling Benchmark: Used Heap Memory",
        "Used Heap Memory (MB)",
        PLOTS_DIR / "java_scaling_memory.png"
    )


def main():
    plot_python_scaling()
    plot_java_scaling()
    print("scaling plots generated.")


if __name__ == "__main__":
    main()
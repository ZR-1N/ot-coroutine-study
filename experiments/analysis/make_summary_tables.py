from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "results" / "raw"
SUMMARY_DIR = ROOT / "results" / "summary"

SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


def save_df(df: pd.DataFrame, filename: str) -> None:
    path = SUMMARY_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")


def make_sleep_summary() -> pd.DataFrame:
    path = RAW_DIR / "sleep_io_results.csv"
    df = pd.read_csv(path)

    grouped = (
        df.groupby(["model", "task_count", "delay_ms"], as_index=False)
        .agg({
            "wall_time_s": "mean",
            "throughput_ops": "mean",
            "peak_rss_mb": "mean"
        })
    )

    rows = []
    for delay_ms in sorted(grouped["delay_ms"].unique()):
        for task_count in sorted(grouped["task_count"].unique()):
            sub = grouped[
                (grouped["delay_ms"] == delay_ms) &
                (grouped["task_count"] == task_count)
            ]

            asyncio_row = sub[sub["model"] == "asyncio"].iloc[0]
            thread_row = sub[sub["model"] == "threadpool"].iloc[0]

            rows.append({
                "experiment": "sleep_io",
                "delay_ms": delay_ms,
                "task_count": task_count,
                "asyncio_wall_time_s": round(asyncio_row["wall_time_s"], 6),
                "threadpool_wall_time_s": round(thread_row["wall_time_s"], 6),
                "speedup_asyncio_vs_threadpool": round(
                    thread_row["wall_time_s"] / asyncio_row["wall_time_s"], 3
                ),
                "asyncio_throughput": round(asyncio_row["throughput_ops"], 3),
                "threadpool_throughput": round(thread_row["throughput_ops"], 3),
                "asyncio_peak_rss_mb": round(asyncio_row["peak_rss_mb"], 3),
                "threadpool_peak_rss_mb": round(thread_row["peak_rss_mb"], 3),
            })

    result = pd.DataFrame(rows)
    save_df(result, "sleep_io_summary.csv")
    return result


def make_http_summary() -> pd.DataFrame:
    path = RAW_DIR / "http_local_results.csv"
    df = pd.read_csv(path)

    grouped = (
        df.groupby(["model", "task_count", "delay_ms"], as_index=False)
        .agg({
            "wall_time_s": "mean",
            "throughput_ops": "mean",
            "peak_rss_mb": "mean"
        })
    )

    rows = []
    for delay_ms in sorted(grouped["delay_ms"].unique()):
        for task_count in sorted(grouped["task_count"].unique()):
            sub = grouped[
                (grouped["delay_ms"] == delay_ms) &
                (grouped["task_count"] == task_count)
            ]

            asyncio_row = sub[sub["model"] == "asyncio_aiohttp"].iloc[0]
            thread_row = sub[sub["model"] == "threadpool_requests"].iloc[0]

            rows.append({
                "experiment": "http_local",
                "delay_ms": delay_ms,
                "task_count": task_count,
                "asyncio_wall_time_s": round(asyncio_row["wall_time_s"], 6),
                "threadpool_wall_time_s": round(thread_row["wall_time_s"], 6),
                "speedup_asyncio_vs_threadpool": round(
                    thread_row["wall_time_s"] / asyncio_row["wall_time_s"], 3
                ),
                "asyncio_throughput": round(asyncio_row["throughput_ops"], 3),
                "threadpool_throughput": round(thread_row["throughput_ops"], 3),
                "asyncio_peak_rss_mb": round(asyncio_row["peak_rss_mb"], 3),
                "threadpool_peak_rss_mb": round(thread_row["peak_rss_mb"], 3),
            })

    result = pd.DataFrame(rows)
    save_df(result, "http_local_summary.csv")
    return result


def make_cpu_summary() -> pd.DataFrame:
    path = RAW_DIR / "cpu_bound_results.csv"
    df = pd.read_csv(path)

    grouped = (
        df.groupby(["model", "task_count", "work_n"], as_index=False)
        .agg({
            "wall_time_s": "mean",
            "throughput_ops": "mean",
            "peak_rss_mb": "mean"
        })
    )

    rows = []
    for work_n in sorted(grouped["work_n"].dropna().unique()):
        for task_count in sorted(grouped["task_count"].unique()):
            sub = grouped[
                (grouped["work_n"] == work_n) &
                (grouped["task_count"] == task_count)
            ]

            single_row = sub[sub["model"] == "single"].iloc[0]
            asyncio_row = sub[sub["model"] == "asyncio"].iloc[0]
            thread_row = sub[sub["model"] == "threadpool"].iloc[0]

            rows.append({
                "experiment": "cpu_bound",
                "work_n": int(work_n),
                "task_count": task_count,
                "single_wall_time_s": round(single_row["wall_time_s"], 6),
                "asyncio_wall_time_s": round(asyncio_row["wall_time_s"], 6),
                "threadpool_wall_time_s": round(thread_row["wall_time_s"], 6),
                "single_throughput": round(single_row["throughput_ops"], 3),
                "asyncio_throughput": round(asyncio_row["throughput_ops"], 3),
                "threadpool_throughput": round(thread_row["throughput_ops"], 3),
                "single_peak_rss_mb": round(single_row["peak_rss_mb"], 3),
                "asyncio_peak_rss_mb": round(asyncio_row["peak_rss_mb"], 3),
                "threadpool_peak_rss_mb": round(thread_row["peak_rss_mb"], 3),
                "asyncio_vs_single_ratio": round(
                    asyncio_row["wall_time_s"] / single_row["wall_time_s"], 3
                ),
                "threadpool_vs_single_ratio": round(
                    thread_row["wall_time_s"] / single_row["wall_time_s"], 3
                ),
            })

    result = pd.DataFrame(rows)
    save_df(result, "cpu_bound_summary.csv")
    return result


def make_key_table(
    sleep_df: pd.DataFrame,
    http_df: pd.DataFrame,
    cpu_df: pd.DataFrame
) -> pd.DataFrame:
    """
    只摘最关键的几行，方便直接放进报告：
    - sleep_io: task_count = 10000
    - http_local: task_count = 3000
    - cpu_bound: task_count = 100
    """
    sleep_key = sleep_df[sleep_df["task_count"] == 10000].copy()
    sleep_key["scenario"] = sleep_key["delay_ms"].astype(str) + " ms"

    http_key = http_df[http_df["task_count"] == 3000].copy()
    http_key["scenario"] = http_key["delay_ms"].astype(str) + " ms"

    cpu_key = cpu_df[cpu_df["task_count"] == 100].copy()
    cpu_key["scenario"] = "work_n=" + cpu_key["work_n"].astype(int).astype(str)

    key_rows = []

    for _, row in sleep_key.iterrows():
        key_rows.append({
            "experiment": "sleep_io",
            "scenario": row["scenario"],
            "task_count": int(row["task_count"]),
            "asyncio_wall_time_s": row["asyncio_wall_time_s"],
            "baseline_wall_time_s": row["threadpool_wall_time_s"],
            "speedup_or_ratio": row["speedup_asyncio_vs_threadpool"],
            "note": "asyncio vs threadpool"
        })

    for _, row in http_key.iterrows():
        key_rows.append({
            "experiment": "http_local",
            "scenario": row["scenario"],
            "task_count": int(row["task_count"]),
            "asyncio_wall_time_s": row["asyncio_wall_time_s"],
            "baseline_wall_time_s": row["threadpool_wall_time_s"],
            "speedup_or_ratio": row["speedup_asyncio_vs_threadpool"],
            "note": "asyncio vs threadpool"
        })

    for _, row in cpu_key.iterrows():
        key_rows.append({
            "experiment": "cpu_bound",
            "scenario": row["scenario"],
            "task_count": int(row["task_count"]),
            "asyncio_wall_time_s": row["asyncio_wall_time_s"],
            "baseline_wall_time_s": row["single_wall_time_s"],
            "speedup_or_ratio": row["asyncio_vs_single_ratio"],
            "note": "ratio to single (closer to 1 means similar)"
        })

    key_df = pd.DataFrame(key_rows)
    save_df(key_df, "key_summary_table.csv")
    return key_df


def write_markdown(
    sleep_df: pd.DataFrame,
    http_df: pd.DataFrame,
    cpu_df: pd.DataFrame,
    key_df: pd.DataFrame
) -> None:
    path = SUMMARY_DIR / "summary_tables.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Summary Tables\n\n")

        f.write("## Key Summary Table\n\n")
        f.write(key_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## Sleep I/O Summary\n\n")
        f.write(sleep_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## Local HTTP Summary\n\n")
        f.write(http_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## CPU-bound Summary\n\n")
        f.write(cpu_df.to_markdown(index=False))
        f.write("\n")


def main():
    sleep_df = make_sleep_summary()
    http_df = make_http_summary()
    cpu_df = make_cpu_summary()
    key_df = make_key_table(sleep_df, http_df, cpu_df)
    write_markdown(sleep_df, http_df, cpu_df, key_df)
    print("summary tables generated in results/summary/")


if __name__ == "__main__":
    main()
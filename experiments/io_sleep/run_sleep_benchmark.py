import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from experiments.common.metrics import BenchmarkResult, ProcessMonitor, result_to_dict
from experiments.common.utils import append_results_csv


TASK_COUNTS = [100, 1000, 5000, 10000]
DELAYS_MS = [10, 50, 100]
REPEATS = 3
THREAD_WORKERS = 300


def blocking_sleep_task(delay_ms: int) -> None:
    time.sleep(delay_ms / 1000)


async def async_sleep_task(delay_ms: int) -> None:
    await asyncio.sleep(delay_ms / 1000)


def run_threadpool(task_count: int, delay_ms: int) -> tuple[float, float, float]:
    monitor = ProcessMonitor()
    monitor.start()
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=THREAD_WORKERS) as pool:
        list(pool.map(lambda _: blocking_sleep_task(delay_ms), range(task_count)))
    wall = time.perf_counter() - start
    monitor.stop()
    return wall, monitor.avg_cpu_percent, monitor.peak_rss_mb


async def run_asyncio(task_count: int, delay_ms: int) -> tuple[float, float, float]:
    monitor = ProcessMonitor()
    monitor.start()
    start = time.perf_counter()
    await asyncio.gather(*(async_sleep_task(delay_ms) for _ in range(task_count)))
    wall = time.perf_counter() - start
    monitor.stop()
    return wall, monitor.avg_cpu_percent, monitor.peak_rss_mb


def main():
    rows = []
    for repeat_id in range(1, REPEATS + 1):
        for delay_ms in DELAYS_MS:
            for task_count in TASK_COUNTS:
                wall, cpu, rss = run_threadpool(task_count, delay_ms)
                rows.append(result_to_dict(BenchmarkResult(
                    experiment="sleep_io",
                    model="threadpool",
                    task_count=task_count,
                    concurrency=THREAD_WORKERS,
                    delay_ms=delay_ms,
                    repeat_id=repeat_id,
                    wall_time_s=wall,
                    throughput_ops=task_count / wall,
                    avg_cpu_percent=cpu,
                    peak_rss_mb=rss,
                )))

                wall, cpu, rss = asyncio.run(run_asyncio(task_count, delay_ms))
                rows.append(result_to_dict(BenchmarkResult(
                    experiment="sleep_io",
                    model="asyncio",
                    task_count=task_count,
                    concurrency=task_count,
                    delay_ms=delay_ms,
                    repeat_id=repeat_id,
                    wall_time_s=wall,
                    throughput_ops=task_count / wall,
                    avg_cpu_percent=cpu,
                    peak_rss_mb=rss,
                )))
                print(f"[sleep_io] repeat={repeat_id} delay={delay_ms}ms tasks={task_count} done")

    append_results_csv("sleep_io_results.csv", rows)


if __name__ == "__main__":
    main()
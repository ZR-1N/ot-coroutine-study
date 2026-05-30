import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from experiments.common.metrics import BenchmarkResult, ProcessMonitor, result_to_dict
from experiments.common.utils import append_results_csv


TASK_COUNTS = [10, 50, 100]
WORK_N = [200000, 500000, 1000000]
REPEATS = 3
THREAD_WORKERS = 8


def cpu_task(n: int) -> int:
    s = 0
    for i in range(n):
        s += i * i
    return s


async def fake_async_cpu_task(n: int) -> int:
    return cpu_task(n)


def run_single(task_count: int, n: int) -> tuple[float, float, float]:
    monitor = ProcessMonitor()
    monitor.start()
    start = time.perf_counter()
    for _ in range(task_count):
        cpu_task(n)
    wall = time.perf_counter() - start
    monitor.stop()
    return wall, monitor.avg_cpu_percent, monitor.peak_rss_mb


def run_threadpool(task_count: int, n: int) -> tuple[float, float, float]:
    monitor = ProcessMonitor()
    monitor.start()
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=THREAD_WORKERS) as pool:
        list(pool.map(lambda _: cpu_task(n), range(task_count)))
    wall = time.perf_counter() - start
    monitor.stop()
    return wall, monitor.avg_cpu_percent, monitor.peak_rss_mb


async def run_asyncio(task_count: int, n: int) -> tuple[float, float, float]:
    monitor = ProcessMonitor()
    monitor.start()
    start = time.perf_counter()
    await asyncio.gather(*(fake_async_cpu_task(n) for _ in range(task_count)))
    wall = time.perf_counter() - start
    monitor.stop()
    return wall, monitor.avg_cpu_percent, monitor.peak_rss_mb


def main():
    rows = []
    for repeat_id in range(1, REPEATS + 1):
        for n in WORK_N:
            for task_count in TASK_COUNTS:
                wall, cpu, rss = run_single(task_count, n)
                rows.append(result_to_dict(BenchmarkResult(
                    experiment="cpu_bound",
                    model="single",
                    task_count=task_count,
                    concurrency=1,
                    delay_ms=0,
                    repeat_id=repeat_id,
                    wall_time_s=wall,
                    throughput_ops=task_count / wall,
                    avg_cpu_percent=cpu,
                    peak_rss_mb=rss,
                )))

                wall, cpu, rss = run_threadpool(task_count, n)
                rows.append(result_to_dict(BenchmarkResult(
                    experiment="cpu_bound",
                    model="threadpool",
                    task_count=task_count,
                    concurrency=THREAD_WORKERS,
                    delay_ms=0,
                    repeat_id=repeat_id,
                    wall_time_s=wall,
                    throughput_ops=task_count / wall,
                    avg_cpu_percent=cpu,
                    peak_rss_mb=rss,
                )))

                wall, cpu, rss = asyncio.run(run_asyncio(task_count, n))
                rows.append(result_to_dict(BenchmarkResult(
                    experiment="cpu_bound",
                    model="asyncio",
                    task_count=task_count,
                    concurrency=task_count,
                    delay_ms=0,
                    repeat_id=repeat_id,
                    wall_time_s=wall,
                    throughput_ops=task_count / wall,
                    avg_cpu_percent=cpu,
                    peak_rss_mb=rss,
                )))
                print(f"[cpu_bound] repeat={repeat_id} n={n} tasks={task_count} done")

    append_results_csv("cpu_bound_results.csv", rows)


if __name__ == "__main__":
    main()
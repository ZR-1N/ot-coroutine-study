import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import requests

from experiments.common.metrics import BenchmarkResult, ProcessMonitor, result_to_dict
from experiments.common.utils import append_results_csv


URL = "http://127.0.0.1:8080/ping"
TASK_COUNTS = [100, 1000, 3000]
DELAYS_MS = [10, 50, 100]
REPEATS = 3
THREAD_WORKERS = 200


def sync_http_task(delay_ms: int, session: requests.Session) -> None:
    resp = session.get(URL, params={"delay_ms": delay_ms}, timeout=10)
    resp.raise_for_status()


async def async_http_task(delay_ms: int, session: aiohttp.ClientSession) -> None:
    async with session.get(URL, params={"delay_ms": delay_ms}, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        await resp.read()


def run_threadpool_http(task_count: int, delay_ms: int) -> tuple[float, float, float]:
    monitor = ProcessMonitor()
    monitor.start()
    start = time.perf_counter()
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=THREAD_WORKERS) as pool:
            list(pool.map(lambda _: sync_http_task(delay_ms, session), range(task_count)))
    wall = time.perf_counter() - start
    monitor.stop()
    return wall, monitor.avg_cpu_percent, monitor.peak_rss_mb


async def run_async_http(task_count: int, delay_ms: int) -> tuple[float, float, float]:
    monitor = ProcessMonitor()
    monitor.start()
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*(async_http_task(delay_ms, session) for _ in range(task_count)))
    wall = time.perf_counter() - start
    monitor.stop()
    return wall, monitor.avg_cpu_percent, monitor.peak_rss_mb


def main():
    rows = []
    for repeat_id in range(1, REPEATS + 1):
        for delay_ms in DELAYS_MS:
            for task_count in TASK_COUNTS:
                wall, cpu, rss = run_threadpool_http(task_count, delay_ms)
                rows.append(result_to_dict(BenchmarkResult(
                    experiment="http_local",
                    model="threadpool_requests",
                    task_count=task_count,
                    concurrency=THREAD_WORKERS,
                    delay_ms=delay_ms,
                    repeat_id=repeat_id,
                    wall_time_s=wall,
                    throughput_ops=task_count / wall,
                    avg_cpu_percent=cpu,
                    peak_rss_mb=rss,
                )))

                wall, cpu, rss = asyncio.run(run_async_http(task_count, delay_ms))
                rows.append(result_to_dict(BenchmarkResult(
                    experiment="http_local",
                    model="asyncio_aiohttp",
                    task_count=task_count,
                    concurrency=task_count,
                    delay_ms=delay_ms,
                    repeat_id=repeat_id,
                    wall_time_s=wall,
                    throughput_ops=task_count / wall,
                    avg_cpu_percent=cpu,
                    peak_rss_mb=rss,
                )))
                print(f"[http_local] repeat={repeat_id} delay={delay_ms}ms tasks={task_count} done")

    append_results_csv("http_local_results.csv", rows)


if __name__ == "__main__":
    main()
import asyncio
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import psutil


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "results" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

TOTAL_TASKS = 10000
DELAY_MS = 50
CONCURRENCY_LEVELS = [100, 500, 1000, 2000, 3000, 5000]
REPEATS = 3
CPU_WORK_ROUNDS = 3000


class MemorySampler:
    def __init__(self, interval: float = 0.02):
        self.process = psutil.Process()
        self.interval = interval
        self.running = False
        self.thread = None
        self.peak_rss_mb = 0.0

    def _worker(self):
        while self.running:
            rss_mb = self.process.memory_info().rss / (1024 * 1024)
            self.peak_rss_mb = max(self.peak_rss_mb, rss_mb)
            time.sleep(self.interval)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()


def light_cpu_work() -> int:
    s = 0
    for i in range(CPU_WORK_ROUNDS):
        s += (i * i) % 97
    return s


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = max(0, math.ceil(0.95 * len(values)) - 1)
    return values[idx]


def thread_task(delay_ms: int, scheduled_at: float) -> float:
    light_cpu_work()
    time.sleep(delay_ms / 1000.0)
    return (time.perf_counter() - scheduled_at) * 1000.0


async def async_task(delay_ms: int, sem: asyncio.Semaphore, scheduled_at: float) -> float:
    async with sem:
        light_cpu_work()
        await asyncio.sleep(delay_ms / 1000.0)
    return (time.perf_counter() - scheduled_at) * 1000.0


def run_threadpool(concurrency: int) -> dict:
    sampler = MemorySampler()
    sampler.start()

    start_all = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = []
        for _ in range(TOTAL_TASKS):
            scheduled_at = time.perf_counter()
            futures.append(pool.submit(thread_task, DELAY_MS, scheduled_at))
        latencies = [f.result() for f in futures]

    total_time = time.perf_counter() - start_all
    sampler.stop()

    return {
        "total_time_s": total_time,
        "qps": TOTAL_TASKS / total_time,
        "p95_latency_ms": p95(latencies),
        "peak_rss_mb": sampler.peak_rss_mb,
    }


async def run_asyncio(concurrency: int) -> dict:
    sampler = MemorySampler()
    sampler.start()

    start_all = time.perf_counter()
    sem = asyncio.Semaphore(concurrency)

    tasks = []
    for _ in range(TOTAL_TASKS):
        scheduled_at = time.perf_counter()
        tasks.append(asyncio.create_task(async_task(DELAY_MS, sem, scheduled_at)))

    latencies = await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start_all
    sampler.stop()

    return {
        "total_time_s": total_time,
        "qps": TOTAL_TASKS / total_time,
        "p95_latency_ms": p95(list(latencies)),
        "peak_rss_mb": sampler.peak_rss_mb,
    }


def main():
    rows = []

    for repeat_id in range(1, REPEATS + 1):
        for concurrency in CONCURRENCY_LEVELS:
            result = run_threadpool(concurrency)
            rows.append({
                "experiment": "python_scaling",
                "model": "threadpool",
                "total_tasks": TOTAL_TASKS,
                "delay_ms": DELAY_MS,
                "concurrency": concurrency,
                "repeat_id": repeat_id,
                **result,
            })
            print(f"[python_scaling][threadpool] repeat={repeat_id}, concurrency={concurrency} done")

            result = asyncio.run(run_asyncio(concurrency))
            rows.append({
                "experiment": "python_scaling",
                "model": "asyncio",
                "total_tasks": TOTAL_TASKS,
                "delay_ms": DELAY_MS,
                "concurrency": concurrency,
                "repeat_id": repeat_id,
                **result,
            })
            print(f"[python_scaling][asyncio] repeat={repeat_id}, concurrency={concurrency} done")

    df = pd.DataFrame(rows)
    output = RAW_DIR / "python_scaling_results.csv"
    df.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"saved to: {output}")


if __name__ == "__main__":
    main()
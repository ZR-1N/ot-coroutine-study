import os
import time
import threading
from dataclasses import dataclass, asdict

import psutil


@dataclass
class BenchmarkResult:
    experiment: str
    model: str
    task_count: int
    concurrency: int
    delay_ms: int
    repeat_id: int
    wall_time_s: float
    throughput_ops: float
    avg_cpu_percent: float
    peak_rss_mb: float


class ProcessMonitor:
    def __init__(self, interval: float = 0.05):
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        self._running = False
        self._thread = None
        self.cpu_samples = []
        self.rss_samples = []

    def _worker(self):
        self.process.cpu_percent(interval=None)
        while self._running:
            cpu = self.process.cpu_percent(interval=None)
            rss_mb = self.process.memory_info().rss / (1024 * 1024)
            self.cpu_samples.append(cpu)
            self.rss_samples.append(rss_mb)
            time.sleep(self.interval)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join()

    @property
    def avg_cpu_percent(self) -> float:
        if not self.cpu_samples:
            return 0.0
        return sum(self.cpu_samples) / len(self.cpu_samples)

    @property
    def peak_rss_mb(self) -> float:
        if not self.rss_samples:
            return 0.0
        return max(self.rss_samples)


def result_to_dict(result: BenchmarkResult) -> dict:
    return asdict(result)
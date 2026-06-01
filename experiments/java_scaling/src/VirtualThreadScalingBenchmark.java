import java.io.IOException;
import java.io.PrintWriter;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.*;


public class VirtualThreadScalingBenchmark {
    static final int TOTAL_TASKS = 10000;
    static final int SLEEP_MS = 50;
    static final int REPEATS = 3;
    static final int CPU_WORK_ROUNDS = 3000;
    static final int[] CONCURRENCY_LEVELS = {100, 500, 1000, 2000, 3000};

    static class Result {
        double totalTimeS;
        double qps;
        double p95LatencyMs;
        double peakUsedMemoryMB;

        Result(double totalTimeS, double qps, double p95LatencyMs, double peakUsedMemoryMB) {
            this.totalTimeS = totalTimeS;
            this.qps = qps;
            this.p95LatencyMs = p95LatencyMs;
            this.peakUsedMemoryMB = peakUsedMemoryMB;
        }
    }

    static class MemorySampler implements AutoCloseable {
        private volatile boolean running = true;
        private volatile long peakUsedBytes = 0;
        private final Thread samplerThread;

        MemorySampler() {
            samplerThread = Thread.ofPlatform().daemon().start(() -> {
                MemoryMXBean bean = ManagementFactory.getMemoryMXBean();
                while (running) {
                    long used = bean.getHeapMemoryUsage().getUsed();
                    peakUsedBytes = Math.max(peakUsedBytes, used);
                    try {
                        Thread.sleep(20);
                    } catch (InterruptedException ignored) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            });
        }

        double peakUsedMemoryMB() {
            return peakUsedBytes / (1024.0 * 1024.0);
        }

        @Override
        public void close() {
            running = false;
            try {
                samplerThread.join();
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }
        }
    }

    static void lightCpuWork() {
        long s = 0;
        for (int i = 0; i < CPU_WORK_ROUNDS; i++) {
            s += (long) i * i % 97;
        }
        if (s == -1) {
            System.out.println("impossible");
        }
    }

    static double percentile95(List<Double> values) {
        if (values.isEmpty()) return 0.0;
        Collections.sort(values);
        int idx = Math.max(0, (int) Math.ceil(0.95 * values.size()) - 1);
        return values.get(idx);
    }

    static Result runPlatformThreads(int concurrency) throws Exception {
        try (MemorySampler sampler = new MemorySampler()) {
            long startAll = System.nanoTime();
            ExecutorService executor = Executors.newFixedThreadPool(concurrency);
            List<Future<Double>> futures = new ArrayList<>(TOTAL_TASKS);

            for (int i = 0; i < TOTAL_TASKS; i++) {
                long scheduledAt = System.nanoTime();
                futures.add(executor.submit(() -> {
                    lightCpuWork();
                    Thread.sleep(SLEEP_MS);
                    return (System.nanoTime() - scheduledAt) / 1_000_000.0;
                }));
            }

            List<Double> latencies = new ArrayList<>(TOTAL_TASKS);
            for (Future<Double> f : futures) {
                latencies.add(f.get());
            }

            executor.shutdown();
            executor.awaitTermination(1, TimeUnit.HOURS);

            double totalTimeS = (System.nanoTime() - startAll) / 1_000_000_000.0;
            return new Result(
                    totalTimeS,
                    TOTAL_TASKS / totalTimeS,
                    percentile95(latencies),
                    sampler.peakUsedMemoryMB()
            );
        }
    }

    static Result runVirtualThreads(int concurrency) throws Exception {
        try (MemorySampler sampler = new MemorySampler()) {
            long startAll = System.nanoTime();
            ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
            Semaphore semaphore = new Semaphore(concurrency);
            List<Future<Double>> futures = new ArrayList<>(TOTAL_TASKS);

            for (int i = 0; i < TOTAL_TASKS; i++) {
                long scheduledAt = System.nanoTime();
                futures.add(executor.submit(() -> {
                    semaphore.acquire();
                    try {
                        lightCpuWork();
                        Thread.sleep(SLEEP_MS);
                        return (System.nanoTime() - scheduledAt) / 1_000_000.0;
                    } finally {
                        semaphore.release();
                    }
                }));
            }

            List<Double> latencies = new ArrayList<>(TOTAL_TASKS);
            for (Future<Double> f : futures) {
                latencies.add(f.get());
            }

            executor.shutdown();
            executor.awaitTermination(1, TimeUnit.HOURS);

            double totalTimeS = (System.nanoTime() - startAll) / 1_000_000_000.0;
            return new Result(
                    totalTimeS,
                    TOTAL_TASKS / totalTimeS,
                    percentile95(latencies),
                    sampler.peakUsedMemoryMB()
            );
        }
    }

    public static void main(String[] args) throws Exception {
        Path root = Path.of("").toAbsolutePath();
        Path rawDir = root.resolve("results").resolve("raw");
        Files.createDirectories(rawDir);

        Path output = rawDir.resolve("java_scaling_results.csv");

        try (PrintWriter writer = new PrintWriter(Files.newBufferedWriter(output, StandardCharsets.UTF_8))) {
            writer.println("experiment,model,total_tasks,sleep_ms,concurrency,repeat_id,total_time_s,qps,p95_latency_ms,peak_used_memory_mb");

            for (int repeatId = 1; repeatId <= REPEATS; repeatId++) {
                for (int concurrency : CONCURRENCY_LEVELS) {
                    Result platform = runPlatformThreads(concurrency);
                    writer.printf(
                            "java_scaling,platform_thread,%d,%d,%d,%d,%.6f,%.6f,%.6f,%.6f%n",
                            TOTAL_TASKS, SLEEP_MS, concurrency, repeatId,
                            platform.totalTimeS, platform.qps, platform.p95LatencyMs, platform.peakUsedMemoryMB
                    );
                    System.out.printf("[java_scaling][platform_thread] repeat=%d, concurrency=%d done%n", repeatId, concurrency);

                    Result virtual = runVirtualThreads(concurrency);
                    writer.printf(
                            "java_scaling,virtual_thread,%d,%d,%d,%d,%.6f,%.6f,%.6f,%.6f%n",
                            TOTAL_TASKS, SLEEP_MS, concurrency, repeatId,
                            virtual.totalTimeS, virtual.qps, virtual.p95LatencyMs, virtual.peakUsedMemoryMB
                    );
                    System.out.printf("[java_scaling][virtual_thread] repeat=%d, concurrency=%d done%n", repeatId, concurrency);
                }
            }
        }

        System.out.println("saved to: " + output.toAbsolutePath());
    }
}
# OT-Coroutine-Study

OT-协程技术调研课程项目仓库。  
本项目围绕**“从线程到协程：高并发 I/O 场景下轻量级并发机制的底层实现与实验分析”**展开，包含实验代码、原始结果数据、自动绘图脚本、环境信息收集脚本，以及课程报告与 Slides 所需素材。

---

## 1. 项目简介

在高并发服务端系统中，许多任务的主要时间并不消耗在计算上，而是消耗在：

- 网络 I/O
- 数据库访问
- 磁盘读写
- RPC 调用
- 定时等待与事件通知

传统的“一请求一线程”写法虽然直观，但当并发数上升后，线程栈空间、上下文切换、阻塞等待和调度成本都会迅速累积。协程、轻量级线程与事件循环机制的核心目标，并不是让单个任务“算得更快”，而是：

> 以更低的成本组织大量等待中的任务。

本仓库通过多组实验，系统比较了：

- Python 中 `asyncio` 与线程池模型的差异
- Java 21 中 platform thread 与 virtual thread 的差异
- I/O 密集型任务与 CPU 密集型任务的本质不同
- 高并发扩展区间内，吞吐、内存与高分位延迟的变化趋势

---

## 2. 项目目标

本项目主要研究以下问题：

1. 为什么并发模型会从进程、线程进一步演进到协程式并发。
2. 协程在高并发 I/O 场景中究竟“轻”在哪里。
3. 编译器、运行时与操作系统分别在协程实现中承担什么职责。
4. 不同语言（Python、Java、Go、C++20）对轻量级并发的支持方式有何差异。
5. 在 I/O 密集型与 CPU 密集型任务中，协程/轻量级并发与线程模型的性能差异如何。
6. 当并发上限继续提高时，不同并发模型会在何处出现平台、波动或性能回落。

---

## 3. 仓库结构

```text
ot-coroutine-study/
├─ experiments/                  # 各类实验代码
│  ├─ common/                    # 公共工具（指标采集、CSV 写入等）
│  ├─ io_sleep/                  # Sleep I/O 基础实验
│  ├─ http_local/                # Local HTTP 基础实验
│  ├─ cpu_bound/                 # CPU-bound 反例实验
│  ├─ python_scaling/            # Python 高并发扩展实验
│  ├─ java_scaling/              # Java 21 平台线程 / 虚拟线程扩展实验
│  └─ analysis/                  # 汇总、绘图、环境信息脚本
├─ results/
│  ├─ raw/                       # 原始 CSV 数据
│  ├─ plots/                     # 绘制后的图表
│  └─ summary/                   # 摘要表与环境信息
├─ docs/                         # 补充说明文档
├─ requirements.txt              # Python 依赖
└─ README.md
```

---

## 4. 实验体系总览

本项目共包含 **5 组实验**，可以分成两类。

### 4.1 基础机制验证实验

#### 实验一：Sleep I/O 基础实验
比较：

- `asyncio + asyncio.sleep`
- `ThreadPoolExecutor + time.sleep`

目的：

- 验证在模拟等待型任务中，协程相对于线程池是否具有明显优势。
- 尽量剥离真实网络协议栈带来的额外因素，聚焦“等待型任务调度成本”。

#### 实验二：Local HTTP 基础实验
比较：

- `aiohttp + asyncio`
- `requests + ThreadPoolExecutor`

目的：

- 在更接近真实网络编程的场景下，验证协程是否仍然具有优势。
- 观察 HTTP 请求处理、协议解析、连接管理等实际开销引入后，协程优势是否收敛。

#### 实验三：CPU-bound 反例实验
比较：

- 单线程顺序执行
- 线程池执行
- `asyncio.gather` 包装执行

目的：

- 说明协程不适合纯 CPU 密集型任务。
- 强调协程的价值在于“管理等待”，而不是“自动加速计算”。

### 4.2 扩展实验

#### 实验四：Python 高并发扩展实验
比较：

- `ThreadPoolExecutor + time.sleep`
- `asyncio + asyncio.sleep`

特征：

- 固定总任务数
- 提高并发上限
- 观察 QPS、P95 延迟和峰值 RSS 随并发变化的趋势

目的：

- 研究高并发区间中 `asyncio` 与线程池各自的拐点、平台和资源成本变化。

#### 实验五：Java 21 扩展实验
比较：

- `Executors.newFixedThreadPool(...)` 平台线程
- `Executors.newVirtualThreadPerTaskExecutor()` 虚拟线程

目的：

- 从 Java 21 的角度补充“轻量级并发执行单元”的实证对照。
- 验证 virtual thread 在等待型高并发任务中的扩展性表现。

---

## 5. 运行环境

### 5.1 Python 环境

建议版本：

- Python 3.12+

安装依赖：

```bash
pip install -r requirements.txt
```

当前 `requirements.txt` 中的依赖包括：

- `aiohttp`
- `requests`
- `psutil`
- `pandas`
- `matplotlib`
- `tabulate`

### 5.2 Java 环境

Java 扩展实验需要：

- **JDK 21**

检查方式：

```bash
java -version
javac -version
```

如果要运行 Java 21 虚拟线程实验，必须确保：

- `java -version` 输出为 21
- `javac -version` 输出为 21

说明：

- `requirements.txt` 只管理 Python 依赖。
- Java 环境不写入 `requirements.txt`，而是在 README 中单独说明。

---

## 6. 快速开始

### 6.1 克隆仓库

```bash
git clone https://github.com/ZR-1N/ot-coroutine-study.git
cd ot-coroutine-study
```

### 6.2 创建并激活虚拟环境（可选但推荐）

Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 6.3 安装 Python 依赖

```bash
pip install -r requirements.txt
```

---

## 7. 各实验运行方式

### 7.1 Sleep I/O 基础实验

```bash
python -m experiments.io_sleep.run_sleep_benchmark
```

输出：

- `results/raw/sleep_io_results.csv`

---

### 7.2 Local HTTP 基础实验

先启动本地 HTTP 服务：

```bash
python -m experiments.http_local.local_server
```

再在另一个终端中运行 benchmark：

```bash
python -m experiments.http_local.run_http_benchmark
```

输出：

- `results/raw/http_local_results.csv`

---

### 7.3 CPU-bound 实验

```bash
python -m experiments.cpu_bound.run_cpu_benchmark
```

输出：

- `results/raw/cpu_bound_results.csv`

---

### 7.4 Python 高并发扩展实验

```bash
python -m experiments.python_scaling.run_scaling_benchmark
```

输出：

- `results/raw/python_scaling_results.csv`

---

### 7.5 Java 21 扩展实验

PowerShell 下运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\experiments\java_scaling\run_java_benchmark.ps1
```

输出：

- `results/raw/java_scaling_results.csv`

---

## 8. 绘图与结果汇总

### 8.1 基础实验绘图

```bash
python -m experiments.analysis.plot_results
```

生成：

- `results/plots/sleep_io_wall_time_*.png`
- `results/plots/http_local_wall_time_*.png`
- `results/plots/cpu_bound_wall_time_work_*.png`

### 8.2 扩展实验绘图

```bash
python -m experiments.analysis.plot_scaling_results
```

生成：

- `results/plots/python_scaling_qps.png`
- `results/plots/python_scaling_p95.png`
- `results/plots/python_scaling_memory.png`
- `results/plots/java_scaling_qps.png`
- `results/plots/java_scaling_p95.png`
- `results/plots/java_scaling_memory.png`

### 8.3 摘要表与环境信息

```bash
python -m experiments.analysis.make_summary_tables
python -m experiments.analysis.collect_env_info
```

生成：

- `results/summary/*.csv`
- `results/summary/*.md`
- `results/summary/environment_info.txt`
- `results/summary/environment_info.json`

---

## 9. 结果文件说明

### 9.1 `results/raw/`

保存原始实验结果 CSV，便于后续重复分析与重新绘图。

### 9.2 `results/plots/`

保存自动生成的图表，可直接用于：

- 课程报告 PDF
- LaTeX Slides
- 实验结果展示页

### 9.3 `results/summary/`

保存摘要表与环境信息，便于：

- 从原始 CSV 中提炼关键数字
- 直接用于实验报告中的总表
- 统一描述平台配置

---

## 10. 指标说明与结果解读注意事项

本项目主要使用以下指标：

- **总耗时（wall time）**：完成全部任务的实际总时间
- **吞吐量（QPS / throughput）**：单位时间完成任务数
- **峰值内存**：Python 使用 RSS 峰值，Java 使用已用堆内存峰值
- **P95 延迟**：高分位延迟，用于观察高并发区间的尾部行为

### 10.1 为什么 QPS 和内存是主证据

对于扩展实验，本项目主要把：

- **QPS**
- **峰值内存 / 已用堆内存趋势**

作为更强证据，因为它们更直接反映：

- 系统整体吞吐能力
- 高并发下的资源成本

### 10.2 为什么 P95 延迟需要谨慎解释

在固定总任务数、循环提交任务的实验设计中，任务本身会受到提交顺序影响，因此：

- P95 延迟不仅反映运行时排队
- 还会受到任务提交时刻与统一起点定义的影响

因此在本项目中：

- **P95 作为辅助观察指标**
- **QPS 和内存趋势作为主要判断依据**

### 10.3 为什么 Python 和 Java 的内存不能直接横向比较

因为两者统计口径不同：

- Python 更接近操作系统进程视角的 RSS
- Java 更接近 JVM 堆管理视角，受 GC 和堆扩缩容影响更大

因此：

- **跨语言内存图更适合看趋势**
- **不适合直接比较绝对数值**

---

## 11. 当前主要结论

结合本项目现有实验，可以得到以下结论：

1. 在 I/O 密集型任务中，协程/轻量级并发模型通常比线程池更适合高并发场景。
2. 在模拟等待型任务和真实本地 HTTP 场景中，`asyncio` 均表现出明显优势。
3. 在 CPU 密集型任务中，协程没有天然性能收益。
4. 当并发上限继续提高时，Python `asyncio` 与 Java virtual thread 都表现出更好的吞吐扩展性。
5. 轻量级并发模型的价值主要在于以更低的成本管理大量等待中的任务，而不是提升纯计算本身的速度。

---

## 12. 对应课程成果

本仓库对应课程报告主题：

> 从线程到协程：高并发 I/O 场景下轻量级并发机制的底层实现与实验分析

相关成果包括：

- 实验报告 PDF（LaTeX）
- Slides（LaTeX Beamer / TemplateMC 模板）
- 实验代码与图表素材

---

## 13. 后续可扩展方向

本项目后续还可以继续扩展：

- 在 Go 上复现扩展实验，补充 goroutine 的实证对照
- 在 C++20 真正的协程网络库上做异步 I/O 基准
- 改进高分位延迟统计方式，例如使用统一批次起点和更稳定的到达过程建模
- 增加取消传播、背压、异常传播与任务泄漏等工程问题的实验

---

## 14. License

MIT License

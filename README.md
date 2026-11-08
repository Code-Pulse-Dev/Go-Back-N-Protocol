# Go-Back-N-Protocol

**English** | [中文](#中文说明)

**Go-Back-N ARQ Experiment/Implementation Software**

A visual and interactive simulator for the Go-Back-N ARQ sliding window protocol. It models the Data Link Layer concepts of error control and flow control through a live, frame-by-frame animation.

<img width="960" height="510" alt="image" src="https://github.com/user-attachments/assets/68918d38-c9f4-4173-94a1-b7a37310fd29" />


### WHY I BUILT THIS
I built this tool while studying sliding window protocols,to visualize the practical simulation and implementation of the Go-Back-N protocol. It plays out frame by frame on a live channel, so every lost packet, every timeout, and every retransmission becomes something you can watch happen.I hope it can help you too.

### WHAT IT DOES
This is an interactive simulator of the Go-Back-N Automatic Repeat reQuest protocol. It models the sliding window mechanism used in the Data Link Layer, showing how a sender and receiver transfer data reliably over an unreliable channel. A live channel animates packets flowing between the two sides, and you can raise or lower the channel error rate to see how the protocol reacts to frame loss, frame corruption, and ACK loss.

### KEY FEATURES
* **Animated Channel:** The simulator shows an animated transmission channel, with the sender window sliding forward on each ACK and the receiver window only accepting frames in order. 
* **Color-Coded States:** Each frame is colour-coded by its current state: sending, acked, lost, corrupted, or timed-out.
* **Flexible Input:** You can type a message of up to i.e thirteen characters (each character becomes one packet), or enter a packet count i.e between one and thirteen (packets are labelled A, B, C, etc.).
* **Adjustable Parameters:** Window size, timeout duration, and channel error rate are all adjustable before each run.
* **Real-time Tracking:** The interface tracks frames sent, frames acked, retransmissions, timeouts, and efficiency while the simulation runs.
* **Graphs & Logs:** The Run Tests button opens a window with a history table and graphs comparing efficiency, retransmissions, and timeouts. Every event is also written to a transmission log panel.

### GETTING STARTED
To run this project you need at least **Python 3.10 or higher**, **Tkinter** (bundled with most Python installations), and **Matplotlib** for the graphs window.

1. Clone the repository using 'git clone'.
2. Navigate into the folder.
3. Install the only external dependency with 'pip install matplotlib'.
4. Launch the app by running 'python main.py'.
5. On the welcome screen, click **CLICK HERE TO ENTER THE SOFTWARE**. On the next page, click **ENTER EXPERIMENT PLATFORM**.


<img width="960" height="509" alt="image" src="https://github.com/user-attachments/assets/3a64ca57-ebd6-46b7-aeb7-25c2c8c4985f" />



  <img width="960" height="512" alt="image" src="https://github.com/user-attachments/assets/b6a33719-55d1-405b-9202-9e1c1c5c3dbd" />


### PROJECT STRUCTURE
The project has five main files:
* 'main.py': The entry point and handles the welcome page, intro page, and navigation.
* 'experiment.py': Contains the simulation engine, the full interface, animation logic, and the graph window.
* 'packet.py': Defines the Packet class with helpers for converting packets to and from JSON.
* 'checksum.py': Contains the checksum functions used to detect corrupted frames.
* 'config.json': Generated automatically at runtime and stores your last-used settings.

### USAGE GUIDE
* **Step 1: Provide Data.** Click **Enter Data** and choose one of two input modes: type a message (up to 13 chars) or enter packets number (1-13).
* **Step 2: Configure Protocol.** Use **Set Window Size**, **Set Timeout**, and **Set Channel Error Rate** to choose your parameters.
* **Step 3: Run Simulation.** Press **START SIMULATION**. If a timeout happens, the simulation pauses and **RESUME** becomes available,so you can click it. **STOP** halts the current run and records it in the history. **CLEAR ALL RESET** wipes the state, data, and history.
* **Step 4: Look at Results.** Click **Run Tests** in the top bar to open a window showing a history table and graphs comparing efficiency, retransmissions, and timeouts against the error rate.

### HOW THE PROTOCOL WORKS
The sender keeps a sliding window of size N and sends frames in order, up to N frames ahead of the last acknowledged one. A timer is started for the oldest unacknowledged frame. If the timer runs out before an ACK arrives, the sender goes back to the base sequence number and **retransmits the entire window**. 

The receiver only accepts frames that arrive in order. Frames that arrive out of order are quietly discarded, with no negative acknowledgement, because Go-Back-N relies on the sender's timeout to recover. The receiver sends cumulative ACKs for the highest in-order frame it has.

**Error Mapping:**
* **0%:** Clean transmission.
* **1% - 15%:** Occasional frame loss.
* **16% - 30%:** Frequent ACK loss.
* **31% - 50%:** Every window has one corrupted frame.
* **51% - 70%:** Two different errors per window.
* **71% - 100%:** Window collapse (retransmission happens forever).

### PERFORMANCE METRICS
The simulator tracks five numbers:
1. **Frames Sent:** All transmissions, including retransmissions.
2. **Frames ACKed:** Frames successfully acknowledged.
3. **Retransmissions:** Frames sent again after a timeout or error.
4. **Timeouts:** How many times the sender gave up waiting for an ACK.
5. **Efficiency:** Useful frames sent divided by total frames sent, times 100.

### WHAT YOU CAN LEARN
The tool makes an abstract protocol easier to picture. You can watch the sliding window move forward and reset, see how one lost frame wastes an entire window, compare window sizes and their effect on throughput, watch efficiency drop as the error rate rises, and see where Go-Back-N breaks down.

### TECH STACK
* **Language:** Python 3.10+
* **Interface:** Tkinter + ttk
* **Graphs:** Matplotlib
* **Storage:** JSON


### CONTRIBUTING & LICENSE
Please contact the author before using, modifying, or distributing this project.
See the LICENSE file for the copyright and permission notice.

### AUTHOR
**MUZANENHAMO MALON**

If this project helped you understand Go-Back-N ARQ, consider giving it a star on GitHub.

Built in Python.

--------------------------------------------

## 中文说明

这是一个基于 Python 开发的 Go-Back-N (后退N帧) ARQ 协议可视化交互模拟器。它通过实时、逐帧的动画，生动地展示了数据链路层中的差错控制和流量控制机制。


<img width="960" height="510" alt="image" src="https://github.com/user-attachments/assets/68918d38-c9f4-4173-94a1-b7a37310fd29" />


### 为什么做这个项目？
我在学习滑动窗口协议时开发了这个工具，目的是为了直观地模拟和实现 Go-Back-N 协议的实际运行过程。丢包、超时、重传这些抽象概念，全都能变成肉眼可见的动画。希望它也能帮到正在学习网络协议的你们。

### 功能简介
这是一个交互式的 Go-Back-N ARQ 模拟器。它模拟了数据链路层的滑动窗口机制，展示了发送端和接收端如何在一个不可靠的信道上实现可靠传输。你可以随时调高或调低信道的误码率，观察协议面对帧丢失，帧损坏和 ACK 丢失时的反应。发送窗口会随着 ACK 的到达向前滑动，而接收窗口只按序接收。每个数据帧都有颜色编码（如发送中，已确认，丢失，损坏，超时），一目了然。

### 核心特性
*   **双模式数据输入**：可以输入最多 13 个字符（每个字符化为一个数据包），或者直接指定 1-13 之间的数据包数量（自动命名为 A, B, C...）。
*   **参数可调**：每次运行前，你可以自由调整窗口大小，超时时间和信道误码率。
*   **实时数据追踪**：界面实时统计发送帧数，确认帧数，重传次数，超时次数和传输效率。
*   **可视化报告**：多次运行后，点击“Run Tests”可以查看历史数据表，并通过图表直观对比不同误码率下的效率，重传和超时情况。所有的底层事件都会输出到传输日志面板中。

### 快速开始
**环境要求**：Python 3.10+，Tkinter（通常随 Python 自带），Matplotlib（用于绘制图表）。
**安装与运行**：
1. 克隆仓库并进入项目目录。
2. （可选）创建并激活 Python 虚拟环境。
3. 安装依赖：pip install matplotlib
4. 运行程序：python main.py
5. 在欢迎界面点击“CLICK HERE TO ENTER THE SOFTWARE”，进入后点击“ENTER EXPERIMENT PLATFORM”。在左侧面板设置好参数，点击“START SIMULATION”即可开始。

<img width="960" height="509" alt="image" src="https://github.com/user-attachments/assets/3a64ca57-ebd6-46b7-aeb7-25c2c8c4985f" />


   <img width="960" height="512" alt="image" src="https://github.com/user-attachments/assets/a99de915-c12b-4c8e-bd6e-b750a1d76d7a" />


### 项目结构
项目包含五个主要文件，各司其职：
*   main.py：程序入口，负责欢迎页，介绍页以及页面间的路由。
*   experiment.py：核心模拟引擎，包含完整的 UI 界面，动画逻辑和图表生成。
*   packet.py：定义 Packet 类，以及数据包与 JSON 格式互转的工具函数。
*   checksum.py：实现简单的字节和校验（byte-sum checksum），用于检测损坏帧。
*   config.json：程序运行时自动生成，用于保存你上一次的参数设置。

### 使用指南
*   **第一步：输入数据**。点击“Enter Data”，输入一段最多 13 个字符的消息，或者输入 1-13 的数据包数量。
*   **第二步：配置协议**。设置窗口大小，发送端等待 ACK 的超时时间，以及 0-100% 的信道误码率。
*   **第三步：运行模拟**。点击“START SIMULATION”开始。发生超时时，程序会暂停，你可以点击“RESUME”继续观察；点击“STOP”结束当前运行并记录到历史；点击“CLEAR ALL RESET”清除所有状态和数据。
*   **第四步：查看结果**。点击顶部的“Run Tests”，查看历史数据表以及效率，重传，超时随误码率变化的对比图表。

### 协议工作原理
发送端维护一个大小为 N 的滑动窗口，按序发送最多 N 个未被确认的帧。当最早的未确认帧定时器超时时，发送端会回退到基础序列号，并**重传整个窗口**（这就是 Go-Back-N 的核心思想）。
接收端只接收按序到达的帧。乱序到达的帧会被静默丢弃（不发 NAK），完全依赖发送端超时来恢复。接收端会对按序到达的最高帧发送累积 ACK；如果收到重复帧，则重发最后一次的 ACK，这样即使 ACK 丢失也能最终恢复。

**模拟器的误码机制**：
为了保证每次运行结果可复现且必定结束，模拟器设定了固定的按窗口错误映射：
*   0%：完美传输
*   1%-15%：偶尔丢帧
*   16%-30%：频繁 ACK 丢失（恢复成本低）
*   31%-50%：每个窗口损坏一帧
*   51%-70%：每个窗口出现两种不同错误
*   71%-100%：**窗口崩溃 (Window Collapse)**。协议陷入无限重传，直观展示协议失效的场景。

### 性能指标
模拟器会实时追踪五个数据场景或情况：
*   **已发送帧数**：包含重传在内的所有传输。
*   **已确认帧数**：成功收到 ACK 的帧数。
*   **重传次数**：超时或出错后重发的帧数。
*   **超时次数**：发送端放弃等待 ACK 的次数。
*   **效率**：（有效帧数 / 总发送帧数）× 100%，即大致的吞吐量。

### 你能学到什么？
这个工具可以把抽象的网络协议具象化。你可以看到：窗口是如何滑动的；一个丢帧是如何导致整个窗口被浪费的；窗口大小如何影响吞吐量；误码率上升时效率如何暴跌；以及 Go-Back-N 协议在什么情况下会崩溃，从而理解为什么后来会发明 Selective Repeat (选择重传) 协议。

### 技术栈
*   **语言**：Python 3.10+
*   **UI 界面**：Tkinter (窗口，画布，按钮) + ttk (历史表格)
*   **图表**：Matplotlib + FigureCanvasTkAgg (嵌入 Tkinter 窗口)
*   **数据存储**：JSON (数据包和配置文件)



### 贡献与许可
如需使用，修改或分发本项目，请先联系作者。
详情请参阅 LICENSE 文件。

### 作者
**马龙**

如果这个项目帮你搞懂了 Go-Back-N ARQ，欢迎在 GitHub 上点个 Star。

基于 Python 构建。

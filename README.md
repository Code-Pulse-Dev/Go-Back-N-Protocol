Go-Back-N ARQ Experiment/Implementation Software

A visual simulator for the Go-Back-N ARQ sliding window protocol that I built as a project to practice and better understand Data Link Layer concepts, especially error control and flow control.

WHY I BUILT THIS

I built this tool while studying sliding window protocols,to see the Go-Back-N protocol actually running.It plays out frame by frame on a live channel,so every lost packet,every timeout,and every retransmission becomes something you can watch happen.I hope it helps other students too.

WHAT IT DOES

This is an interactive simulator of the Go-Back-N Automatic Repeat reQuest protocol. It models the sliding window mechanism used in the Data Link Layer,showing how a sender and receiver transfer data reliably over an unreliable channel.A live channel animates packets flowing between the two sides,and you can raise or lower the channel error rate to see how the protocol reacts to frame loss,frame corruption,and ACK loss.

KEY FEATURES

The simulator shows an animated transmission channel,with the sender window sliding forward on each ACK and the receiver window only accepting frames in order.Each frame is colour-coded by its current state: sending,acked,lost, corrupted,or timed-out.

You can provide input in two ways.You can type a message of up to thirteen characters,where each character becomes one packet,or you can enter a packet count between one and thirteen and the packets are labelled A, B, C, and so on.Window size, timeout duration, and channel error rate are all adjustable before each run.

The interface tracks frames sent,frames acked, retransmissions,timeouts,and efficiency while the simulation runs.After several runs,the Run Tests button opens a window with a history table and graphs comparing efficiency,retransmissions,and timeouts across error rates.Every sender, receiver,and channel event is also written to a transmission log panel.

GETTING STARTED

To run this project you need Python 3.10 or higher,Tkinter (which comes bundled with most Python installations),and Matplotlib for the graphs window.

Clone the repository using git clone with the repository URL,then navigate into the folder.Optionally,you can create and activate a virtual environment using the standard Python venv commands for your operating system.Then install the only external dependency with pip install matplotlib.

To launch the app,run python main.py from the project folder.On the welcome screen, click CLICK HERE TO ENTER THE SOFTWARE. On the next page,click ENTER EXPERIMENT PLATFORM.Set your parameters in the left panel and press START SIMULATION to begin.

PROJECT STRUCTURE

The project has five main files.main.py is the entry point and handles the welcome page,the intro page,and navigation between them.experiment.py contains the simulation engine,the full interface,the animation logic,and the graph window.packet.py defines the Packet class with helpers for converting packets to and from JSON. checksum.py has the checksum functions used to detect corrupted frames.config.json is generated automatically at runtime and stores your last-used settings.

Each file is kept small and focused on one job.main.py only builds the Tkinter window and routes navigation.experiment.py handles the entire simulation:the sender and receiver canvases,the channel animation, timeout handling,the Go-Back-N logic,the transmission log,and the matplotlib graphs. packet.py models a network packet with a sequence number,data,and a checksum. checksum.py implements the simple byte-sum checksum used to detect corruption.

USAGE GUIDE

The first step is to provide data.Click Enter Data and choose one of two input modes:type a message of up to thirteen characters (each character becomes one packet),or enter a packet count between one and thirteen (packets are labelled A, B, C, and so on).

The second step is to configure the protocol.Use Set Window Size to choose how many frames you would like to send.Use Set Timeout to choose how long the sender waits for an ACK before retransmitting.Use Set Channel Error Rate to choose a bit-error probability between zero and one hundred percent.

The third step is to run the simulation. Press START SIMULATION to begin.If a timeout happens,the simulation pauses and RESUME becomes available so you can see what happened before continuing.STOP halts the current run and records it in the history.CLEAR ALL RESET wipes the state, data,and history.

The fourth step is to look at the results. Click Run Tests in the top bar to open a window showing a history table of every run you have done,plus graphs comparing efficiency,retransmissions,and timeouts against the error rate.

HOW THE PROTOCOL WORKS

The sender keeps a sliding window of size N and sends frames in order,up to N frames ahead of the last acknowledged one.A timer is started for the oldest unacknowledged frame.If the timer runs out before an ACK arrives,the sender goes back to the base sequence number and retransmits the entire window.That full-window retransmission is the main idea behind Go-Back-N.

The receiver only accepts frames that arrive in order.Frames that arrive out of order are quietly discarded,with no negative acknowledgement,because Go-Back-N relies on the sender's timeout to recover. The receiver sends cumulative ACKs for the highest in-order frame it has,and if it sees a duplicate frame it sends the last ACK again so a lost ACK can eventually recover.

The simulator uses a fixed per-window error mapping so every run is reproducible and always finishes.At zero percent error rate the transmission is clean.Between one and fifteen percent there is occasional frame loss.Between sixteen and thirty percent there is frequent ACK loss,which is cheap to recover from.Between thirty-one and fifty percent every window has one corrupted frame.Between fifty-one and seventy percent there are two different errors per window.Between seventy-one and one hundred percent the protocol enters window collapse,where retransmission happens forever and the simulation shows the protocol breaking down.

PERFORMANCE METRICS

The simulator tracks five numbers.Frames Sent counts all transmissions,including retransmissions.Frames ACKed counts frames that were successfully acknowledged. Retransmissions counts frames sent again after a timeout or error.Timeouts counts how many times the sender gave up waiting for an ACK.Efficiency is useful frames sent divided by total frames sent,times one hundred,which gives a rough throughput percentage.

WHAT YOU CAN LEARN FROM IT

The tool is meant to make an abstract protocol easier to picture.You can watch the sliding window move forward and reset, see how one lost frame wastes an entire window,compare window sizes and their effect on throughput,watch efficiency drop as the error rate rises,and see where Go-Back-N breaks down and why protocols like Selective Repeat were invented.

TECH STACK

The project is written in Python 3.10 or higher.The interface uses Tkinter for windows,canvases,and buttons,and ttk for the history table.Graphs use Matplotlib through FigureCanvasTkAgg,which lets matplotlib figures live inside a Tkinter window.Packets and config files are stored as JSON.

WHAT I MIGHT ADD LATER

Things I would like to add are a Selective Repeat mode for comparison,exporting the simulation history as CSV,unit tests for the checksum and packet modules,showing corruption at the bit level,other languages for the interface,and a real socket-based sender and receiver mode so it can talk over an actual network.

CONTRIBUTING

Please contact the author before using, modifying, or distributing this project.

LICENSE

All rights reserved. See the LICENSE file for the copyright and permission notice.

AUTHOR

MUZANENHAMO MALON

If this project helped you understand Go-Back-N ARQ,consider giving it a star on GitHub.

Built in Python.

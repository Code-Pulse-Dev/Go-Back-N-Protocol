import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import time
import random

# ====================== MOCK DEPENDENCIES ======================
class Packet:
    def __init__(self, seq_num, data, checksum):
        self.seq_num = seq_num
        self.data = data
        self.checksum = checksum

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(json_str):
        d = json.loads(json_str)
        return Packet(d['seq_num'], d['data'], d['checksum'])

def calculate_checksum(data):
    return sum(ord(c) for c in data) % 256

def verify_checksum(data, checksum):
    return calculate_checksum(data) == checksum

def save_config(config_dict):
    pass

# ====================== COLORS ======================
BG_BLUE = "#1f4e79"
WHITE = "#ffffff"
GREEN = "#27ae60"
RED = "#e74c3c"
YELLOW = "#f39c12"
DARK_BG = "#0d3b5e"
ORANGE = "#e67e22"
BLUE_SEND = "#3498db"
PURPLE = "#9b59b6"
GRAY = "#555555"
DARK_CANVAS = "#0a1628"
LIGHT_BLUE = "#5dade2"
WINDOW_HIGHLIGHT = "#00ffff"
PINK = "#e056a0"
YELLOW_PKT = "#e8b800"

def show_experiment_page(root, config, go_back_callback):
    for widget in root.winfo_children():
        widget.destroy()
    config["message"] = ""
    config["window_size"] = None
    config["timeout"] = None
    config["error_rate"] = None
    config["input_mode"] = "message"  # "message" or "packets"
    config["packet_count"] = 0

    root.state('zoomed')

    frame_states = {}
    received_frames = {}
    discarded_frames = set()
    base_val = 0
    next_to_send = 0
    total_sent = 0
    total_retrans = 0
    total_timeouts = 0
    timer_start_time = None
    last_progress_time = None
    animating = False
    paused_by_error = False
    waiting_logged = False
    timeout_pending = False
    current_window_errors = {}

    simulation_history = []

    # ====================== CONFIG DIALOGS ====================
    def enter_data():
        """Choice dialog: enter a text message OR specify a packet count."""
        dlg = tk.Toplevel(root)
        dlg.title("Enter Data")
        dlg.geometry("440x230")
        dlg.configure(bg=BG_BLUE)
        dlg.transient(root)
        dlg.grab_set()
        dlg.resizable(False, False)
        tk.Label(dlg, text="Select Input Type", font=("Segoe UI", 15, "bold"),
                 bg=BG_BLUE, fg=WHITE).pack(pady=(22, 6))
        tk.Label(dlg, text="Choose how you want to provide data for the simulation.",
                 font=("Segoe UI", 9), bg=BG_BLUE, fg="#aabbcc").pack()
        row = tk.Frame(dlg, bg=BG_BLUE)
        row.pack(pady=22)
        def _open_msg():
            dlg.destroy(); _enter_text_message()
        def _open_pkt():
            dlg.destroy(); _enter_packet_count()
        tk.Button(row, text="✉  Enter a Message",   font=("Segoe UI", 11, "bold"),
                  bg="#2980b9", fg=WHITE, width=17, height=2, relief="raised", bd=2,
                  command=_open_msg).pack(side="left", padx=12)
        tk.Button(row, text="📦  Enter Packet Count", font=("Segoe UI", 11, "bold"),
                  bg="#8e44ad", fg=WHITE, width=17, height=2, relief="raised", bd=2,
                  command=_open_pkt).pack(side="left", padx=12)
        tk.Button(dlg, text="Cancel", font=("Segoe UI", 9), bg="#555", fg=WHITE,
                  width=10, command=dlg.destroy).pack(pady=(0, 12))

    def _enter_text_message():
        dialog = tk.Toplevel(root)
        dialog.title("Enter Message")
        dialog.geometry("500x380")
        dialog.configure(bg=BG_BLUE)
        dialog.transient(root)
        dialog.grab_set()
        tk.Label(dialog, text="Enter Your Message", font=("Segoe UI", 16, "bold"),
                 bg=BG_BLUE, fg=WHITE).pack(pady=15)
        tk.Label(dialog, text="Type or paste your message below:",
                 font=("Segoe UI", 10), bg=BG_BLUE, fg=WHITE).pack()
        text_widget = tk.Text(dialog, height=8, width=50, font=("Consolas", 11))
        text_widget.pack(pady=10, padx=20)
        prev = config.get("message", "") if config.get("input_mode") == "message" else ""
        text_widget.insert("1.0", prev)
        tk.Label(dialog, text="Each character is one packet/frame.",
                 font=("Segoe UI", 9, "bold"), bg=BG_BLUE, fg="#f39c12").pack(padx=20, pady=(0,5))
        def save_msg():
            msg = text_widget.get('1.0', 'end-1c').strip()
            if len(msg) < 1:
                messagebox.showwarning("Empty", "Please enter a message.", parent=dialog); return
            if len(msg) > 13:
                messagebox.showerror("Too Long",
                    f"Maximum for the panel window display is 13 characters. You entered {len(msg)}.", parent=dialog); return
            config['message']      = msg
            config['input_mode']   = 'message'
            config['packet_count'] = len(msg)
            save_config(config)
            update_bottom_info_bar()
            update_settings_display()
            dialog.destroy()
            messagebox.showinfo("Saved", f"Message saved ({len(msg)} characters / packets)")
            root.after(50, draw_top_row)
            root.after(50, draw_bottom_row)
        bf = tk.Frame(dialog, bg=BG_BLUE); bf.pack(pady=10)
        tk.Button(bf, text="Save",   font=("Segoe UI", 11, "bold"), bg=GREEN,     fg=WHITE, width=12, command=save_msg).pack(side="left", padx=5)
        tk.Button(bf, text="Cancel", font=("Segoe UI", 11),          bg="#666666", fg=WHITE, width=12, command=dialog.destroy).pack(side="left", padx=5)

    def _enter_packet_count():
        dialog = tk.Toplevel(root)
        dialog.title("Enter Packet count")
        dialog.geometry("420x270")
        dialog.configure(bg=BG_BLUE)
        dialog.transient(root)
        dialog.grab_set()
        tk.Label(dialog, text="Number of Packets", font=("Segoe UI", 15, "bold"),
                 bg=BG_BLUE, fg=WHITE).pack(pady=(20, 6))
        tk.Label(dialog, text="How many packets do you want to simulate?",
                 font=("Segoe UI", 9), bg=BG_BLUE, fg="#aabbcc").pack()
        var = tk.StringVar(value=str(config.get('packet_count') or ''))
        e = tk.Entry(dialog, textvariable=var, width=8, font=("Segoe UI", 20), justify="center")
        e.pack(pady=18); e.focus_set()
        def save_count():
            try:
                n = int(var.get().strip())
                if n < 1 or n > 13: raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Maximum for the panel window display is 13 characters. Enter a whole number from 1 to 13.", parent=dialog); return
            # Synthetic message: letters A-M, one per packet
            synthetic = ''.join(chr(ord('A') + i) for i in range(n))
            config['message']      = synthetic
            config['input_mode']   = 'packets'
            config['packet_count'] = n
            save_config(config)
            update_bottom_info_bar()
            update_settings_display()
            dialog.destroy()
            messagebox.showinfo("Saved", f"{n} packets configured.")
            root.after(50, draw_top_row)
            root.after(50, draw_bottom_row)
        bf = tk.Frame(dialog, bg=BG_BLUE); bf.pack(pady=5)
        tk.Button(bf, text="Save",   font=("Segoe UI", 11, "bold"), bg=GREEN,     fg=WHITE, width=12, command=save_count).pack(side="left", padx=5)
        tk.Button(bf, text="Cancel", font=("Segoe UI", 11),          bg="#666666", fg=WHITE, width=12, command=dialog.destroy).pack(side="left", padx=5)

    enter_message = enter_data  # keep old name working

    def load_file():
        filepath = filedialog.askopenfilename(title="Select a text file", filetypes=[("Text files", "*.txt")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config['message'] = f.read().strip()
                if len(config['message']) < 1:
                    messagebox.showwarning("Empty", "The loaded file is empty. Please use a file with 1–13 characters.")
                    config['message'] = ""
                    return
                if len(config['message']) > 13:
                    messagebox.showerror("Too Long", f"Message length exceeds the display panel limit.\nLoaded file has {len(config['message'])} characters. Please use a file with at most 13 characters to properly visualize Go-Back-N.")
                    config['message'] = ""
                    return
                save_config(config)
                update_bottom_info_bar()
                update_settings_display()
                messagebox.showinfo("Success", f"Loaded {len(config['message'])} characters")
                root.after(50, draw_top_row)
                root.after(50, draw_bottom_row)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def set_window_size():
        dialog = tk.Toplevel(root)
        dialog.title("Set Window Size")
        dialog.geometry("400x250")
        dialog.configure(bg=BG_BLUE)
        dialog.transient(root)
        dialog.grab_set()
        tk.Label(dialog, text="Window Size", font=("Segoe UI", 14, "bold"), bg=BG_BLUE, fg=WHITE).pack(pady=15)
        var = tk.StringVar()
        tk.Entry(dialog, textvariable=var, width=10, font=("Segoe UI", 18), justify="center").pack(pady=15)
        
        def save_win():
            try:
                v = int(var.get())
                if v <= 0: raise ValueError
                config['window_size'] = v
                save_config(config)
                update_bottom_info_bar()
                update_settings_display()
                dialog.destroy()
                root.after(50, draw_top_row)
                root.after(50, draw_bottom_row)
            except:
                messagebox.showwarning("Invalid", "Enter a positive integer!", parent=dialog)
        tk.Button(dialog, text="Save", font=("Segoe UI", 11, "bold"), bg=GREEN, fg=WHITE, width=12, command=save_win).pack(pady=15)

    def set_timeout():
        dialog = tk.Toplevel(root)
        dialog.title("Set Timeout")
        dialog.geometry("400x250")
        dialog.configure(bg=BG_BLUE)
        dialog.transient(root)
        dialog.grab_set()
        tk.Label(dialog, text="Timeout (seconds)", font=("Segoe UI", 14, "bold"), bg=BG_BLUE, fg=WHITE).pack(pady=15)
        var = tk.StringVar()
        tk.Entry(dialog, textvariable=var, width=10, font=("Segoe UI", 18), justify="center").pack(pady=15)
        
        def save_timeout():
            try:
                v = float(var.get())
                if v <= 0: raise ValueError
                config['timeout'] = v
                save_config(config)
                update_bottom_info_bar()
                update_settings_display()
                dialog.destroy()
            except:
                 messagebox.showwarning("Invalid", "Enter a positive number!", parent=dialog)
        tk.Button(dialog, text="Save", font=("Segoe UI", 11, "bold"), bg=GREEN, fg=WHITE, width=12, command=save_timeout).pack(pady=15)

    def set_error_rate():
        dialog = tk.Toplevel(root)
        dialog.title("Set Error Rate")
        dialog.geometry("400x280")
        dialog.configure(bg=BG_BLUE)
        dialog.transient(root)
        dialog.grab_set()
        tk.Label(dialog, text="Bit Error Rate", font=("Segoe UI", 14, "bold"), bg=BG_BLUE, fg=WHITE).pack(pady=15)
        initial = int(round(config.get("error_rate", 0.0) * 100)) if config.get("error_rate") is not None else 0
        var = tk.IntVar(value=initial)
        scale_frame = tk.Frame(dialog, bg=BG_BLUE)
        scale_frame.pack(pady=10)
        tk.Label(scale_frame, text="0%", font=("Segoe UI", 9), bg=BG_BLUE, fg=WHITE).pack(side="left")
        
        def on_scale_change(v):
            try:
                value_label.config(text=f"{int(float(v))}%")
            except Exception:
                value_label.config(text=f"{var.get()}%")
                
        s = tk.Scale(scale_frame, from_=0, to=100, orient="horizontal", variable=var, length=250, bg=BG_BLUE, fg=WHITE, command=on_scale_change)
        s.pack(side="left", padx=10)
        tk.Label(scale_frame, text="100%", font=("Segoe UI", 9), bg=BG_BLUE, fg=WHITE).pack(side="left")
        value_label = tk.Label(dialog, text=f"{var.get()}%", font=("Segoe UI", 16, "bold"), bg=BG_BLUE, fg=RED)
        value_label.pack(pady=5)
        
        def save_error():
            try:
                val = int(var.get())
                config['error_rate'] = max(0.0, min(1.0, val / 100.0))
                save_config(config)
                update_bottom_info_bar()
                update_settings_display()
                dialog.destroy()
            except Exception:
                messagebox.showwarning("Invalid", "Enter a valid error value!", parent=dialog)
        tk.Button(dialog, text="Save", font=("Segoe UI", 11, "bold"), bg=GREEN, fg=WHITE, width=12, command=save_error).pack(pady=10)

    # ==================== UI UPDATES ====================
    def view_full_message():
        if not config.get('message'): return
        dialog = tk.Toplevel(root)
        dialog.title("Full Message")
        dialog.geometry("500x350")
        dialog.configure(bg=BG_BLUE)
        dialog.transient(root)
        dialog.grab_set()
        tk.Label(dialog, text="Full Message", font=("Segoe UI", 13, "bold"), bg=BG_BLUE, fg=WHITE).pack(pady=(15, 5))
        tk.Label(dialog, text=f"({len(config['message'])} characters)", font=("Segoe UI", 9), bg=BG_BLUE, fg="#aabbcc").pack()
        txt = tk.Text(dialog, font=("Consolas", 10), bg="#1a1a2e", fg="#00ff88", wrap="word", relief="flat")
        txt.pack(fill="both", expand=True, padx=15, pady=10)
        txt.insert("1.0", config['message'])
        txt.config(state="disabled")
        tk.Button(dialog, text="Close", font=("Segoe UI", 10, "bold"), bg="#666666", fg=WHITE, width=12, command=dialog.destroy).pack(pady=(0, 15))

    def show_channel_idle():
        mid_canvas.delete("all")
        mid_canvas.update_idletasks()
        W = mid_canvas.winfo_width() or 700
        H = mid_canvas.winfo_height() or 300
        mid_canvas.create_text(W//2, H//2 - 20, text="— Transmission Channel —", fill="#1a5276", font=("Segoe UI", 16, "bold"))
        mid_canvas.create_text(W//2, H//2 + 15, text="Configure parameters on the left and press START to begin", fill="#2980b9", font=("Segoe UI", 10))

    def show_channel_complete(received_msg=""):
        mid_canvas.delete("all")
        mid_canvas.update_idletasks()
        W = mid_canvas.winfo_width() or 700
        H = mid_canvas.winfo_height() or 300
        mid_canvas.create_text(W//2, H//2 - 55, text="✓  Transmission Complete",
                                fill="#27ae60", font=("Segoe UI", 16, "bold"))
        if config.get('input_mode') == 'packets':
            n = config.get('packet_count', 0)
            line2 = f"Receiver: {len(received_frames)} / {n} packets successfully received."
        else:
            line2 = f'Receiver decoded message:  "{received_msg}"'
        mid_canvas.create_text(W//2, H//2 - 12, text=line2,
                                fill="#f0e68c", font=("Segoe UI", 13, "bold"))
        mid_canvas.create_text(W//2, H//2 + 28,
                                text="Check the Transmission Log for full details.",
                                fill="#5dade2", font=("Segoe UI", 10))
        mid_canvas.create_text(W//2, H//2 + 54,
                                text="Press  🗑 CLEAR  to reset everything.",
                                fill="#5dade2", font=("Segoe UI", 10))
        # Update receiver row canvas with summary banner
        bot_canvas.delete("summary_overlay")
        W2 = bot_canvas.winfo_width() or 700
        H2 = bot_canvas.winfo_height() or 50
        if config.get('input_mode') == 'packets':
            n = config.get('packet_count', 0)
            rtxt = f"✓  {len(received_frames)} / {n} packets successfully received"
        else:
            rtxt = f'✓  Message received:  "{received_msg}"'
        bot_canvas.create_rectangle(0, 0, W2, H2, fill="#0a2a10", outline="#27ae60",
                                    width=2, tags="summary_overlay")
        bot_canvas.create_text(W2//2, H2//2, text=rtxt, fill="#2ecc71",
                                font=("Segoe UI", 11, "bold"), tags="summary_overlay")

    def clear_all():
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear everything?\nAll entered data and displayed frames will be erased."):
            nonlocal animating, base_val, next_to_send, total_sent, total_retrans, total_timeouts, timer_start_time, paused_by_error, waiting_logged, last_progress_time, discarded_frames, timeout_pending, current_window_errors
            animating = False
            paused_by_error = False
            waiting_logged = False
            timeout_pending = False
            base_val = 0
            next_to_send = 0
            total_sent = 0
            total_retrans = 0
            total_timeouts = 0
            timer_start_time = None
            last_progress_time = None
            current_window_errors.clear()
            config["message"] = ""
            config["window_size"] = None
            config["timeout"] = None
            config["error_rate"] = None
            frame_states.clear()
            received_frames.clear()
            discarded_frames.clear()
            simulation_history.clear()
            save_config(config)
            update_bottom_info_bar()
            update_settings_display()
            log_text.delete('1.0', 'end')
            frames_sent_label.config(text="Sent: 0")
            frames_acked_label.config(text="ACKed: 0")
            retrans_label.config(text="Retransmitted: 0")
            timeout_count_label.config(text="Timeouts: 0")
            efficiency_label.config(text="Efficiency: 0%")
            recv_count_label.config(text="Recv: 0/0")
            resume_btn.config(state=tk.DISABLED)
            update_progress_bar(0)
            set_status("ready", "Ready")
            draw_top_row()
            draw_bottom_row()
            root.after(100, show_channel_idle)

    def update_bottom_info_bar():
        msg = config.get('message', '')
        ws = config.get('window_size')
        to = config.get('timeout')
        if len(msg) > 20:
            bottom_msg_val.config(text=msg[:20] + '...', fg="#5dade2", cursor="hand2")
            bottom_msg_val.bind("<Button-1>", lambda e: view_full_message())
        else:
            bottom_msg_val.config(text=(msg if msg else '-'), fg=WHITE, cursor="")
            bottom_msg_val.unbind("<Button-1>")
        bottom_ws_val.config(text=str(ws) if ws is not None else '-')
        bottom_to_val.config(text=f"{to}s" if to is not None else '-')

    # ==================== GRAPHS & TABLE WINDOW ====================
    def show_graphs_window():
        if not simulation_history:
            messagebox.showinfo("No Data", "No simulation data available yet. Run some simulations first!")
            return

        graph_win = tk.Toplevel(root)
        graph_win.title("Simulation Test Results")
        graph_win.geometry("1300x750")
        graph_win.configure(bg=DARK_BG)
        graph_win.transient(root)

        table_container = tk.Frame(graph_win, bg=DARK_BG)
        table_container.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(table_container, text="SIMULATION HISTORY", font=("Segoe UI", 14, "bold"), bg=DARK_BG, fg=WHITE).pack(anchor="w", pady=(0, 10))

        columns = ("id", "error_rate", "window_size", "sent", "retransmitted", "timeouts", "efficiency")
        tree = ttk.Treeview(table_container, columns=columns, show="headings", height=5)
        
        headings = {
            "id": "#", "error_rate": "Error Rate (%)", "window_size": "Window Size", 
            "sent": "Frames Sent", "retransmitted": "Retransmissions", 
            "timeouts": "Timeouts", "efficiency": "Efficiency (%)"
        }
        widths = {"id": 40, "error_rate": 100, "window_size": 90, "sent": 90, "retransmitted": 120, "timeouts": 80, "efficiency": 100}

        for col in columns:
            tree.heading(col, text=headings[col], anchor="center")
            tree.column(col, width=widths[col], anchor="center", minwidth=widths[col])

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")

        for idx, h in enumerate(simulation_history, 1):
            def _fmt(v, decimals=0):
                if v == float('inf'): return "∞"
                if decimals: return f"{v:.{decimals}f}"
                return str(int(v)) if isinstance(v, float) else str(v)
            tree.insert("", "end", values=(
                idx,
                f"{h['error_rate']*100:.1f}%",
                h['window_size'],
                _fmt(h['sent']),
                _fmt(h['retransmitted']),
                _fmt(h['timeouts']),
                f"{h['efficiency']:.1f}%" if h['efficiency'] != float('inf') else "0.0%"
            ))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#112233", foreground=WHITE, fieldbackground="#112233", borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#1a3a5c", foreground=WHITE, font=("Segoe UI", 10, "bold"), borderwidth=1, relief="flat")
        style.map("Treeview", background=[("selected", BLUE_SEND)], foreground=[("selected", WHITE)])

        graphs_container = tk.Frame(graph_win, bg=DARK_BG)
        graphs_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        sorted_history = sorted(simulation_history, key=lambda x: x['error_rate'])
        error_rates = [h['error_rate'] * 100 for h in sorted_history]
        efficiencies = [h['efficiency'] for h in sorted_history]
        # Replace inf retransmissions/timeouts with max_finite * 1.3 so the bar is just
        # slightly taller than the tallest real bar — annotated with ∞, not a fake number.
        _max_finite_r = max((h['retransmitted'] for h in sorted_history if h['retransmitted'] != float('inf')), default=10)
        _max_finite_t = max((h['timeouts'] for h in sorted_history if h['timeouts'] != float('inf')), default=5)
        retransmissions = [h['retransmitted'] if h['retransmitted'] != float('inf') else _max_finite_r * 1.3 for h in sorted_history]
        timeouts_raw    = [h['timeouts']      if h['timeouts']      != float('inf') else _max_finite_t * 1.3 for h in sorted_history]
        inf_retrans = [h['retransmitted'] == float('inf') for h in sorted_history]
        inf_timeouts = [h['timeouts'] == float('inf') for h in sorted_history]
        W = sorted_history[0]['window_size'] if sorted_history else 4

        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            timeouts_list = timeouts_raw  # already computed above with inf→large-value substitution

            # ── Helper: style one axis consistently ──────────────────────
            def _style_ax(ax, title, xlabel, ylabel):
                ax.set_facecolor("#0d1f33")
                ax.set_title(title, color=WHITE, fontsize=11, fontweight="bold", pad=12)
                ax.set_xlabel(xlabel, color="#aabbcc", fontsize=9, labelpad=8)
                ax.set_ylabel(ylabel, color="#aabbcc", fontsize=9, labelpad=8)
                ax.tick_params(colors=WHITE, labelsize=8, length=4)
                ax.grid(True, color="#1e3a5f", linewidth=0.6, linestyle="--", alpha=0.7)
                for spine in ax.spines.values():
                    spine.set_color("#2a4a6a")
                    spine.set_linewidth(0.8)

            def _annotate(ax, xs, ys, color, fmt="{:.1f}"):
                for x, y in zip(xs, ys):
                    ax.annotate(fmt.format(y),
                                xy=(x, y), xytext=(0, 7),
                                textcoords="offset points",
                                ha="center", va="bottom",
                                color=color, fontsize=7, fontweight="bold")

            fig = Figure(figsize=(14, 6), dpi=100)
            fig.patch.set_facecolor(DARK_BG)
            fig.subplots_adjust(left=0.09, right=0.97, top=0.88, bottom=0.18,
                                wspace=0.52, hspace=0.4)

            x_left = min(error_rates) - max(5, (max(error_rates) - min(error_rates)) * 0.05) if error_rates else 0

            def _draw_y_refs(ax, xs, ys, line_color, labels):
                """Draw dashed reference lines from each point to the y-axis.
                Colours the existing tick if the value is already there; otherwise annotates beside the axis."""
                import math
                # Collect all y tick positions matplotlib already placed
                existing = [round(t, 4) for t in ax.get_yticks()]
                seen_y = set()
                for x, y, lbl in zip(xs, ys, labels):
                    yr = round(y, 4)
                    # dashed line from y-axis edge to the point
                    ax.plot([x_left, x], [y, y],
                            color=line_color, linewidth=0.8, linestyle="--", alpha=0.55, zorder=1)
                    if yr in seen_y:
                        continue
                    seen_y.add(yr)
                    if yr in existing:
                        # colour the matching tick label instead of writing a new one
                        for tl in ax.get_yticklabels():
                            try:
                                if round(float(tl.get_text().replace('%','')), 4) == yr:
                                    tl.set_color(line_color)
                                    tl.set_fontweight("bold")
                                    tl.set_fontsize(8)
                            except ValueError:
                                pass
                    else:
                        ax.annotate(lbl,
                                    xy=(x_left, y), xytext=(-4, 0),
                                    textcoords="offset points",
                                    ha="right", va="center",
                                    color=line_color, fontsize=7, fontweight="bold")

            # ── Plot 1: Efficiency vs Error Rate ─────────────────────────
            ax1 = fig.add_subplot(131)
            _style_ax(ax1, "Efficiency vs Error Rate",
                      "Error Rate (%)", "Efficiency (%)")
            ax1.set_ylim(-5, 110)
            ax1.plot(error_rates, efficiencies, color="#2ecc71", linewidth=2.2,
                     marker="o", markersize=7, markerfacecolor="#27ae60",
                     markeredgecolor="white", markeredgewidth=0.8, zorder=3)
            _draw_y_refs(ax1, error_rates, efficiencies, "#2ecc71",
                         [f"{y:.0f}%" for y in efficiencies])

            # ── Plot 2: Retransmissions vs Error Rate ────────────────────
            ax2 = fig.add_subplot(132)
            _style_ax(ax2, "Retransmissions vs Error Rate",
                      "Error Rate (%)", "Retransmissions")
            ax2.bar(error_rates, retransmissions, width=max(2, (max(error_rates)-min(error_rates)+4)/len(error_rates)*0.7) if len(error_rates)>1 else 4,
                    color="#e67e22", edgecolor="#d35400", linewidth=0.6, alpha=0.85, zorder=3)
            ax2.plot(error_rates, retransmissions, color="#3498db", linewidth=1.5,
                     marker="s", markersize=5, markerfacecolor="#3498db",
                     markeredgecolor="white", markeredgewidth=0.6, zorder=4)
            _draw_y_refs(ax2, error_rates, retransmissions, "#3498db",
                         ["\u221e" if inf else f"{y:.0f}" for y, inf in zip(retransmissions, inf_retrans)])

            # ── Plot 3: Timeouts vs Error Rate ───────────────────────────
            ax3 = fig.add_subplot(133)
            _style_ax(ax3, "Timeouts vs Error Rate",
                      "Error Rate (%)", "Timeouts")
            ax3.bar(error_rates, timeouts_list, width=max(2, (max(error_rates)-min(error_rates)+4)/len(error_rates)*0.7) if len(error_rates)>1 else 4,
                    color="#9b59b6", edgecolor="#7d3c98", linewidth=0.6, alpha=0.85, zorder=3)
            ax3.plot(error_rates, timeouts_list, color="#27ae60", linewidth=1.5,
                     marker="^", markersize=5, markerfacecolor="#27ae60",
                     markeredgecolor="white", markeredgewidth=0.6, zorder=4)
            _draw_y_refs(ax3, error_rates, timeouts_list, "#3498db",
                         ["\u221e" if inf else f"{y:.0f}" for y, inf in zip(timeouts_list, inf_timeouts)])

            canvas = FigureCanvasTkAgg(fig, master=graphs_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except ImportError:
            tk.Label(graphs_container,
                     text="Matplotlib is required. Install with: pip install matplotlib",
                     fg=RED, bg=DARK_BG, font=("Segoe UI", 12)).pack(pady=50)

    # ==================== FRAME ROW DRAWING ====================
    FRAME_W = 46
    FRAME_H = 34
    FRAME_GAP = 4
    ROW_PAD = 10

    def _frame_x(seq):
        return ROW_PAD + seq * (FRAME_W + FRAME_GAP) + FRAME_W // 2

    def _scroll_frac(seq, total, canvas_w):
        total_w = ROW_PAD + total * (FRAME_W + FRAME_GAP) + ROW_PAD
        px = _frame_x(seq) 
        return max(0.0, min(1.0, (px - canvas_w // 2) / max(total_w, 1))), total_w

    def draw_top_row(event=None):
        top_canvas.delete("all")
        message = config.get('message', '')
        if not message:
            top_canvas.create_text(10, FRAME_H//2+4, text="Enter message & click START", fill="#666666", font=("Segoe UI", 10), anchor="w")
            return
        total = len(message)
        WINDOW_SIZE = config.get('window_size') or 4
        base = base_val
        total_w = ROW_PAD + total * (FRAME_W + FRAME_GAP) + ROW_PAD
        top_canvas.configure(scrollregion=(0, 0, max(total_w, top_canvas.winfo_width()), FRAME_H + 16))
        if base < total:
            wx1 = ROW_PAD + base * (FRAME_W + FRAME_GAP) - 3
            wx2 = ROW_PAD + min(base + WINDOW_SIZE, total) * (FRAME_W + FRAME_GAP) - FRAME_GAP + 3
            top_canvas.create_rectangle(wx1, 2, wx2, FRAME_H + 12, outline=WINDOW_HIGHLIGHT, width=3)
        for i in range(total):
            x1 = ROW_PAD + i * (FRAME_W + FRAME_GAP)
            y1, x2, y2 = 6, x1 + FRAME_W, 6 + FRAME_H
            state = frame_states.get(i, "waiting")
            if state == "acked" or i < base:
                color = GREEN
            elif state in ["error", "lost", "timeout"]:
                color = RED
            elif state == "sending":
                color = BLUE_SEND
            elif i < base + WINDOW_SIZE:
                color = "#3a6bc4"
            else:
                color = "#2a3a6a"
            top_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=WHITE, width=1)
            top_canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(i), fill=WHITE, font=("Consolas", 9, "bold"))
        frac, _ = _scroll_frac(base, total, top_canvas.winfo_width() or 700)
        top_canvas.xview_moveto(frac)

    def draw_bottom_row(event=None):
        bot_canvas.delete("all")
        message = config.get('message', '')
        if not message: return
        total = len(message)
        total_w = ROW_PAD + total * (FRAME_W + FRAME_GAP) + ROW_PAD
        bot_canvas.configure(scrollregion=(0, 0, max(total_w, bot_canvas.winfo_width()), FRAME_H + 16))
        for i in range(total):
            x1 = ROW_PAD + i * (FRAME_W + FRAME_GAP)
            y1, x2, y2 = 6, x1 + FRAME_W, 6 + FRAME_H
            
            if i in received_frames:
                color, label, text_color = GREEN, str(i), WHITE 
            elif frame_states.get(i) == "lost":
                color, label, text_color = RED, "✗", WHITE
            elif i in discarded_frames:
                color, label, text_color = "#2a3060", "✗", RED
            elif frame_states.get(i) == "error":
                color, label, text_color = RED, "✗", WHITE
            else:
                color, label, text_color = "#2a3060", str(i), WHITE
                
            bot_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#aaaaaa", width=1)
            bot_canvas.create_text((x1+x2)//2, (y1+y2)//2, text=label, fill=text_color, font=("Consolas", 9, "bold"))
        frac, _ = _scroll_frac(base_val, total, bot_canvas.winfo_width() or 700)
        bot_canvas.xview_moveto(frac)

    # ==================== CHANNEL ANIMATION ====================
    PKT_W, PKT_H = 42, 26

    def _canvas_x(seq):
        raw = _frame_x(seq)
        try:
            x0 = top_canvas.xview()[0]
            total = len(config.get('message', '') or ' ')
            total_w = ROW_PAD + total * (FRAME_W + FRAME_GAP) + ROW_PAD
            return raw - x0 * total_w
        except Exception:
            return raw

    def _launch_pkt_lost(tag, seq_num, x1, y1, x2, y2, steps=48, delay=22):
        mid_canvas.delete(tag)
        mid_canvas.delete(tag + "_lost_label")
        r = mid_canvas.create_rectangle(x1 - PKT_W//2, y1 - PKT_H//2, x1 + PKT_W//2, y1 + PKT_H//2,
                                        fill=PINK, outline="white", width=2, tags=tag)
        t = mid_canvas.create_text(x1, y1, text=str(seq_num), fill="white",
                                   font=("Consolas", 11, "bold"), tags=tag)
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        halfway = steps // 2

        def _step(i, cx, cy):
            if i >= halfway:
                mid_canvas.itemconfig(r, fill=RED)
                mid_canvas.create_text(cx + PKT_W//2 + 6, cy, text=f"Frame {seq_num} lost",
                                       fill=RED, font=("Segoe UI", 9, "bold"), anchor="w",
                                       tags=tag + "_lost_label")
                def _vanish():
                    mid_canvas.delete(tag)
                    mid_canvas.delete(tag + "_lost_label")
                    # Frame is truly lost — receiver never sees it, no ACK sent, sender will timeout
                mid_canvas.after(800, _vanish)
                return
            mid_canvas.coords(r, cx - PKT_W//2, cy - PKT_H//2, cx + PKT_W//2, cy + PKT_H//2)
            mid_canvas.coords(t, cx, cy)
            mid_canvas.after(delay, lambda: _step(i + 1, cx + dx, cy + dy))

        _step(0, x1, y1)

    def _launch_ack_lost(tag, ack_num, x1, y1, x2, y2, steps=48, delay=22):
        mid_canvas.delete(tag)
        mid_canvas.delete(tag + "_lost_label")
        r = mid_canvas.create_rectangle(x1 - PKT_W//2, y1 - PKT_H//2, x1 + PKT_W//2, y1 + PKT_H//2,
                                        fill=YELLOW_PKT, outline="white", width=2, tags=tag)
        t = mid_canvas.create_text(x1, y1, text=f"ACK{ack_num}", fill="white",
                                   font=("Consolas", 11, "bold"), tags=tag)
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        halfway = steps // 2

        def _step(i, cx, cy):
            if i >= halfway:
                mid_canvas.itemconfig(r, fill=RED)
                mid_canvas.create_text(cx + PKT_W//2 + 6, cy, text=f"ACK {ack_num} lost",
                                       fill=RED, font=("Segoe UI", 9, "bold"), anchor="w",
                                       tags=tag + "_lost_label")
                def _vanish():
                    mid_canvas.delete(tag)
                    mid_canvas.delete(tag + "_lost_label")
                mid_canvas.after(800, _vanish)
                return
            mid_canvas.coords(r, cx - PKT_W//2, cy - PKT_H//2, cx + PKT_W//2, cy + PKT_H//2)
            mid_canvas.coords(t, cx, cy)
            mid_canvas.after(delay, lambda: _step(i + 1, cx + dx, cy + dy))

        _step(0, x1, y1)

    def _launch_pkt(tag, color, label, x1, y1, x2, y2, steps=48, delay=22, on_done=None, mark_x=False, seq_label=None):
        mid_canvas.delete(tag)
        mid_canvas.delete(tag + "_x")
        mid_canvas.delete(tag + "_seq")
        r = mid_canvas.create_rectangle(x1 - PKT_W//2, y1 - PKT_H//2, x1 + PKT_W//2, y1 + PKT_H//2, fill=color, outline="white", width=2, tags=tag)
        t = mid_canvas.create_text(x1, y1, text=label, fill="white", font=("Consolas", 11, "bold"), tags=tag)
        seq_t = None
        if seq_label is not None:
            seq_t = mid_canvas.create_text(x1 + PKT_W//2 - 6, y1 - PKT_H//2 + 8, text=seq_label, fill="white", font=("Consolas", 7, "bold"), anchor="ne", tags=tag + "_seq")
        xmark = None
        if mark_x:
            xmark = mid_canvas.create_text(x1, y1, text="✗", fill="white", font=("Segoe UI", 11, "bold"), tags=tag + "_x")
        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps
        def _step(i, cx, cy):
            if i >= steps:
                mid_canvas.delete(tag)
                mid_canvas.delete(tag + "_x")
                mid_canvas.delete(tag + "_seq")
                if on_done: on_done()
                return
            mid_canvas.coords(r, cx-PKT_W//2, cy-PKT_H//2, cx+PKT_W//2, cy+PKT_H//2)
            mid_canvas.coords(t, cx, cy)
            if seq_t is not None:
                mid_canvas.coords(seq_t, cx + PKT_W//2 - 6, cy - PKT_H//2 + 8)
            if xmark is not None:
                mid_canvas.coords(xmark, cx, cy)
            mid_canvas.after(delay, lambda: _step(i+1, cx+dx, cy+dy))
        _step(0, x1, y1)

    def set_status(state, message):
        colors = {"ready": GREEN, "sending": BLUE_SEND, "error": RED, "timeout": RED, "complete": GREEN, "ack_loss": RED}
        indicator_canvas.itemconfig(indicator_light, fill=colors.get(state, GREEN))
        status_text.config(text=f"Status: {message}")

    def log(msg):
        log_text.insert('end', msg + '\n')
        log_text.see('end')
        root.update_idletasks()

    # ==================== SIMULATION ENGINE ====================

    def send_next_frame():
        nonlocal next_to_send, total_sent, timer_start_time, current_window_errors
        if not animating or paused_by_error:
            return

        message = config['message']
        total_frames = len(message)
        window_size = config['window_size']
        error_rate = config.get('error_rate', 0.0)

        if base_val >= total_frames:
            end_simulation()
            return

        if next_to_send >= base_val + window_size or next_to_send >= total_frames:
            return

        # --- DETERMINISTIC ERROR MAPPING PER WINDOW ---
        if next_to_send == base_val:
            current_window_errors.clear()
            error_pct = int(error_rate * 100)
            win_size = min(window_size, total_frames - base_val)

            # ── Safety rule ───────────────────────────────────────────────
            # The last 4 frames of the entire message are NEVER targeted by
            # any error (except 71-100% window-collapse).  This guarantees
            # every simulation can finish regardless of window size.
            #
            # Key insight that fixes the infinite-loop bug:
            #   After a timeout, next_to_send is reset to base_val.
            #   resume_animation clears current_window_errors.
            #   send_next_frame sees next_to_send == base_val → regenerates
            #   errors.  If the only safe slot is index 0 and we assign an
            #   error there, that error fires AGAIN on every retransmit →
            #   infinite loop.  Fix: for scenarios that need index >= 1,
            #   NEVER fall back to index 0.  If no index >= 1 is available
            #   (small window at end of message), assign NO error so the
            #   window transmits cleanly and the simulation finishes.
            # ──────────────────────────────────────────────────────────────
            last4_start = max(0, total_frames - 4)

            # Indices safe from last-4 protection (absolute seq < last4_start)
            all_safe = [i for i in range(win_size) if (base_val + i) < last4_start]
            # Subset that excludes index 0 — safe to use for corruption/multi-error
            non_zero_safe = [i for i in all_safe if i >= 1]

            if 71 <= error_pct <= 100:
                # WINDOW COLLAPSE: first frame always lost, no protection.
                current_window_errors[0] = "frame_loss"

            elif not all_safe:
                # Entire window is inside the last-4 zone → clean transmission.
                pass

            elif 1 <= error_pct <= 15:
                # LOW severity — lost frame, ~15% of windows only.
                # Frame loss is expensive (full window retransmit + timeout),
                # so I  keep the probability very low so total retransmissions
                # stay clearly BELOW the 16-30% ACK-loss range (65% frequency
                # but cheap per event).  15% here vs 65% there ensures the
                # retransmission count trend always increases with error rate.
                if non_zero_safe and random.random() < 0.08:  # LOW: fires only 8% of windows — far less than 16-30% (65%)
                    t = random.choice(non_zero_safe)
                    current_window_errors[t] = "frame_loss"

            elif 16 <= error_pct <= 30:
                # MEDIUM-LOW — lost ACK, ~65% of windows.
                # ACK loss: data arrives fine, only the ACK disappears.
                # Receiver re-ACKs on duplicate → cheap retransmit.
                if non_zero_safe and random.random() < 0.65:
                    t = random.choice(non_zero_safe)
                    current_window_errors[t] = "ack_loss"

            elif 31 <= error_pct <= 50:
                # MEDIUM — corrupted frame, every window (100%).
                # Targets index >= 1 ONLY.  If no such slot exists → clean.
                if non_zero_safe:
                    t = random.choice(non_zero_safe)
                    current_window_errors[t] = "frame_corruption"
                # else: window too small for a safe non-zero target → clean

            elif 51 <= error_pct <= 70:
                # HIGH — two distinct errors, every window.
                # Both must target index >= 1 ONLY.
                if len(non_zero_safe) >= 2:
                    t1, t2 = random.sample(non_zero_safe, 2)
                    e1, e2 = random.sample(["frame_loss", "frame_corruption", "ack_loss"], 2)
                    current_window_errors[t1] = e1
                    current_window_errors[t2] = e2
                elif len(non_zero_safe) == 1:
                    # Only one non-zero slot — single error
                    current_window_errors[non_zero_safe[0]] = "frame_corruption"
                # else: no safe non-zero slot → clean window

        curr_seq = next_to_send
        next_to_send += 1

        frame_states[curr_seq] = "sending"
        draw_top_row()

        cs = calculate_checksum(message[curr_seq])
        action = "Retransmitting" if frame_states.get(curr_seq) in ["timeout", "lost", "error"] else "Sending"
        log(f"[SENDER]   {action} Frame {curr_seq} -> Packet(seq={curr_seq}, data='{message[curr_seq]}', checksum={cs})")

        total_sent += 1
        frames_sent_label.config(text=f"Sent: {total_sent}")

        if timer_start_time is None:
            timer_start_time = time.time()

        is_lost = False
        is_corrupted = False
        err_type = None

        frame_idx = curr_seq - base_val
        if frame_idx in current_window_errors:
            assigned_err = current_window_errors[frame_idx]
            if assigned_err == "frame_loss":
                is_lost = True
                err_type = "frame_loss"
                frame_states[curr_seq] = "lost"
                log(f"[CHANNEL]  ! Frame {curr_seq} disappears mid-channel -> Lost in transit!")
                log(f"           Receiver never sees Frame {curr_seq}.")
                log(f"           Subsequent frames in window discarded (seq mismatch).")
                log(f"           No ACK will be sent. Sender will timeout.")
            elif assigned_err == "frame_corruption":
                is_corrupted = True
                err_type = "frame_corruption"
                log(f"[CHANNEL]  ! Frame {curr_seq} reaches receiver but checksum will FAIL (corrupted in transit).")
            elif assigned_err == "ack_loss":
                err_type = "ack_loss"
                log(f"[CHANNEL]  Frame {curr_seq} travels normally -> will reach receiver OK.")

        H = mid_canvas.winfo_height() or 220
        cx_s = _canvas_x(curr_seq)

        if is_lost:
            _launch_pkt_lost(f"pkt_{curr_seq}", curr_seq, cx_s, 8, cx_s, H - 8, steps=48, delay=22)
            last_progress_time = time.time()  # reset so timeout fires after timeout_dur
        else:
            if is_corrupted:
                last_progress_time = time.time()  # corrupted frame will get no ACK, need timeout
            _launch_pkt(
                f"pkt_{curr_seq}", ORANGE if is_corrupted else PINK,
                message[curr_seq], cx_s, 8, cx_s, H - 8, steps=48, delay=22,
                on_done=lambda s=curr_seq, ic=is_corrupted, et=err_type: process_receiver_arrival(s, ic, et),
                mark_x=False, seq_label=f"#{curr_seq + 1}"
            )

        if next_to_send < base_val + window_size and next_to_send < total_frames:
            root.after(300, send_next_frame)

    def timeout_check():
        nonlocal timer_start_time, next_to_send, total_retrans, total_timeouts, waiting_logged, paused_by_error, last_progress_time, timeout_pending
        if not animating or paused_by_error:
            root.after(200, timeout_check)
            return

        timeout_dur = config.get('timeout', 1.0)

        if last_progress_time is not None:
            elapsed_since_progress = time.time() - last_progress_time
            if elapsed_since_progress >= timeout_dur:
                if not timeout_pending:
                    timeout_pending = True
                    root.after(600, trigger_timeout)
                return

            if not waiting_logged and elapsed_since_progress > 0:
                waiting_logged = True
                log(f"  [SENDER] Waiting for ACK... (timeout in {timeout_dur}s)")

        root.after(200, timeout_check)

    def trigger_timeout():
        nonlocal timer_start_time, next_to_send, total_retrans, total_timeouts, waiting_logged, paused_by_error, last_progress_time, timeout_pending
        if not animating or paused_by_error:
            timeout_pending = False
            return
        
        elapsed_since_progress = time.time() - last_progress_time
        timeout_dur = config.get('timeout', 1.0)
        
        if elapsed_since_progress < timeout_dur:
            timeout_pending = False
            root.after(200, timeout_check)
            return

        timeout_pending = False
        waiting_logged = False
        total_timeouts += 1  
        timeout_count_label.config(text=f"Timeouts: {total_timeouts}")

        rolled_back_count = next_to_send - base_val
        total_retrans += rolled_back_count
        retrans_label.config(text=f"Retransmitted: {total_retrans}")

        for i in range(base_val, next_to_send):
            frame_states[i] = "timeout"
        draw_top_row()

        next_to_send = base_val
        timer_start_time = None
        last_progress_time = None
        mid_canvas.delete("all")
        draw_top_row()

        log(f"[SENDER]   TIMEOUT! No ACK received for Frame {base_val} within {timeout_dur}s.")
        log(f"           Go-Back-N: Entire window from Frame {base_val} must be retransmitted.")
        log(f"Timeout occurs for Frame {base_val}. RED INDICATOR LIGHT ON.")
        log("           Transmission PAUSED.")
        log("Please click the Resume button to continue.")
        set_status("timeout", "⏸ Timeout — Click Resume")
        indicator_canvas.itemconfig(indicator_light, fill=RED)
        paused_by_error = True
        resume_btn.config(state=tk.NORMAL)
        root.after(200, timeout_check)

    def process_receiver_arrival(seq, is_corrupted, error_type):
        if not animating: return
        H = mid_canvas.winfo_height() or 220
        cx = _canvas_x(seq)

        if is_corrupted:
            expected_cs = calculate_checksum(config['message'][seq])
            got_cs = (expected_cs + 1) % 256
            log(f"[RECEIVER] Frame {seq} arrived but Checksum FAILED (expected={expected_cs}, got={got_cs})")
            log(f"[RECEIVER] Frame {seq} CORRUPTED -> DISCARD. No ACK sent.")
            log(f"           All subsequent frames in this window also discarded (seq mismatch).")
            frame_states[seq] = "error"
            discarded_frames.add(seq)
            draw_bottom_row()
            return

        expected_seq = len(received_frames)
        if seq == expected_seq:
            log(f"[RECEIVER] Frame {seq} received OK. Checksum PASSED. Seq matches expected ({seq}).")
            received_frames[seq] = config['message'][seq]
            draw_bottom_row()
            recv_count_label.config(text=f"Recv: {len(received_frames)}/{len(config['message'])}")

            ack_seq = seq + 1
            if error_type == "ack_loss":
                log(f"[RECEIVER] Sending cumulative ACK {ack_seq}...")
                log(f"[CHANNEL]  ! ACK {ack_seq} lost mid-channel -> Sender never receives it.")
                log(f"           Sender will timeout and retransmit entire window.")
                log(f"           Receiver will discard duplicates (already received), then re-ACK.")
                _launch_ack_lost(f"ack_lost_{seq}", ack_seq, cx, H - 8, cx, H // 2, steps=48, delay=22)
            else:
                log(f"[RECEIVER] Sending cumulative ACK {ack_seq}...")
                log(f"[CHANNEL]  ACK {ack_seq} delivered to Sender successfully.")
                _launch_pkt(f"ack_{seq}", YELLOW_PKT, f"ACK{ack_seq}", cx, H - 8, cx, 8, steps=48, delay=22,
                            on_done=lambda a=ack_seq: process_sender_ack(a))
        elif seq in received_frames:
            # Duplicate frame (already received — e.g. after ACK was lost and sender retransmitted).
            # Receiver discards the data but re-sends a cumulative ACK so sender can advance.
            ack_seq = seq + 1
            log(f"[RECEIVER] Frame {seq} is a DUPLICATE (already received). Discarding data.")
            log(f"[RECEIVER] Re-sending cumulative ACK {ack_seq} to unblock sender.")
            _launch_pkt(f"ack_dup_{seq}", YELLOW_PKT, f"ACK{ack_seq}", cx, H - 8, cx, 8, steps=48, delay=22,
                        on_done=lambda a=ack_seq: process_sender_ack(a))
        else:
            log(f"[RECEIVER] Frame {seq} arrived but seq={seq} != expected={expected_seq} -> DISCARD (out of order).")
            log(f"           No ACK sent for this frame.")
            discarded_frames.add(seq)
            draw_bottom_row()

    def process_sender_ack(ack_num):
        nonlocal timer_start_time, base_val, waiting_logged, last_progress_time
        if not animating: return
        
        if paused_by_error:
            return

        if ack_num == base_val + 1:
            frame_states[base_val] = "acked"
            base_val += 1
            
            window_size = config['window_size']
            new_win_end = min(base_val + window_size, len(config['message'])) - 1
            new_window_str = f"{base_val} to {new_win_end}" if base_val <= new_win_end else "none (all done)"
            log(f"[SENDER]   ACK {ack_num} received. Frame {base_val-1} confirmed. Sliding window -> [{new_window_str}]")
            
            draw_top_row()
            frames_acked_label.config(text=f"ACKed: {base_val}")
            update_progress_bar((base_val / len(config['message'])) * 100)
            efficiency_label.config(text=f"Efficiency: {((total_sent - total_retrans) / total_sent * 100):.1f}%" if total_sent > 0 else "0%")

            if base_val >= len(config['message']):
                end_simulation()
                return

            waiting_logged = False
            timer_start_time = time.time()
            last_progress_time = time.time()
            send_next_frame()
        else:
            log(f"[SENDER]   ACK {ack_num} received but out of order. Expecting ACK {base_val + 1}. Discarding.")

    def end_simulation():
        nonlocal animating
        animating = False
        efficiency = 100.0 if total_sent == 0 else ((total_sent - total_retrans) / total_sent) * 100
        received_msg = ''.join(received_frames.get(i, '') for i in range(len(config['message'])))
        log("=" * 55)
        log("  TRANSMISSION COMPLETE")
        log("=" * 55)
        log(f"  Total Frames Sent     : {total_sent}")
        log(f"  Total Retransmissions : {total_retrans}")
        log(f"  Timeouts Encountered  : {total_timeouts}")
        if config.get('input_mode') == 'packets':
            log(f"  Packets Received      : {len(received_frames)} / {config['packet_count']} packets successfully received")
        else:
            log(f"  Received Message       : {received_msg}")
        log(f"  Channel Efficiency    : {efficiency:.1f}%")
        log("=" * 55)

        simulation_history.append({"error_rate": config.get('error_rate', 0), "window_size": config['window_size'], "sent": total_sent, "acked": base_val, "retransmitted": total_retrans, "timeouts": total_timeouts, "efficiency": efficiency, "received_msg": received_msg})
        set_status("complete", "✓ Complete")
        update_progress_bar(100)
        root.after(500, lambda: show_channel_complete(received_msg))

    def start_animation():
        nonlocal animating, base_val, next_to_send, total_sent, total_retrans, total_timeouts, timer_start_time, waiting_logged, paused_by_error, last_progress_time, discarded_frames, timeout_pending, current_window_errors
        if not config.get('message'):
            messagebox.showwarning("No Data", "Enter a message first!"); return
        if config.get('window_size') is None:
            messagebox.showwarning("Missing", "Set Window Size first!"); return
        if config.get('timeout') is None:
            messagebox.showwarning("Missing", "Set Timeout first!"); return
        if config.get('error_rate') is None:
            messagebox.showwarning("Missing", "Set Error Rate first!"); return

        animating = True
        paused_by_error = False
        base_val = 0
        waiting_logged = False
        timeout_pending = False
        current_window_errors.clear()
        next_to_send = 0
        total_sent = 0
        total_retrans = 0
        total_timeouts = 0
        timer_start_time = None
        last_progress_time = time.time()

        log_text.delete('1.0', 'end')
        frame_states.clear()
        received_frames.clear()
        discarded_frames.clear()
        frames_sent_label.config(text="Sent: 0")
        frames_acked_label.config(text="ACKed: 0")
        retrans_label.config(text="Retransmitted: 0")
        timeout_count_label.config(text="Timeouts: 0")
        efficiency_label.config(text="Efficiency: 0%")
        recv_count_label.config(text=f"Recv: 0/{len(config['message'])}")
        resume_btn.config(state=tk.DISABLED)
        update_progress_bar(0)
        set_status("sending", "Transmitting window block...")
        mid_canvas.delete("all")
        draw_top_row()
        draw_bottom_row()

        ws = config['window_size']
        er = config.get('error_rate', 0.0)
        msg = config['message']
        er_pct = int(er * 100)

        log("=" * 55)
        log("  Go-Back-N ARQ Simulation Started")
        log("=" * 55)
        log(f"  Sender connected to Receiver successfully.")
        log(f"  Message Length : {len(msg)} frames")
        log(f"  Window Size    : {ws}")
        log(f"  Timeout        : {config.get('timeout', 1.0)}s")
        log(f"  Error Rate     : {er_pct}%")
        log("=" * 55)
        first_window_end = min(ws, len(msg)) - 1
        log(f"  Sending window: Frame 0 to Frame {first_window_end}")
        log(f"[SENDER] Transmitting Frame 0 to Frame {first_window_end}...")

        send_next_frame()
        root.after(200, timeout_check)

    def resume_animation():
        nonlocal paused_by_error, timer_start_time, waiting_logged, last_progress_time, timeout_pending, current_window_errors
        if paused_by_error:
            paused_by_error = False
            timer_start_time = time.time()
            last_progress_time = time.time()
            waiting_logged = False
            timeout_pending = False
            current_window_errors.clear()
            resume_btn.config(state=tk.DISABLED)
            indicator_canvas.itemconfig(indicator_light, fill=GREEN)
            log(f"[SENDER]   Resuming transmission. Retransmitting window from Frame {base_val}.")
            set_status("sending", "Retransmitting...")
            send_next_frame()

    def stop_animation():
        nonlocal animating, paused_by_error
        # For 71-100% window-collapse, stopping is the expected end condition.
        # Record an "infinity" entry so the table and graphs show the breakdown.
        er = config.get('error_rate') or 0
        er_pct = int(er * 100)
        if animating and 71 <= er_pct <= 100 and config.get('window_size') and config.get('message'):
            log("=" * 55)
            log("  TRANSMISSION STOPPED — Window Collapse (71-100%)")
            log("=" * 55)
            log(f"  Frames Sent           : \u221e")
            log(f"  Retransmissions       : \u221e")
            log(f"  Timeouts              : \u221e")
            log(f"  Useful Frames ACKed   : {base_val} / {len(config['message'])}")
            log(f"  Channel Efficiency    : 0%  (protocol breakdown)")
            log("=" * 55)
            log("")
            log("  \U0001f4a1 Click '\U0001f4ca Run Tests' above to view all")
            log("     simulation results and graphs.")
            simulation_history.append({
                "error_rate": er,
                "window_size": config['window_size'],
                "sent": float('inf'),
                "acked": base_val,
                "retransmitted": float('inf'),
                "timeouts": float('inf'),
                "efficiency": 0.0,
                "received_msg": ""
            })
            set_status("complete", "✗ Stopped — Window Collapse")
        animating = False
        paused_by_error = False
        resume_btn.config(state=tk.DISABLED)

    def update_progress_bar(pct):
        pct = max(0.0, min(100.0, pct))
        progress_label.config(text=f"Progress: {int(pct)}%")
        progress_canvas.update_idletasks()
        W = progress_canvas.winfo_width()
        if W <= 1: W = 290
        progress_canvas.coords(progress_bar_fill, 0, 0, int((pct/100.0)*W), 20)

    # ==================== MAIN PAGE LAYOUT ====================
    main_frame = tk.Frame(root, bg=DARK_BG)
    main_frame.pack(fill="both", expand=True)

    top_bar = tk.Frame(main_frame, bg=BG_BLUE, height=50)
    top_bar.pack(side="top", fill="x")
    top_bar.pack_propagate(False)

    back_btn = tk.Button(top_bar, text="⬅  Back", font=("Segoe UI", 10, "bold"), bg=RED, fg=WHITE, relief="flat", padx=10, command=lambda: [stop_animation(), go_back_callback()])
    back_btn.pack(side="left", padx=15, pady=10)

    indicator_canvas = tk.Canvas(top_bar, width=20, height=20, bg=BG_BLUE, highlightthickness=0)
    indicator_canvas.pack(side="left", padx=(10, 5), pady=15)
    indicator_light = indicator_canvas.create_oval(2, 2, 18, 18, fill=GREEN, outline=WHITE)

    status_text = tk.Label(top_bar, text="Status: Ready", font=("Segoe UI", 11, "bold"), bg=BG_BLUE, fg=WHITE)
    status_text.pack(side="left", padx=5, pady=12)

    counters_frame = tk.Frame(top_bar, bg=BG_BLUE)
    counters_frame.pack(side="right", padx=15)

    run_tests_btn = tk.Button(counters_frame, text="📊 Run Tests", font=("Segoe UI", 10, "bold"), bg="#2980b9", fg=WHITE, relief="flat", padx=12, command=show_graphs_window)
    run_tests_btn.pack(side="left", padx=4, pady=12)

    frames_sent_label = tk.Label(counters_frame, text="Sent: 0", font=("Segoe UI", 10, "bold"), bg=DARK_BG, fg="#5dade2", width=10, bd=1, relief="groove")
    frames_sent_label.pack(side="left", padx=4, pady=12)
    frames_acked_label = tk.Label(counters_frame, text="ACKed: 0", font=("Segoe UI", 10, "bold"), bg=DARK_BG, fg=GREEN, width=11, bd=1, relief="groove")
    frames_acked_label.pack(side="left", padx=4, pady=12)
    retrans_label = tk.Label(counters_frame, text="Retransmitted: 0", font=("Segoe UI", 10, "bold"), bg=DARK_BG, fg=ORANGE, width=17, bd=1, relief="groove")
    retrans_label.pack(side="left", padx=4, pady=12)
    timeout_count_label = tk.Label(counters_frame, text="Timeouts: 0", font=("Segoe UI", 10, "bold"), bg=DARK_BG, fg=RED, width=13, bd=1, relief="groove")
    timeout_count_label.pack(side="left", padx=4, pady=12)
    efficiency_label = tk.Label(counters_frame, text="Efficiency: 0%", font=("Segoe UI", 10, "bold"), bg=DARK_BG, fg=YELLOW, width=15, bd=1, relief="groove")
    efficiency_label.pack(side="left", padx=4, pady=12)

    left_panel = tk.Frame(main_frame, bg=DARK_BG, width=240)
    left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)
    left_panel.pack_propagate(False)

    tk.Label(left_panel, text="INPUT CONFIGURATION", font=("Segoe UI", 11, "bold"), bg=DARK_BG, fg="#aabbcc").pack(pady=(5, 12))

    btn_opts = {"font": ("Segoe UI", 10, "bold"), "bg": "#2980b9", "fg": WHITE, "activebackground": "#3498db", "activeforeground": WHITE, "relief": "raised", "bd": 2, "height": 1}
    tk.Button(left_panel, text="✍  Enter Data",         **btn_opts, command=enter_data).pack(fill="x", pady=4)
    tk.Button(left_panel, text="🪟  Set Window Size (N)", **btn_opts, command=set_window_size).pack(fill="x", pady=4)
    tk.Button(left_panel, text="⏱  Set Timeout (S)", **btn_opts, command=set_timeout).pack(fill="x", pady=4)
    tk.Button(left_panel, text="💥  Set Channel Error Rate", **btn_opts, command=set_error_rate).pack(fill="x", pady=4)

    settings_frame = tk.Frame(left_panel, bg="#1a3a5c", bd=1, relief="groove")
    settings_frame.pack(fill="x", pady=10, padx=5)

    tk.Label(settings_frame, text="CURRENT SETTINGS", font=("Segoe UI", 9, "bold"), bg="#1a3a5c", fg=WHITE).pack(pady=5)

    def get_msg_display():
        if config.get('input_mode') == 'packets':
            n = config.get('packet_count', 0)
            return f"{n} packet(s)" if n else '-'
        msg = config.get('message', '')
        if len(msg) > 15:
            return msg[:12] + "..."
        return msg if msg else '-'

    msg_lbl = tk.Label(settings_frame, text=f"Message: {get_msg_display()}", font=("Segoe UI", 9), bg="#1a3a5c", fg="#aabbcc", anchor="w", cursor="hand2")
    msg_lbl.pack(fill="x", padx=10)
    msg_lbl.bind("<Button-1>", lambda e: view_full_message())

    ws_lbl = tk.Label(settings_frame, text=f"Window Size: {config.get('window_size', '-')}", font=("Segoe UI", 9), bg="#1a3a5c", fg="#aabbcc", anchor="w")
    ws_lbl.pack(fill="x", padx=10)

    to_lbl = tk.Label(settings_frame, text=f"Timeout: {config.get('timeout', '-')}s", font=("Segoe UI", 9), bg="#1a3a5c", fg="#aabbcc", anchor="w")
    to_lbl.pack(fill="x", padx=10)

    er = config.get('error_rate')
    er_lbl = tk.Label(settings_frame, text=f"Error Rate: {int(er * 100) if er is not None else 0}%", font=("Segoe UI", 9), bg="#1a3a5c", fg="#aabbcc", anchor="w")
    er_lbl.pack(fill="x", padx=10, pady=(0, 10))

    def update_settings_display():
        msg_lbl.config(text=f"Message: {get_msg_display()}")
        ws_lbl.config(text=f"Window Size: {config.get('window_size', '-')}")
        to_lbl.config(text=f"Timeout: {config.get('timeout', '-')}s")
        er = config.get('error_rate')
        er_lbl.config(text=f"Error Rate: {int(er * 100) if er is not None else 0}%")

    tk.Frame(left_panel, height=2, bg=BG_BLUE).pack(fill="x", pady=15)

    tk.Label(left_panel, text="EXECUTION CONTROLS", font=("Segoe UI", 11, "bold"), bg=DARK_BG, fg="#aabbcc").pack(pady=(0, 10))

    start_btn = tk.Button(left_panel, text="▶  START SIMULATION", font=("Segoe UI", 11, "bold"), bg=GREEN, fg=WHITE, relief="raised", bd=3, command=start_animation)
    start_btn.pack(fill="x", pady=4)
    resume_btn = tk.Button(left_panel, text="⏯  RESUME", font=("Segoe UI", 11, "bold"), bg=YELLOW, fg=WHITE, relief="raised", bd=3, state=tk.DISABLED, command=resume_animation)
    resume_btn.pack(fill="x", pady=4)
    stop_btn = tk.Button(left_panel, text="🛑  STOP", font=("Segoe UI", 10, "bold"), bg="#c0392b", fg=WHITE, relief="flat", command=stop_animation)
    stop_btn.pack(fill="x", pady=4)
    clear_btn = tk.Button(left_panel, text="🗑  CLEAR ALL RESET", font=("Segoe UI", 10, "bold"), bg="#7f8c8d", fg=WHITE, relief="flat", command=clear_all)
    clear_btn.pack(fill="x", pady=(4, 15))

    mid_panel = tk.Frame(main_frame, bg=DARK_BG)
    mid_panel.pack(side="left", fill="both", expand=True, padx=5, pady=10)

    sender_hdr = tk.Frame(mid_panel, bg="#1a3a5c", height=26)
    sender_hdr.pack(fill="x")
    sender_hdr.pack_propagate(False)
    tk.Label(sender_hdr, text="SENDER WINDOW", font=("Segoe UI", 9, "bold"), bg="#1a3a5c", fg=WHITE).pack(side="left", padx=8, pady=3)

    top_canvas = tk.Canvas(mid_panel, bg=DARK_CANVAS, height=FRAME_H + 16, highlightthickness=1, highlightbackground=BG_BLUE)
    top_canvas.pack(fill="x", pady=(0, 10))
    top_canvas.bind("<Configure>", draw_top_row)

    trans_hdr = tk.Frame(mid_panel, bg="#1a3a5c", height=26)
    trans_hdr.pack(fill="x")
    trans_hdr.pack_propagate(False)
    tk.Label(trans_hdr, text="LIVE TRANSIT COMMUNICATION CHANNEL (Go-Back-N ARQ Protocol)", font=("Segoe UI", 9, "bold"), bg="#1a3a5c", fg=WHITE).pack(side="left", padx=8, pady=3)

    mid_canvas = tk.Canvas(mid_panel, bg=DARK_CANVAS, highlightthickness=1, highlightbackground=BG_BLUE)
    mid_canvas.pack(fill="both", expand=True, pady=(0, 10))
    root.after(100, show_channel_idle)

    recv_hdr = tk.Frame(mid_panel, bg="#1a3a5c", height=26)
    recv_hdr.pack(fill="x")
    recv_hdr.pack_propagate(False)
    tk.Label(recv_hdr, text="RECEIVER WINDOW", font=("Segoe UI", 9, "bold"), bg="#1a3a5c", fg=WHITE).pack(side="left", padx=8, pady=3)
    recv_count_label = tk.Label(recv_hdr, text="Recv: 0/0", font=("Segoe UI", 9, "bold"), bg="#1a3a5c", fg=GREEN)
    recv_count_label.pack(side="left", padx=8)

    bot_canvas = tk.Canvas(mid_panel, bg=DARK_CANVAS, height=FRAME_H + 16, highlightthickness=1, highlightbackground=BG_BLUE)
    bot_canvas.pack(fill="x")
    bot_canvas.bind("<Configure>", draw_bottom_row)

    right_panel = tk.Frame(main_frame, bg=DARK_BG, width=330)
    right_panel.pack(side="right", fill="y")
    right_panel.pack_propagate(False)

    progress_label = tk.Label(right_panel, text="Progress: 0%", font=("Segoe UI", 15, "bold"), bg=DARK_BG, fg=WHITE)
    progress_label.pack(pady=(8,2))
    progress_canvas = tk.Canvas(right_panel, bg="#333333", height=20, highlightthickness=0)
    progress_canvas.pack(padx=20, fill="x")
    progress_bar_fill = progress_canvas.create_rectangle(0, 0, 0, 20, fill=BLUE_SEND)

    tk.Label(right_panel, text="TRANSMISSION LOG", font=("Segoe UI", 13, "bold"), bg=DARK_BG, fg="#aabbcc").pack(pady=(10,2))
    log_frame = tk.Frame(right_panel, bg="#2980b9", bd=1)
    log_frame.pack(fill="both", expand=True, padx=10, pady=10)

    log_text = tk.Text(log_frame, bg="#112233", fg=WHITE, font=("Consolas", 9), wrap="word", relief="flat")
    log_text.pack(fill="both", expand=True)

    bottom_bar = tk.Frame(main_frame, bg=BG_BLUE, height=24)
    bottom_bar.pack(side="bottom", fill="x")
    bottom_bar.pack_propagate(False)

    tk.Label(bottom_bar, text="Current Config -> Message:", font=("Segoe UI", 9, "bold"), bg=BG_BLUE, fg="#aabbcc").pack(side="left", padx=(10,2))
    bottom_msg_val = tk.Label(bottom_bar, text="-", font=("Segoe UI", 9), bg=BG_BLUE, fg=WHITE)
    bottom_msg_val.pack(side="left")

    tk.Label(bottom_bar, text=" | Window Size:", font=("Segoe UI", 9, "bold"), bg=BG_BLUE, fg="#aabbcc").pack(side="left", padx=2)
    bottom_ws_val = tk.Label(bottom_bar, text="-", font=("Segoe UI", 9), bg=BG_BLUE, fg=WHITE)
    bottom_ws_val.pack(side="left")

    tk.Label(bottom_bar, text=" | Timeout:", font=("Segoe UI", 9, "bold"), bg=BG_BLUE, fg="#aabbcc").pack(side="left", padx=2)
    bottom_to_val = tk.Label(bottom_bar, text="-", font=("Segoe UI", 9), bg=BG_BLUE, fg=WHITE)
    bottom_to_val.pack(side="left")

    update_bottom_info_bar()
    update_settings_display()
    root.update_idletasks()
import tkinter as tk
from tkinter import messagebox
import json
import os

# ==================== MODERN COLOR PALETTE ====================
BG_DARK = "#0f172a"
ACCENT = "#22d3ee"
GREEN = "#10b981"
WHITE = "#f8fafc"
GRAY = "#94a3b8"

# ==================== CONFIG ====================

def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except:
            cfg = {}
    else:
        cfg = {}

    cfg.setdefault("window_size", 4)
    cfg.setdefault("timeout", 3.0)
    cfg.setdefault("host", "127.0.0.1")
    cfg.setdefault("port", 5000)
    cfg.setdefault("message", "")
    cfg.setdefault("error_rate", 0.0)

    return cfg


def save_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


# ==================== BUTTON HOVER ====================

def add_hover_effect(button, color, hover_color):
    def on_enter(e):
        button["background"] = hover_color
    def on_leave(e):
        button["background"] = color
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


# ==================== MAIN WINDOW ====================

root = tk.Tk()
root.title("Go-Back-N ARQ Software")
root.geometry("1400x800")
root.configure(bg=BG_DARK)

config = load_config()


# ==================== NAVIGATION ====================

def go_to_intro():
    welcome_page.pack_forget()
    build_intro_page()
    intro_page.pack(fill="both", expand=True)

def go_to_experiment():
    intro_page.pack_forget()
    import experiment
    experiment.show_experiment_page(root, config, go_back)

def go_back():
    for widget in root.winfo_children():
        widget.destroy()
    build_welcome_page()
    welcome_page.pack(fill="both", expand=True)

def go_back_to_welcome():
    intro_page.pack_forget()
    welcome_page.pack(fill="both", expand=True)


# ==================== WELCOME PAGE ====================

def build_welcome_page():
    global welcome_page
    welcome_page = tk.Frame(root, bg=BG_DARK)

    # TITLE
    tk.Label(
        welcome_page,
        text="📡 Welcome to the Go-Back-N ARQ Experiment Teaching Software",
        font=("Segoe UI", 24, "bold"),
        bg=BG_DARK,
        fg=ACCENT
    ).pack(pady=(20, 25))

    # ==================================================
    # VISUAL + TEXT SECTION (horizontal)
    # ==================================================
    visual_frame = tk.Frame(welcome_page, bg=BG_DARK)
    visual_frame.pack(fill="x", pady=20)

    visual_frame.columnconfigure(0, weight=1, minsize=250)
    visual_frame.columnconfigure(1, weight=3)
    visual_frame.columnconfigure(2, weight=1, minsize=250)

    # ------------------------------------------
    # LEFT: Sender
    # ------------------------------------------
    left_frame = tk.Frame(visual_frame, bg=BG_DARK)
    left_frame.grid(row=0, column=0, padx=10, pady=(60, 0), sticky="n")

    tk.Label(
        left_frame,
        text="MESSAGE SENDER",
        font=("Segoe UI", 12, "bold"),
        bg=ACCENT,
        fg=BG_DARK,
        padx=15,
        pady=5
    ).pack(pady=(0, 10))

    # ------------------------------------------
    # CENTER: Info text
    # ------------------------------------------
    center_frame = tk.Frame(visual_frame, bg=BG_DARK)
    center_frame.grid(row=0, column=1, padx=20, sticky="n")

    tk.Label(
        center_frame,
        text="Welcome !",
        font=("Segoe UI", 18, "bold"),
        bg=BG_DARK,
        fg=ACCENT
    ).pack(pady=(20, 5))

    tk.Label(
        center_frame,
        text="Glad you're here !",
        font=("Segoe UI", 14),
        bg=BG_DARK,
        fg=WHITE,
        justify="center"
    ).pack(pady=(0, 20))

    tk.Label(
        center_frame,
        text="",
        font=("Segoe UI", 18, "bold"),
        bg=BG_DARK,
        fg=ACCENT
    ).pack(pady=(0, 5))

    # Split into two separate labels so neither line wraps
    tk.Label(
        center_frame,
        text="",
        font=("Segoe UI", 13),
        bg=BG_DARK,
        fg=WHITE,
        justify="center"
    ).pack(pady=(0, 5))

    tk.Label(
        center_frame,
        text="",
        font=("Segoe UI", 13),
        bg=BG_DARK,
        fg=WHITE,
        justify="center"
    ).pack(pady=(0, 20))

    # ------------------------------------------
    # RIGHT: Receiver
    # ------------------------------------------
    right_frame = tk.Frame(visual_frame, bg=BG_DARK)
    right_frame.grid(row=0, column=2, padx=10, pady=(60, 0), sticky="n")

    tk.Label(
        right_frame,
        text="MESSAGE RECEIVER",
        font=("Segoe UI", 12, "bold"),
        bg=ACCENT,
        fg=BG_DARK,
        padx=15,
        pady=5
    ).pack(pady=(0, 10))

    # ==================================================
    # ENTER BUTTON
    # ==================================================
    enter_btn = tk.Button(
        welcome_page,
        text="CLICK HERE TO ENTER THE SOFTWARE",
        font=("Segoe UI", 14, "bold"),
        bg=GREEN,
        fg=WHITE,
        width=32,
        height=2,
        bd=0,
        cursor="hand2",
        activebackground="#34d399",
        command=go_to_intro
    )
    enter_btn.pack(pady=30)
    add_hover_effect(enter_btn, GREEN, "#34d399")

    return welcome_page


# ==================== INTRO PAGE ====================

def build_intro_page():
    global intro_page
    intro_page = tk.Frame(root, bg=BG_DARK)

    # ── Top accent bar ──────────────────────────────────────────
    top_bar = tk.Frame(intro_page, bg=ACCENT, height=4)
    top_bar.pack(fill="x")

    # ── Main content area ───────────────────────────────────────
    content = tk.Frame(intro_page, bg=BG_DARK)
    content.pack(fill="both", expand=True, padx=60, pady=30)

    # Platform title
    tk.Label(
        content,
        text="GO-BACK-N ARQ",
        font=("Segoe UI", 42, "bold"),
        bg=BG_DARK,
        fg=ACCENT
    ).pack(pady=(10, 0))

    tk.Label(
        content,
        text="EXPERIMENT TEACHING PLATFORM",
        font=("Segoe UI", 22, "bold"),
        bg=BG_DARK,
        fg=WHITE
    ).pack(pady=(0, 6))

    # Thin separator
    sep = tk.Frame(content, bg=ACCENT, height=2, width=500)
    sep.pack(pady=(4, 20))

    # Subtitle / tagline
    tk.Label(
        content,
        text="Visualization & Implementation of the Sliding Window Protocol",
        font=("Segoe UI", 14, "italic"),
        bg=BG_DARK,
        fg=GRAY
    ).pack(pady=(0, 30))

    # ── Info cards row ──────────────────────────────────────────
    cards_frame = tk.Frame(content, bg=BG_DARK)
    cards_frame.pack(fill="x", pady=(0, 30))
    cards_frame.columnconfigure(0, weight=1)
    cards_frame.columnconfigure(1, weight=1)
    cards_frame.columnconfigure(2, weight=1)

    card_data = [
        ("🔁", "Go-Back-N\\nError Control", "Simulate error free transmission or with errors such as frame loss, ACK Loss,\\ntimeout retransmissions and other transmission mechanisms\\nusing the GBN ARQ protocol."),
        ("🪟", "Sliding Window\\nProtocol", "Visualize how the sender window\\nadvances with ACKs and resets\\non timeout or REJ events."),
        ("📊", "Performance\\nAnalysis", "Run multi-scenario tests and\\nview efficiency, retransmission\\nand timeout graphs in real time."),
    ]

    CARD_BG = "#1e293b"
    for col, (icon, title, desc) in enumerate(card_data):
        card = tk.Frame(cards_frame, bg=CARD_BG, padx=20, pady=18,
                        highlightbackground=ACCENT, highlightthickness=1)
        card.grid(row=0, column=col, padx=14, sticky="nsew")

        tk.Label(card, text=icon, font=("Segoe UI", 28), bg=CARD_BG, fg=ACCENT).pack()
        tk.Label(card, text=title, font=("Segoe UI", 13, "bold"),
                 bg=CARD_BG, fg=WHITE, justify="center").pack(pady=(6, 4))
        tk.Label(card, text=desc, font=("Segoe UI", 10),
                 bg=CARD_BG, fg=GRAY, justify="center", wraplength=260).pack()

    # ── Buttons row ─────────────────────────────────────────────
    btn_frame = tk.Frame(content, bg=BG_DARK)
    btn_frame.pack(pady=(10, 0))

    back_btn = tk.Button(
        btn_frame,
        text="⬅  Back",
        font=("Segoe UI", 13, "bold"),
        bg="#334155",
        fg=WHITE,
        width=18,
        height=2,
        bd=0,
        cursor="hand2",
        activebackground="#475569",
        command=go_back_to_welcome
    )
    back_btn.pack(side="left", padx=16)
    add_hover_effect(back_btn, "#334155", "#475569")

    enter_btn = tk.Button(
        btn_frame,
        text="ENTER EXPERIMENT PLATFORM  ➤",
        font=("Segoe UI", 13, "bold"),
        bg=GREEN,
        fg=WHITE,
        width=28,
        height=2,
        bd=0,
        cursor="hand2",
        activebackground="#34d399",
        command=go_to_experiment
    )
    enter_btn.pack(side="left", padx=16)
    add_hover_effect(enter_btn, GREEN, "#34d399")

    # ── Bottom accent bar ───────────────────────────────────────
    bot_bar = tk.Frame(intro_page, bg=ACCENT, height=4)
    bot_bar.pack(fill="x", side="bottom")

    return intro_page


# ==================== START APP ====================
build_welcome_page()
welcome_page.pack(fill="both", expand=True)
root.mainloop()
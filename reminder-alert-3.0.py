import os
import sys
import subprocess
import venv

# ==========================================
# 1. VIRTUAL ENVIRONMENT BOOTSTRAPPER
# ==========================================
VENV_DIR = "alarm_env"

def get_venv_python():
    """Returns the path to the virtual environment's Python executable."""
    if os.name == 'nt': # Windows
        return os.path.abspath(os.path.join(VENV_DIR, "Scripts", "python.exe"))
    else: # macOS / Linux
        return os.path.abspath(os.path.join(VENV_DIR, "bin", "python"))

def setup_and_relaunch():
    """Creates venv if missing, and re-launches the script inside it."""
    venv_python = get_venv_python()
    
    # If the current Python interpreter is not the venv one, we need to switch
    if os.path.abspath(sys.executable) != venv_python:
        if not os.path.exists(VENV_DIR):
            print(f"[*] Creating virtual environment in '{VENV_DIR}'... (This takes a few seconds)")
            try:
                venv.create(VENV_DIR, with_pip=True)
            except Exception as e:
                print(f"[!] Failed to create venv: {e}")
                sys.exit(1)
        
        print("[*] Re-launching application inside the virtual environment...")
        subprocess.run([venv_python, os.path.abspath(__file__)])
        sys.exit(0)

setup_and_relaunch()

# ==========================================
# 2. AUTO-INSTALL DEPENDENCIES IN VENV
# ==========================================
try:
    import customtkinter as ctk
    import pygame
except ImportError:
    print("[*] First run detected: Installing required packages into the virtual environment...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "pygame"])
    import customtkinter as ctk
    import pygame

# ==========================================
# 3. MAIN APPLICATION UI & LOGIC
# ==========================================
import tkinter.messagebox as messagebox
from tkinter import filedialog
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Color Palette matching the image
BG_COLOR = "#0D1117"
CARD_COLOR = "#161B22"
ACCENT_PURPLE = "#5E5CE6"
ACCENT_GREEN = "#30D158"
TEXT_LIGHT = "#FFFFFF"
TEXT_MUTED = "#8B949E"
TIME_COLOR = "#82A0FA"

class AlarmApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Custom Interval Alarm")
        self.geometry("550x600")
        self.configure(fg_color=BG_COLOR)
        self.resizable(False, False)

        # Initialize Pygame Mixer
        pygame.mixer.init()

        # Variables
        self.is_running = False
        self.alarm_sound_path = None
        self.interval_minutes = 0
        self.time_left = 0
        
        # Threading event to pause timer while popup is open
        self.wait_for_user_event = threading.Event()

        self.create_widgets()

    def create_widgets(self):
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(25, 15))

        title_lbl = ctk.CTkLabel(header_frame, text="⏰ Recurring Alarm Clock", font=("Helvetica", 24, "bold"), text_color=TEXT_LIGHT)
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(header_frame, text="Stay on track. Stay focused.", font=("Helvetica", 14), text_color=TEXT_MUTED)
        sub_lbl.pack(anchor="w", padx=35)

        # --- INTERVAL SELECTION CARD ---
        interval_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12)
        interval_card.pack(fill="x", padx=30, pady=10)
        
        interval_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(interval_card, text="⏱️", font=("Helvetica", 20)).grid(row=0, column=0, padx=(15, 10), pady=15)
        ctk.CTkLabel(interval_card, text="Select Interval (mins)", font=("Helvetica", 14), text_color=TEXT_LIGHT).grid(row=0, column=1, sticky="w")
        
        self.interval_var = ctk.StringVar(value="15 minutes")
        intervals = ["5 minutes", "10 minutes", "15 minutes", "20 minutes", "25 minutes", "30 minutes", "60 minutes"]
        self.interval_dropdown = ctk.CTkOptionMenu(
            interval_card, variable=self.interval_var, values=intervals,
            fg_color="#21262D", button_color="#21262D", button_hover_color="#30363D", text_color=TEXT_LIGHT
        )
        self.interval_dropdown.grid(row=0, column=2, padx=15, pady=15)

        # --- SOUND SELECTION CARD ---
        sound_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12)
        sound_card.pack(fill="x", padx=30, pady=10)
        
        sound_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sound_card, text="🎵", font=("Helvetica", 20)).grid(row=0, column=0, padx=(15, 10), pady=15)
        
        sound_info_frame = ctk.CTkFrame(sound_card, fg_color="transparent")
        sound_info_frame.grid(row=0, column=1, sticky="w")
        
        ctk.CTkLabel(sound_info_frame, text="Alarm Sound", font=("Helvetica", 14), text_color=TEXT_LIGHT).pack(anchor="w")
        self.sound_label = ctk.CTkLabel(sound_info_frame, text="Selected: Default Beep", font=("Helvetica", 12), text_color=TEXT_MUTED)
        self.sound_label.pack(anchor="w")

        self.sound_btn = ctk.CTkButton(
            sound_card, text="📁 Choose Sound", command=self.choose_sound,
            fg_color=ACCENT_PURPLE, hover_color="#4B49B8", font=("Helvetica", 13, "bold")
        )
        self.sound_btn.grid(row=0, column=2, padx=15, pady=15)

        # --- COUNTDOWN CARD ---
        countdown_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12)
        countdown_card.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(countdown_card, text="⏳", font=("Helvetica", 24)).pack(pady=(20, 0))
        ctk.CTkLabel(countdown_card, text="Next alarm in", font=("Helvetica", 14), text_color=TEXT_MUTED).pack()
        
        self.countdown_label = ctk.CTkLabel(
            countdown_card, text="-- : --", 
            font=("Helvetica", 54, "bold"), text_color=TIME_COLOR
        )
        self.countdown_label.pack(pady=(0, 5))
        
        ctk.CTkLabel(countdown_card, text="mins            secs", font=("Helvetica", 12), text_color=TEXT_MUTED).pack(pady=(0, 20))

        # --- ACTION BUTTONS ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(20, 10))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶ Start Alarm", command=self.start_alarm,
            fg_color=ACCENT_GREEN, hover_color="#28B04A", text_color="white", font=("Helvetica", 16, "bold"), height=45
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.stop_btn = ctk.CTkButton(
            btn_frame, text="⏹ Stop Alarm", command=self.stop_alarm, state="disabled",
            fg_color="#21262D", hover_color="#30363D", text_color=TEXT_LIGHT, font=("Helvetica", 16, "bold"), height=45
        )
        self.stop_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        # --- FOOTER ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=30, pady=10)

        self.status_label = ctk.CTkLabel(footer_frame, text="● Status: Stopped", font=("Helvetica", 12), text_color=TEXT_MUTED)
        self.status_label.pack(side="left")

        self.repeat_label = ctk.CTkLabel(footer_frame, text="", font=("Helvetica", 12), text_color=TEXT_MUTED)
        self.repeat_label.pack(side="right")

    def choose_sound(self):
        file_path = filedialog.askopenfilename(
            title="Select Alarm Sound",
            filetypes=(("Audio Files", "*.mp3 *.wav"), ("All Files", "*.*"))
        )
        if file_path:
            self.alarm_sound_path = file_path
            filename = os.path.basename(file_path)
            self.sound_label.configure(text=f"Selected: {filename}", text_color=ACCENT_GREEN)

    def start_alarm(self):
        try:
            self.interval_minutes = int(self.interval_var.get().split()[0])
        except ValueError:
            messagebox.showerror("Error", "Please select a valid interval.")
            return

        self.is_running = True
        self.start_btn.configure(state="disabled", fg_color="#1A5E2E")
        self.stop_btn.configure(state="normal")
        self.interval_dropdown.configure(state="disabled")
        self.sound_btn.configure(state="disabled")
        
        self.status_label.configure(text="● Status: Running", text_color=ACCENT_GREEN)
        self.repeat_label.configure(text=f"Alarm will repeat every {self.interval_minutes} minutes")

        # Start background thread for the timer
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()

    def stop_alarm(self):
        self.is_running = False
        self.wait_for_user_event.set() # Unpause thread if it was waiting
        
        self.start_btn.configure(state="normal", fg_color=ACCENT_GREEN)
        self.stop_btn.configure(state="disabled")
        self.interval_dropdown.configure(state="normal")
        self.sound_btn.configure(state="normal")
        
        self.status_label.configure(text="● Status: Stopped", text_color=TEXT_MUTED)
        self.repeat_label.configure(text="")
        self.countdown_label.configure(text="-- : --")
        pygame.mixer.music.stop()
        
    def update_countdown_ui(self, time_str):
        # Helper function to safely update the UI from the background thread
        self.countdown_label.configure(text=time_str)

    def run_timer(self):
        while self.is_running:
            self.time_left = self.interval_minutes * 60
            
            while self.time_left > 0 and self.is_running:
                mins, secs = divmod(self.time_left, 60)
                time_str = f"{mins:02d} : {secs:02d}"
                
                # Safely update the custom tkinter label using the helper function
                self.after(0, self.update_countdown_ui, time_str)
                
                time.sleep(1)
                self.time_left -= 1

            if self.is_running:
                self.wait_for_user_event.clear()
                self.after(0, self.trigger_alarm)
                
                # Pause the timer thread until the user clicks OK on the popup
                while not self.wait_for_user_event.is_set() and self.is_running:
                    time.sleep(0.5)

    def trigger_alarm(self):
        # Play Sound
        if self.alarm_sound_path and os.path.exists(self.alarm_sound_path):
            pygame.mixer.music.load(self.alarm_sound_path)
            pygame.mixer.music.play(-1)
        else:
            if os.name == 'nt':
                import winsound
                winsound.Beep(1000, 2000)
        
        # Show popup (Blocks the main UI thread until user clicks OK)
        messagebox.showinfo("Alarm!", f"{self.interval_minutes} minutes have passed!\nClick OK to dismiss and restart timer.")
        
        # Stop sound and resume the background timer
        pygame.mixer.music.stop()
        self.wait_for_user_event.set()

if __name__ == "__main__":
    app = AlarmApp()
    app.mainloop()

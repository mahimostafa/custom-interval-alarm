#This Script below installs all the required libraries to work the application properly

import subprocess
import sys

def install_dependencies():
    try:
        required = {'pygame', 'pip'} 
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed

        if missing:
            print(f"Installing missing packages: {missing}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    except Exception as e:
        print(f"Auto-install failed: {e}")

install_dependencies()

#Main Script starts from here

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import pygame
import os

class AlarmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Interval Alarm")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        # Initialize Pygame Mixer for cross-platform audio
        pygame.mixer.init()

        # Variables
        self.is_running = False
        self.alarm_sound_path = None
        self.interval_minutes = 0
        self.time_left = 0

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.root, text="Recurring Alarm Clock", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=15)

        # Interval Selection
        interval_frame = ttk.Frame(self.root)
        interval_frame.pack(pady=10)
        
        ttk.Label(interval_frame, text="Select Interval (mins):", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        
        self.interval_var = tk.StringVar()
        intervals = ["5", "10", "15", "20", "25", "30", "60"]
        self.interval_dropdown = ttk.Combobox(interval_frame, textvariable=self.interval_var, values=intervals, state="readonly", width=5)
        self.interval_dropdown.pack(side=tk.LEFT)
        self.interval_dropdown.current(0) # Default to 5 mins

        # Sound File Selection
        self.sound_btn = ttk.Button(self.root, text="Choose Alarm Sound (MP3/WAV)", command=self.choose_sound)
        self.sound_btn.pack(pady=10)

        self.sound_label = ttk.Label(self.root, text="No sound selected. Default beep will play.", foreground="gray", wraplength=350, justify="center")
        self.sound_label.pack(pady=5)

        # Start / Stop Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.start_btn = ttk.Button(btn_frame, text="Start Alarm", command=self.start_alarm)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = ttk.Button(btn_frame, text="Stop Alarm", command=self.stop_alarm, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        # Status Label
        self.status_label = ttk.Label(self.root, text="Status: Stopped", font=("Helvetica", 11, "bold"))
        self.status_label.pack(pady=10)
        
        # Countdown Label
        self.countdown_label = ttk.Label(self.root, text="", foreground="blue")
        self.countdown_label.pack()

    def choose_sound(self):
        file_path = filedialog.askopenfilename(
            title="Select Alarm Sound",
            filetypes=(("Audio Files", "*.mp3 *.wav"), ("All Files", "*.*"))
        )
        if file_path:
            self.alarm_sound_path = file_path
            filename = os.path.basename(file_path)
            self.sound_label.config(text=f"Selected: {filename}", foreground="green")

    def start_alarm(self):
        try:
            self.interval_minutes = int(self.interval_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please select a valid interval.")
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.interval_dropdown.config(state=tk.DISABLED)
        self.sound_btn.config(state=tk.DISABLED)
        
        self.status_label.config(text=f"Status: Running (Every {self.interval_minutes} mins)", foreground="green")

        # Start background thread for the timer so GUI doesn't freeze
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()

    def stop_alarm(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.interval_dropdown.config(state="readonly")
        self.sound_btn.config(state=tk.NORMAL)
        
        self.status_label.config(text="Status: Stopped", foreground="black")
        self.countdown_label.config(text="")
        pygame.mixer.music.stop()

    def run_timer(self):
        while self.is_running:
            self.time_left = self.interval_minutes * 60
            
            while self.time_left > 0 and self.is_running:
                # Update countdown in GUI safely
                mins, secs = divmod(self.time_left, 60)
                time_str = f"Next alarm in: {mins:02d}:{secs:02d}"
                self.root.after(0, self.countdown_label.config, {'text': time_str})
                
                time.sleep(1)
                self.time_left -= 1

            if self.is_running:
                self.root.after(0, self.trigger_alarm)

    def trigger_alarm(self):
        # Play Sound
        if self.alarm_sound_path and os.path.exists(self.alarm_sound_path):
            pygame.mixer.music.load(self.alarm_sound_path)
            pygame.mixer.music.play(-1) # -1 means loop continuously
        else:
            # Fallback beep if no file selected (Requires Windows, on Mac/Linux it just pops up)
            if os.name == 'nt':
                import winsound
                winsound.Beep(1000, 2000)
        
        # Show popup (This blocks until the user clicks OK)
        messagebox.showinfo("Alarm!", f"{self.interval_minutes} minutes have passed!\nClick OK to dismiss and restart timer.")
        
        # Stop sound when user clicks OK
        pygame.mixer.music.stop()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set a clean modern theme if available
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
        
    app = AlarmApp(root)
    root.mainloop()

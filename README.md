# ⏰ Custom Interval Alarm

I built this small app to solve a simple problem:  
sometimes you just need a reminder that repeats — not a one-time alarm.

This is a lightweight desktop app where you can set a time interval, and it will keep reminding you until you stop it. Great for studying, taking breaks, or staying consistent with habits.

---

## ✨ What it does

- Lets you set a repeating alarm (every 5, 10, 15 mins, etc.)
- Shows a live countdown so you always know what’s next
- Allows you to use your own sound (MP3/WAV)
- Falls back to a basic beep if you don’t choose one
- Simple, clean interface — no clutter

---

## 🛠 Built with

- Python  
- Tkinter (for the UI)  
- Pygame (for sound)  
- Threading (so the app doesn’t freeze)

---

## 🚀 Getting started

Clone the repo:

```bash
git clone https://github.com/your-username/custom-interval-alarm.git
cd custom-interval-alarm

Run the app:

python reminder-alert-2.0.py

The script will try to install missing dependencies automatically if needed.

🧑‍💻 How to use
Pick a time interval
(Optional) Select a custom sound
Click Start Alarm
Let it run in the background

When time’s up:

The sound plays
A popup shows up

Click OK, and it starts counting again.

💡 Why I made this

Most reminder apps are either too complex or don’t support simple repeating intervals the way I wanted.
So I made my own — something minimal, fast, and actually useful.

⚠️ A couple of notes
If you don’t select a sound, Windows will use a basic beep
On other systems, it’s better to choose a sound file
Works best with Python 3 installed properly
🔧 Things I might add later
Custom time input (instead of fixed options)
Multiple alarms
Dark mode
Saving your settings
🤝 Contributions

If you’ve got ideas or improvements, feel free to fork it or open a PR.

📄 License

MIT — use it however you want.

👤 Author

Made by Mahi Mostafa

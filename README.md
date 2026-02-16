# 10,000 Hours Tracker ⏱️

> *"Downloading this will automatically create a json file documenting your progress. Start now, believe the progress, get better."*

This is a lightweight, offline desktop application designed to help you track your cumulative study and practice time across multiple subjects. It is built around the philosophy of the 10,000-hour rule: focus on the total accumulated effort rather than micromanaging daily schedules.

## ✨ Features

* **Simple Time Tracking:** A clean start/stop interface to log your study sessions.
* **Custom Subjects:** Add new subjects or delete old ones as your focus changes.
* **Progress Visualization:** Built-in charting tool that plots your cumulative growth over time using a step graph.
* **Manual Entry:** Easily add past hours if you are migrating from another tracking method.
* **Local Data Ownership:** All your data is stored locally in a simple, human-readable `10000_hours_data.json` file. No accounts or internet connection required.
* **Developer Friendly (Auto-Sync):** If the executable (or script) is run inside an initialized Git repository, it will automatically pull, commit, and push your progress to your remote branch every time you stop the timer.

## 🚀 How to Use (Standard Users)

If you just want to track your hours without touching any code:

1. Go to the **Releases** section on the right side of this page.
2. Download the latest `tracker.exe` file.
3. Create a new folder on your computer (e.g., "My Study Tracker") and place the `.exe` inside it.
4. Double-click to run! 

*Note: The app will automatically generate a `10000_hours_data.json` file in the same folder. Keep this file in the same location as the `.exe` so the app can load your saved hours next time you open it.*

## 💻 For Developers (Running from Source)

If you want to run the Python script directly or modify the code:

**1. Clone the repository:**
```bash
git clone [https://github.com/liuhon33/10k_hours_tracker.git](https://github.com/liuhon33/10k_hours_tracker.git)
cd 10k_hours_tracker
```

**2. Install dependencies:**
The GUI uses Python's built-in `tkinter`, but you will need `matplotlib` for the graphing feature.
```bash
pip install matplotlib
```

**3. Run the application:**
```bash
python tracker.py
```

## 📈 About the Graph
The "Show Growth Graph" feature plots your journey using a step-forward line. This accurately represents cumulative time—showing a flat line between study sessions and stepping up vertically only when you put the work in. Keep making it step up!
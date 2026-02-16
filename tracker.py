import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import time
import os
import subprocess

# --- Configuration ---
# Set this to the path of your local Git repository folder. 
# "." means the folder where this script is currently located.
REPO_DIR = "." 
DATA_FILE = os.path.join(REPO_DIR, "10000_hours_data.json")

class StudyTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("10,000 Hours Tracker")
        self.geometry("380x300")
        self.resizable(False, False)

        self.default_subjects = ["python", "stats", "bioinformatics", "machine learning", "linear algebra"]
        
        # 1. Pull the latest data from GitHub first
        self.pull_from_github()
        
        # 2. Then load the data into the app
        self.data = self.load_data()
        
        self.current_subject = tk.StringVar(value=self.default_subjects[0])
        self.start_time = None
        self.is_running = False
        self.session_seconds = 0

        self.setup_ui()
        self.update_clock()

    def pull_from_github(self):
        """Automatically pulls the latest data from GitHub on startup."""
        try:
            # Pulls from the remote named 'origin' and branch 'main'
            subprocess.run(["git", "pull", "origin", "main"], cwd=REPO_DIR, check=True, capture_output=True)
            print("Successfully pulled latest data from GitHub.")
        except subprocess.CalledProcessError as e:
            # Fails silently in the UI, but prints to console for debugging
            print(f"Git pull failed (you might be offline or have local conflicts): {e}")

    def sync_with_github(self):
        """Automatically commits and pushes changes to GitHub."""
        try:
            subprocess.run(["git", "add", DATA_FILE], cwd=REPO_DIR, check=True, capture_output=True)
            commit_msg = "Auto-update: Added study time"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_DIR, check=True, capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True, capture_output=True)
            print("Successfully synced to GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Git push failed: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {sub: 0 for sub in self.default_subjects}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
        # Push to GitHub immediately after saving locally
        self.sync_with_github()

    def setup_ui(self):
        ttk.Label(self, text="Select Subject:", font=("Arial", 12)).pack(pady=(15, 5))
        dropdown = ttk.OptionMenu(self, self.current_subject, self.current_subject.get(), *self.data.keys(), command=self.on_subject_change)
        dropdown.pack()

        self.time_label = ttk.Label(self, text="0.0000 Hours", font=("Arial", 26, "bold"))
        self.time_label.pack(pady=15)

        self.btn_frame = ttk.Frame(self)
        self.btn_frame.pack(pady=5)

        self.start_btn = ttk.Button(self.btn_frame, text="Start", command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(self.btn_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.add_manual_btn = ttk.Button(self, text="Add Past Hours", command=self.add_manual_hours)
        self.add_manual_btn.pack(pady=15)

    def on_subject_change(self, *args):
        if self.is_running:
            self.stop_timer()
        self.update_display()

    def start_timer(self):
        self.is_running = True
        self.start_time = time.time()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.add_manual_btn.config(state=tk.DISABLED)

    def stop_timer(self):
        if not self.is_running: return
        
        self.is_running = False
        elapsed = time.time() - self.start_time
        
        subject = self.current_subject.get()
        self.data[subject] += elapsed
        self.save_data() 
        
        self.session_seconds = 0
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.add_manual_btn.config(state=tk.NORMAL)
        self.update_display()

    def add_manual_hours(self):
        subject = self.current_subject.get()
        hours_str = simpledialog.askstring("Add Past Hours", f"How many hours do you want to add to {subject}?")
        
        if hours_str:
            try:
                hours_to_add = float(hours_str)
                if hours_to_add < 0:
                    raise ValueError
                
                self.data[subject] += (hours_to_add * 3600)
                self.save_data()
                self.update_display()
                messagebox.showinfo("Success", f"Added {hours_to_add} hours to {subject}.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number.")

    def update_clock(self):
        if self.is_running:
            self.session_seconds = time.time() - self.start_time
            self.update_display()
        self.after(1000, self.update_clock)

    def update_display(self):
        subject = self.current_subject.get()
        total_seconds = self.data.get(subject, 0) + self.session_seconds
        total_hours = total_seconds / 3600
        self.time_label.config(text=f"{total_hours:.4f} Hours")

if __name__ == "__main__":
    app = StudyTracker()
    app.mainloop()
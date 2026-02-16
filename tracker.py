import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import time
import os
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt

# --- Configuration ---
REPO_DIR = "." 
DATA_FILE = os.path.join(REPO_DIR, "10000_hours_data.json")

class StudyTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("10,000 Hours Tracker")
        self.geometry("400x380")
        self.resizable(False, False)

        self.default_subjects = ["python", "stats", "bioinformatics", "machine learning",]
        
        self.pull_from_github()
        self.data = self.load_data()
        
        # Ensure at least one subject exists
        if not self.data:
            self.data = {sub: [{"timestamp": time.time(), "total_seconds": 0}] for sub in self.default_subjects}

        self.current_subject = tk.StringVar(value=list(self.data.keys())[0])
        self.start_time = None
        self.is_running = False
        self.session_seconds = 0

        self.setup_ui()
        self.update_clock()

        self.update_display() 
        
        self.update_clock()

    def pull_from_github(self):
        try:
            subprocess.run(["git", "pull", "origin", "master"], cwd=REPO_DIR, check=True, capture_output=True, text=True)
            print("Successfully pulled latest data from GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Git pull failed. Reason:\n{e.stderr}")

    def sync_with_github(self):
        try:
            subprocess.run(["git", "add", DATA_FILE], cwd=REPO_DIR, check=True, capture_output=True, text=True)
            subprocess.run(["git", "commit", "-m", "Auto-update: Added study time/subject"], cwd=REPO_DIR, check=True, capture_output=True, text=True)
            subprocess.run(["git", "push", "origin", "master"], cwd=REPO_DIR, check=True, capture_output=True, text=True)
            print("Successfully synced to GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Git push failed. Reason:\n{e.stderr}")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
            
        with open(DATA_FILE, "r") as f:
            raw_data = json.load(f)
            
        # Data Migration: Convert old flat format to time-series format
        migrated_data = {}
        needs_save = False
        for subject, value in raw_data.items():
            if isinstance(value, (int, float)):
                migrated_data[subject] = [{"timestamp": time.time(), "total_seconds": value}]
                needs_save = True
            else:
                migrated_data[subject] = value
                
        if needs_save:
            self.data = migrated_data
            self.save_data()
            
        return migrated_data

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)
        self.sync_with_github()

    def setup_ui(self):
        # Subject Selection Area
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=(15, 5))
        
        ttk.Label(top_frame, text="Select Subject:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        
        self.dropdown = ttk.Combobox(top_frame, textvariable=self.current_subject, values=list(self.data.keys()), state="readonly", width=15)
        self.dropdown.grid(row=0, column=1, padx=5)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_subject_change)
        
        self.add_sub_btn = ttk.Button(top_frame, text="+ New", width=6, command=self.add_new_subject)
        self.add_sub_btn.grid(row=0, column=2, padx=2)

        # NEW: Delete Button
        self.del_sub_btn = ttk.Button(top_frame, text="- Delete", width=8, command=self.delete_subject)
        self.del_sub_btn.grid(row=0, column=3, padx=2)

        # Time Display
        self.time_label = ttk.Label(self, text="0.0000 Hours", font=("Arial", 26, "bold"))
        self.time_label.pack(pady=15)

        # Timer Buttons
        self.btn_frame = ttk.Frame(self)
        self.btn_frame.pack(pady=5)

        self.start_btn = ttk.Button(self.btn_frame, text="Start", command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(self.btn_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5)

        # Utility Buttons
        self.add_manual_btn = ttk.Button(self, text="Add Past Hours", command=self.add_manual_hours)
        self.add_manual_btn.pack(pady=(20, 5))
        
        self.graph_btn = ttk.Button(self, text="Show Growth Graph", command=self.show_graph)
        self.graph_btn.pack(pady=5)

    def refresh_dropdown(self):
        # Much cleaner Combobox update
        self.dropdown['values'] = list(self.data.keys())

    def add_new_subject(self):
        new_subject = simpledialog.askstring("New Subject", "Enter the name of the new subject:")
        if new_subject:
            new_subject = new_subject.strip()
            if new_subject in self.data:
                messagebox.showwarning("Duplicate", "This subject already exists.")
                return
            
            # Initialize new subject with 0 hours
            self.data[new_subject] = [{"timestamp": time.time(), "total_seconds": 0}]
            self.save_data()
            self.refresh_dropdown()
            self.current_subject.set(new_subject)
            self.update_display()
    
    def delete_subject(self):
        subject_to_delete = self.current_subject.get()
        
        # Guardrail: Prevent deleting the last remaining subject
        if len(self.data) <= 1:
            messagebox.showwarning("Cannot Delete", "You must have at least one subject. Add a new one first before deleting this one.")
            return

        # Warning pop-up to prevent accidental deletion
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to permanently delete '{subject_to_delete}' and all its tracked hours?\n\nThis will sync to GitHub and cannot be easily undone."
        )
        
        if confirm:
            # Delete the data
            del self.data[subject_to_delete]
            
            # Save to JSON and push to GitHub
            self.save_data()
            
            # Refresh the dropdown list
            self.refresh_dropdown()
            
            # Set the dropdown to whatever subject is currently first in the list
            new_subject = list(self.data.keys())[0]
            self.current_subject.set(new_subject)
            
            # Update the big timer display
            self.update_display()

    def get_current_total_seconds(self, subject):
        if not self.data.get(subject):
            return 0
        return self.data[subject][-1]["total_seconds"]

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
        self.add_sub_btn.config(state=tk.DISABLED)

    def stop_timer(self):
        if not self.is_running: return
        
        self.is_running = False
        elapsed = time.time() - self.start_time
        
        subject = self.current_subject.get()
        new_total = self.get_current_total_seconds(subject) + elapsed
        
        # Append the new session to the history
        self.data[subject].append({"timestamp": time.time(), "total_seconds": new_total})
        self.save_data() 
        
        self.session_seconds = 0
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.add_manual_btn.config(state=tk.NORMAL)
        self.add_sub_btn.config(state=tk.NORMAL)
        self.update_display()

    def add_manual_hours(self):
        subject = self.current_subject.get()
        hours_str = simpledialog.askstring("Add Past Hours", f"How many hours do you want to add to {subject}?")
        
        if hours_str:
            try:
                hours_to_add = float(hours_str)
                if hours_to_add < 0:
                    raise ValueError
                
                new_total = self.get_current_total_seconds(subject) + (hours_to_add * 3600)
                self.data[subject].append({"timestamp": time.time(), "total_seconds": new_total})
                self.save_data()
                self.update_display()
                messagebox.showinfo("Success", f"Added {hours_to_add} hours to {subject}.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number.")

    def show_graph(self):
        plt.figure(figsize=(10, 6))
        
        has_data = False
        for subject, history in self.data.items():
            if not history or history[-1]["total_seconds"] == 0:
                continue # Skip subjects with zero total hours
                
            has_data = True
            # Extract timestamps and convert to datetime objects
            dates = [datetime.fromtimestamp(entry["timestamp"]) for entry in history]
            # Convert seconds to hours
            hours = [entry["total_seconds"] / 3600 for entry in history]
            
            # Plot as a step-forward line so the graph stays flat between sessions
            plt.step(dates, hours, where='post', marker='o', label=subject)

        if not has_data:
            messagebox.showinfo("No Data", "No study hours logged yet to graph.")
            plt.close()
            return

        plt.title("10,000 Hours Journey")
        plt.xlabel("Date")
        plt.ylabel("Cumulative Hours")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

    def update_clock(self):
        if self.is_running:
            self.session_seconds = time.time() - self.start_time
            self.update_display()
        self.after(1000, self.update_clock)

    def update_display(self):
        subject = self.current_subject.get()
        total_seconds = self.get_current_total_seconds(subject) + self.session_seconds
        total_hours = total_seconds / 3600
        self.time_label.config(text=f"{total_hours:.4f} Hours")

if __name__ == "__main__":
    app = StudyTracker()
    app.mainloop()
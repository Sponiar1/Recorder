import tkinter as tk
from tkinter import messagebox
import threading
from audioRecorder import AudioRecorder

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Recorder")
        self.root.resizable(True, True)
        self.root.geometry("1270x700")
        self.recorder = AudioRecorder()

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        tk.Label(self.frame, text="Filename: ").pack()
        self.filename_entry = tk.Entry(self.frame, width=30)
        self.filename_entry.insert(0, "recording.wav")
        self.filename_entry.pack(pady=5)

        tk.Label(self.frame, text="Duration: ").pack()
        self.duration_entry = tk.Entry(self.frame, width=10)
        self.duration_entry.insert(0, "5")
        self.duration_entry.pack(pady=5)

        self.record_button = tk.Button(self.frame, text="Record", command=self.start_recording)
        self.record_button.pack(pady=5)

        self.stop_button = tk.Button(self.frame, text="Stop recording", command=self.stop_recording)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(self.frame, text="Ready")
        self.status_label.pack(pady=5)

    def start_recording(self):
        try:
            duration = float(self.duration_entry.get())
            if duration <= 0:
                messagebox.showerror("Error", "Duration must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Error", "Duration must be a positive number.")
            return

        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Recording...")

        def record_thread():
            success, message = self.recorder.start(duration=duration)
            self.root.after(0, self.update_status, success, message)

        threading.Thread(target=record_thread).start()

    def stop_recording(self):
        self.recorder.stop()
        self.update_status(True, "Stopped")

    def update_status(self, success, message):
        self.status_label.config(text=message)
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        if success and not self.recorder.stop():
            filename = self.filename_entry.get().strip()
            success, save_message = self.recorder.save(filename)
            messagebox.showinfo("success", save_message) if success else messagebox.showerror("error", save_message)


    def run(self):
        self.root.mainloop()
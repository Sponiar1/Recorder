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

    def run(self):
        self.root.mainloop()
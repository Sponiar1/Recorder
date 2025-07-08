import tkinter as tk
from tkinter import messagebox
import threading
from audioRecorder import AudioRecorder

class GUI:
    def __init__(self, root):
        #Window
        self.root = root
        self.root.title("Recorder")
        self.root.resizable(True, True)
        self.root.geometry("800x600")
        self.recorder = AudioRecorder()

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        #Input label
        tk.Label(self.frame, text="Vstupné zariadenie:").pack()
        self.device_var = tk.StringVar()
        self.device_map = self.get_device_map()
        device_names = list(self.device_map.keys())
        self.device_menu = tk.OptionMenu(self.frame, self.device_var, *device_names)
        self.device_menu.pack(pady=5)
        default_device_index = self.recorder.device
        if default_device_index is not None:
            for name, index in self.device_map.items():
                if index == default_device_index:
                    self.device_var.set(name)
                    break
        else:
            self.device_var.set(device_names[0] if device_names else "No device detected")
        self.device_var.trace("w", self.update_device)

        # Format label
        tk.Label(self.frame, text="Formát:").pack()
        self.format_var = tk.StringVar(value="wav")
        format_menu = tk.OptionMenu(self.frame, self.format_var, "wav","mp3")
        format_menu.pack(pady=5)

        #Filename label
        tk.Label(self.frame, text="Filename: ").pack()
        self.filename_entry = tk.Entry(self.frame, width=30)
        self.filename_entry.insert(0, "recording")
        self.filename_entry.pack(pady=5)

        #Buttons
        self.record_button = tk.Button(self.frame, text="Record", command=self.start_recording)
        self.record_button.pack(pady=5)
        self.stop_button = tk.Button(self.frame, text="Stop recording", command=self.stop_recording)
        self.stop_button.pack(pady=5)

        #Status Label
        self.status_label = tk.Label(self.frame, text="Ready")
        self.status_label.pack(pady=5)

        #Rec Label
        self.rec_indicator = tk.Label(self.root, text="● REC", fg="red", font=("Arial", 14, "bold"))
        self.rec_indicator.place(relx=0.95, rely=0.05, anchor="ne")
        self.rec_indicator.place_forget()

        self.popup = None

    def get_device_map(self):
        devices = self.recorder.getAvailableDevices()
        return {name: i for i, name in devices}


    def update_device(self, *args):
        selected = self.device_var.get()
        if selected and selected != "No device detected":
            device_index = self.device_map.get(selected)
            if device_index is not None:
                success, message = self.recorder.setDevice(device_index)
                self.status_label.config(text=message)
                if not success:
                    messagebox.showerror("Chyba", message)

    def start_recording(self):
        if self.device_var.get() == "No device detected":
            messagebox.showerror("Error", "Select input device")
            return

        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Recording")
        self.rec_indicator.place(relx=0.95, rely=0.05, anchor="ne")

        def record_thread():
            success, message = self.recorder.start()
            if not success:
                self.root.after(0, lambda: self.status_label.config(text=message))
                self.root.after(0, lambda: self.record_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.rec_indicator.place_forget())

        threading.Thread(target=record_thread, daemon = True).start()

    def stop_recording(self):
        self.recorder.stop()
        self.rec_indicator.place_forget()
        self.update_status(True, "Stopped")

    def update_status(self, success, message):
        self.status_label.config(text=message)
        if success and self.recorder.stopped:
            self.record_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            filename = self.filename_entry.get().strip()
            file_format = self.format_var.get()
            success, save_message = self.recorder.save(filename, file_format)
            self.show_popup("Success" if success else "Error", save_message, "success" if success else "error")

    def show_popup(self, title, message, popup_type):
        if self.popup:
            self.popup.destroy()

        self.popup = tk.Toplevel(self.root)
        self.popup.title(title)
        self.popup.geometry("250x100")
        self.popup.resizable(False, False)
        self.popup.transient(self.root)
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        self.popup.lift()
        self.popup.focus_force()
        self.popup.update()
        bg_color = "light green" if popup_type == "success" else "light coral"
        self.popup.configure(bg=bg_color)

        frame = tk.Frame(self.popup, bg=bg_color)
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(frame, text=message, wraplength=200, bg=bg_color, font=("Arial", 10)).pack(pady=5)
        close_button = tk.Button(frame, text="✕", command=self.popup.destroy, bg=bg_color, font=("Arial", 10),
                                 relief="flat")
        close_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.popup.update_idletasks()
        width=self.popup.winfo_width()
        height = self.popup.winfo_height()
        x = self.root.winfo_x() + self.root.winfo_width() - width - 10
        y = self.root.winfo_y() + self.root.winfo_height() - height - 10
        self.popup.geometry(f"{width}x{height}+{x}+{y}")

        self.popup.attributes("-alpha", 0.0)
        def fade_in(alpha = 0.0):
            alpha += 0.1
            self.popup.attributes("-alpha", min(alpha, 1.0))
            if alpha  < 1.0:
                self.root.after(50, fade_in, alpha)

        fade_in()
        self.root.after(3000, lambda: self.popup.destroy() if self.popup.winfo_exists() else None)

    def run(self):
        self.root.mainloop()
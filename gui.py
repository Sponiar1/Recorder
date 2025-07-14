import subprocess
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
import threading
from audioRecorder import AudioRecorder
from settings import Settings
import os

class GUI:
    def __init__(self, root, setting: Settings):
        #Window
        self.root = root
        self.root.title("Recorder")
        self.root.resizable(True, True)
        self.root.geometry("800x500")
        self.recorder = AudioRecorder()
        self.setting = setting

        self.option_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.button_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.toolbar_frame = ttk.Frame(self.root, padding="10 10 10 10")

        self.option_frame.place(x=10, y=10, anchor="nw")
        self.button_frame.place(relx=0.5, y=10, anchor="n")
        self.toolbar_frame.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

        # Input label
        ttk.Label(self.option_frame, text="Input device:").pack(anchor="w")
        self.device_var = ttk.StringVar()
        self.device_map = self.get_device_map()
        device_names = list(self.device_map.keys())
        self.device_menu = ttk.OptionMenu(self.option_frame, self.device_var, *device_names)
        self.device_menu.pack(pady=5, anchor="w")
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
        ttk.Label(self.option_frame, text="Format:").pack(anchor="w")
        loaded_format=self.get_setting("LAST_SETTINGS", "Format")
        self.format_var = ttk.StringVar(value=loaded_format)
        format_menu = ttk.OptionMenu(self.option_frame, self.format_var, loaded_format, "mp3", "wav", command= lambda value: self.update_setting("LAST_SETTINGS", "Format", value))
        format_menu.pack(pady=5, anchor="w")

        # Filename entry
        ttk.Label(self.option_frame, text="Filename: ").pack(anchor="w")
        self.filename_entry = ttk.Entry(self.option_frame, width=30)
        self.filename_entry.insert(0, "recording")
        self.filename_entry.pack(pady=5, anchor="w")

        # Filepath entry
        ttk.Label(self.option_frame, text="Save location: ").pack(anchor="w")
        self.filepath_var = ttk.StringVar()
        self.filepath_entry = ttk.Entry(self.option_frame, textvariable=self.filepath_var, width=50, state="readonly")
        self.filepath_var.set(self.setting.load_settings("LAST_SETTINGS", "last_path"))
        self.filepath_entry.pack(pady=5, anchor="w")
        self.browse_button = ttk.Button(self.option_frame, text="Browse", command=self.browse)
        self.browse_button.pack(pady=5, anchor="w")
        self.explorer_button = ttk.Button(self.option_frame, text="Open", command=self.open_folder)
        self.explorer_button.pack(pady=5, anchor="ne")
        # Status Label
        self.status_label = ttk.Label(self.button_frame, text="Ready")
        self.status_label.pack(pady=2)

        # Buttons
        self.record_button = ttk.Button(self.button_frame, text="Record", command=self.start_recording)
        self.record_button.pack(pady=5)
        self.stop_button = ttk.Button(self.button_frame, text="Stop recording", command=self.stop_recording)
        self.stop_button.pack(pady=5)
        self.stop_button.configure(state="disabled")

        # Theme Buttons
        self.current_theme = self.root.style.theme_use()
        self.theme_button = ttk.Button(self.toolbar_frame, command=self.toggle_theme)
        if self.current_theme == "darkly":
            self.dark_mode = True
            self.theme_button.configure(text="☀️ Light")
        else:
            self.dark_mode = False
            self.theme_button.configure(text="🌙 Dark")

        self.theme_button.place(x=10, rely=0.9, anchor="sw")
        self.theme_button.pack()

        # Rec Label
        self.rec_indicator = ttk.Label(self.root, text="● REC", foreground="red", font=("Arial", 14, "bold"))
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
                #self.status_label.config(text=message)
                self.show_popup("Input changed", message, "success")
                if not success:
                    messagebox.showerror("Error", message)

    def start_recording(self):
        if self.device_var.get() == "No device detected":
            messagebox.showerror("Error", "Select input device")
            return

        self.record_button.config(state=ttk.DISABLED)
        self.stop_button.config(state=ttk.NORMAL)
        self.status_label.config(text="Recording")
        self.rec_indicator.place(relx=0.95, rely=0.05, anchor="ne")

        def record_thread():
            success, message = self.recorder.start()
            if not success:
                self.root.after(0, lambda: self.status_label.config(text=message))
                self.root.after(0, lambda: self.record_button.config(state=ttk.NORMAL))
                self.root.after(0, lambda: self.stop_button.config(state=ttk.DISABLED))
                self.root.after(0, lambda: self.rec_indicator.place_forget())

        threading.Thread(target=record_thread, daemon = True).start()

    def stop_recording(self):
        self.recorder.stop()
        self.rec_indicator.place_forget()
        self.update_status(True, "Stopped")

    def update_status(self, success, message):
        self.status_label.config(text=message)
        if success and self.recorder.stopped:
            self.record_button.config(state=ttk.NORMAL)
            self.stop_button.config(state=ttk.DISABLED)
            filename = self.filename_entry.get().strip()
            file_format = self.format_var.get()
            success, save_message = self.recorder.save(filename, file_format)
            self.show_popup("Success" if success else "Error", save_message, "success" if success else "error")

    def browse(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.update_setting("LAST_SETTINGS", "last_path", folder_path)
            self.filepath_var.set(folder_path)

    def open_folder(self):
        path = self.filepath_var.get()
        print(f"Trying to open: {path}")
        if os.path.isdir(path):
            #subprocess.Popen(f'explorer "{path}"', shell=True)
            os.startfile(path)
        else:
            print("Path is invalid or does not exist!")

    def show_popup(self, title, message, popup_type):
        if self.popup:
            self.popup.destroy()

        self.popup = ttk.Toplevel(self.root)
        self.popup.title(title)
        self.popup.geometry("200x100")
        self.popup.resizable(False, False)
        self.popup.transient(self.root)
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        self.popup.lift()

        frame = ttk.Frame(self.popup, bootstyle=popup_type, padding=5)
        frame.pack(fill="both", expand=True)

        label = ttk.Label(frame, text=message, wraplength=150, justify="left", font=("Arial", 9),
                          background="#00bc8c")
        label.pack(side="left", padx=5, fill="y")

        close_button = ttk.Button(frame, text="X", command=self.popup.destroy, style=f"{popup_type}.TButton")
        close_button.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

        self.popup.update()
        x = self.root.winfo_x() + self.root.winfo_width() - 210
        y = self.root.winfo_y() + self.root.winfo_height() - 110
        self.popup.geometry(f"+{x}+{y}")

        self.popup.attributes("-alpha", 0.0)

        def fade_in(alpha=0.0):
            alpha += 0.1
            self.popup.attributes("-alpha", min(alpha, 1.0))
            if alpha < 1.0:
                self.root.after(50, fade_in, alpha)

        fade_in()
        self.root.after(3000, lambda: self.popup.destroy() if self.popup.winfo_exists() else None)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.root.style.theme_use("darkly")
            self.theme_button.configure(text="☀️ Light")
            self.update_setting("LAST_SETTINGS", "theme", "darkly")
        else:
            self.root.style.theme_use("flatly")
            self.theme_button.configure(text="🌙 Dark")
            self.update_setting("LAST_SETTINGS", "theme", "flatly")

    def update_setting(self, section, key, value):
        self.setting.save_settings(section, key, value)

    def get_setting(self, section, key):
        return self.setting.load_settings(section, key)

    def run(self):
        self.root.mainloop()
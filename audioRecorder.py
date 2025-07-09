import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import subprocess

class AudioRecorder:
    def __init__(self):
        # Sampling frequency
        self.freq = 44100
        # Channel
        self.channels = 2
        self.isRecording = False
        self.recording = None
        self.stopped = False
        self.device = None
        self.stream = None
        self.frames = []
        self.setDefaultDevice()

    def setDefaultDevice(self):
        try:
            default_device = sd.default.device[0]
            self.device = default_device
            return True, f"Default device: {sd.query_devices()[default_device]['name']}"
        except Exception as e:
            return False, str(e)

    def getAvailableDevices(self):
        devices = sd.query_devices()
        seen_names = set()
        input_devices = []
        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0:
                name = d['name'].lower()
                if name not in seen_names and ('mic' in name or 'microphone' in name):
                    input_devices.append((i, d['name']))
                    seen_names.add(name)
        if not input_devices:
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0 and d['name'].lower() not in seen_names:
                    input_devices.append((i, d['name']))
                    seen_names.add(d['name'].lower())
        return input_devices

    def setDevice(self, device):
        try:
            sd.default.device = device
            self.device = device
            return True, f"Device set to {sd.query_devices()[device]['name']}"
        except Exception as e:
            return False, f"Failed to set device: {e}"

    def start(self):
        if self.isRecording:
            return False, "Recording already started."

        print("Recording...")
        self.isRecording = True
        self.stopped = False
        self.frames = []
        try:
            self.stream = sd.InputStream(
                samplerate=self.freq,
                channels=self.channels,
                device=self.device,
                callback=self._callback
            )
            self.stream.start()
            return True, "Recording started."
        except Exception as e:
            self.isRecording = False
            return False, f"Failed to start recording: {e}"

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"Stream status: {status}")
        if self.isRecording:
            self.frames.append(indata.copy())

    def stop(self):
        if not self.isRecording:
            return
        self.stopped = True
        self.isRecording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.recording = np.concatenate(self.frames, axis=0) if self.frames else None

    def save(self, filename, file_format='wav'):
        if self.recording is None:
            return False, "Nothing to save"

        base_name = filename if not filename.endswith(f".{file_format}") else filename[:-len(file_format) - 1]
        full_name = f"{base_name}.{file_format}"
        counter = 1

        while os.path.exists(full_name):
            full_name = f"{base_name}({counter}).{file_format}"
            counter += 1

        try:
            temp_wav = f"{base_name}_temp.wav"
            write(temp_wav, self.freq, self.recording)

            if file_format == "wav":
                os.rename(temp_wav, full_name)
            elif file_format == "mp3":
                subprocess.run(
                    ["bin\\ffmpeg\\ffmpeg.exe", "-y", "-i", temp_wav, full_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                os.remove(temp_wav)
            else:
                os.remove(temp_wav)
                return False, f"Unsupported format: {file_format}"

            return True, f"Saved recording as {file_format.upper()}"
        except Exception as e:
            return False, f"Failed to save recording: {e}"

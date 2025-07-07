import sounddevice as sd
import wavio as w
import numpy as np
import scipy as sc
from scipy.io.wavfile import write

class AudioRecorder:
    def __init__(self):
        # Sampling frequency
        self.freq = 44100
        # Recording duration
        self.duration = 5
        # Channel
        self.channels = 2
        self.isRecording = False
        self.recording = None
        self.stopped = False

    def start(self, duration):
        if self.isRecording:
            print("Recording already started.")
            return False

        print("Recording...")
        self.isRecording = True
        try:
            self.recording = sd.rec(int(duration * self.freq),samplerate=self.freq,channels=self.channels)
            sd.wait()
            if not self.stopped:
                return True, "Recording finished."
            else:
                return True, "Recording stopped."
        except Exception as e:
            self.isRecording = False
            return False, f"Failed to start recording: {e}"
        finally:
            self.isRecording = False

    def stop(self):
        self.stopped = True
        self.isRecording = False
        sd.stop()

    def save(self, filename):
        if self.recording:
            return False, "Nothing to save"
        if filename.endswith(".wav"):
            filename += ".wav"

        try:
            write(filename,self.freq,self.recording)
            #w.write(filename, recording, freq, sampwidth=2)
            return True, "Saved recording"
        except Exception as e:
            return False, f"Failed to save recording: {e}"

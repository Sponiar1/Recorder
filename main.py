import sounddevice as sd
import wavio as w
import numpy as np
import scipy as sc
from scipy.io.wavfile import write

# Sampling frequency
freq = 44100
# Recording duration
duration = 5
# Channel
channels = 2

print("Recording...")
recording = sd.rec(int(duration * freq),samplerate=freq,channels=channels)
sd.wait()
print("Recording finished")
write("recording1.wav",freq,recording)
#w.write("recording2.wav", recording, freq,sampwidth=2  )

import wave
import numpy as np

w = wave.open("test.wav", 'rb')
astr = w.readframes(w.getnframes())

frames = np.fromstring(astr, np.int16)
frames.shape = (w.getnframes(), w.getnchannels())
frames = frames.T
frames_float = frames.astype(np.float64) / 32768.0

frames_out = (frames_float * 32768.0).astype(np.int16)
frames_out = frames_out.T
str_out = frames_out.tostring()

w_out = wave.open("testout.wav", 'wb')
w_out.setframerate(w.getframerate())
w_out.setnchannels(w.getnchannels())
w_out.setsampwidth(w.getsampwidth())
w_out.writeframes(str_out)
w_out.close()



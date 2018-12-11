import wave
import audiohelper
import numpy as np
import struct

class WavPlayer:
    def __init__(self):
        self.file_path = None
        self.file = None
        self.file_data = None

        self.channels = None
        self.nframes = None
        self.bytes_type = None

        self.current_pos = None
        self.start = None
        self.end = None
        self.on_changed_pos = None

        self._is_running = False
        self._is_ready = False

    def is_ready(self):
        return self._is_ready

    def load(self, file_path):
        self.file_path = file_path
        self.file = wave.open(file_path, 'rb')

        self.channels = self.file.getnchannels()
        self.nframes = self.file.getnframes()
        sample_width = self.file.getsampwidth()
        if sample_width == 1:
            self.bytes_type = np.int8
        elif sample_width == 2:
            self.bytes_type = np.int16
        elif sample_width == 4:
            self.bytes_type = np.int32
        else:
            raise ValueError('Unsupported sample_width %s.' % str(sample_width))

        all_frames = self.file.readframes(self.nframes)
        self.file_data = audiohelper.convert_frame_from_bytes_to_numpy(all_frames, self.channels)
        self.start = 0
        self.current_pos = 0
        self.end = self.nframes
        self._is_ready = True

    def get_frames_numpy(self, nframes):
        if not self._is_running:
            self.current_pos = self.start
            self._is_running = True

        nframes_till_end = self.end - self.current_pos
        nframes_to_read = min(nframes_till_end, nframes)

        frame = self.file_data[:, self.current_pos:self.current_pos + nframes_to_read]
        self.current_pos += nframes_to_read

        if nframes_to_read < nframes:
            self.current_pos = self.start

            nframes_remaining = nframes - nframes_to_read
            frame2 = self.file_data[:, self.current_pos:self.current_pos + nframes_remaining]

            full_frame = np.concatenate((frame, frame2), axis=1)
            if self.on_changed_pos is not None:
                self.on_changed_pos(self.current_pos / float(self.file.getframerate()))
            return full_frame
        else:
            if self.on_changed_pos is not None:
                self.on_changed_pos(self.current_pos/ float(self.file.getframerate()))
            return frame

    def register_on_changed_pos(self, callback):
        self.on_changed_pos = callback

    def set_start(self, value):
        self.start = int(value * self.file.getframerate())

    def set_end(self, value):
        self.end = int(value * self.file.getframerate())

    def get_duration(self):
        return self.file.getnframes() / float(self.file.getframerate())



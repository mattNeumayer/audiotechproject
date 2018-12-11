import wave


class WavRecorder:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = wave.open(file_path, 'wb')

        self._is_ready = False

    def is_ready(self):
        return self._is_ready

    def set_params(self, channels, sample_width, sample_rate, nframes_guess):
        self.file.setparams((channels, sample_width, sample_rate, nframes_guess, 'NONE', ''))
        self._is_ready = True

    def write_byte_frames(self, frames):
        self.file.writeframes(frames)

    def stop(self):
        self.file.close()
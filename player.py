import pyaudio
import numpy as np
import matplotlib.pyplot as plt

class Player:
    def __init__(self):
        self.py_audio = pyaudio.PyAudio()
        self.stream = None
        self.chunk_size = None
        self.data = None
        self.sample_rate = 44000
        self.avg = 0
        self.n = 1

    def get_defaults(self):
        defaults = dict()

        defaults['apis'] = []
        for i in range(self.py_audio.get_host_api_count()):
            defaults['apis'].append(self.py_audio.get_host_api_info_by_index(i))

        defaults['devices'] = []
        for i in range(self.py_audio.get_device_count()):
            defaults['devices'].append(self.py_audio.get_device_info_by_index(i))

        defaults['default_api'] = self.py_audio.get_default_host_api_info()['index']
        return defaults

    def start(self, settings, callback):
        print(settings['api'])

        # TODO: format is hardcoded
        in_format = pyaudio.paInt16
        out_format = pyaudio.paInt16

        api = self.py_audio.get_host_api_info_by_index(settings['api']['index'])
        input_device = self.py_audio.get_device_info_by_index(api['defaultInputDevice'])
        output_device = self.py_audio.get_device_info_by_index(api['defaultOutputDevice'])
        in_channels = input_device['maxInputChannels']
        out_channels = output_device['maxOutputChannels']
        sample_rate = int(output_device['defaultSampleRate'])

        is_supported = self.py_audio.is_format_supported(
            sample_rate,
            input_device=input_device['index'],
            input_channels=in_channels,
            input_format=in_format,
            output_device=output_device['index'],
            output_channels=out_channels,
            output_format=out_format
        )
        print("Supported: " + str(is_supported))

        if is_supported:
            def stream_callback(in_data, frame_count, time_info, status):
                self.chunk_size = int(len(in_data) / 2)

                # TODO: format hardcoded
                self.data = np.fromstring(in_data, np.int16)
                self.fft()
                return in_data, pyaudio.paContinue

            # TODO: in == out in a lot of cases
            self.stream = self.py_audio.open(
                format=out_format,
                channels=out_channels,
                rate=sample_rate,
                output=True,
                input=True,
                input_device_index=input_device['index'],
                output_device_index=output_device['index'],
                stream_callback=stream_callback
            )

            self.sample_rate = sample_rate
            self.stream.start_stream()
            callback(True)

        else:
            callback(False)

    def stop(self):
        if self.stream:
            self.chunk_size = None
            self.stream.stop_stream()

    def fft(self):
        if self.chunk_size is None or self.data is None:
            return

        y = np.fft.fft(self.data[0:self.chunk_size])
        diff = int(20 * np.log10(np.sum(np.abs(y / self.chunk_size)**2))) - self.avg
        print(diff)

        self.avg = self.avg + diff / self.n
        self.n += 1

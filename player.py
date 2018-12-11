import threading
import pyaudio
import numpy as np
import audiohelper
import ringbuffer
from wavrecorder import WavRecorder


class Player:
    def __init__(self):
        self.py_audio = pyaudio.PyAudio()
        self.stream = None
        self.recorder = None

        self.sample_rate = 44100
        self.channels = 2
        self.on_frame = None
        self.input2 = None
        self.input_dbs = [None, None]

    def get_defaults(self):
        defaults = dict()

        defaults['apis'] = []
        for api_index in range(self.py_audio.get_host_api_count()):
            host_api = self.py_audio.get_host_api_info_by_index(api_index)
            defaults['apis'].append(host_api)

            host_api['devices'] = []
            for api_device_index in range(host_api['deviceCount']):
                device = self.py_audio.get_device_info_by_host_api_device_index(api_index, api_device_index)

                if device['index'] == host_api['defaultInputDevice']:
                    host_api['defaultInputDeviceHostIndex'] = api_device_index
                if device['index'] == host_api['defaultOutputDevice']:
                    host_api['defaultOutputDeviceHostIndex'] = api_device_index
                device['hostApiIndex'] = api_device_index

                host_api['devices'].append(device)

        defaults['default_api'] = self.py_audio.get_default_host_api_info()['index']
        return defaults

    def start(self, settings, on_frame=None, input2=None):
        if self.stream:
            self.stop()

        # TODO: format is hardcoded
        in_format = pyaudio.paInt16
        out_format = pyaudio.paInt16

        api = settings['api']
        input_device = settings['inputDevice']
        output_device = settings['outputDevice']
        in_channels = settings['inputChannels']
        out_channels = settings['outputChannels']
        sample_rate = settings['sampleRate']

        print("Starting stream:\nAPI: %s\nSampling Rate: %d\nChannels: %d\nInput: (%d) %s\nOutput: (%d) %s\n"
              % (api['name'],
                 sample_rate,
                 in_channels,
                 input_device['index'], input_device['name'],
                 output_device['index'], output_device['name']
                 )
              )

        try:
            is_supported = self.py_audio.is_format_supported(
                sample_rate,
                input_device=input_device['index'],
                input_channels=in_channels,
                input_format=in_format,
                output_device=output_device['index'],
                output_channels=out_channels,
                output_format=out_format
            )
        except:
            is_supported = False

        if not is_supported:
            print("ERROR: Format not supported")
            return False

        self.sample_rate = sample_rate
        self.on_frame = on_frame
        self.input2 = input2
        self.channels = in_channels
        print(type(input2))

        if 'recordFilename' in settings and settings['recordFilename']:
            self.recorder = WavRecorder(settings['recordFilename'])
            # TODO: hardcoded format
            self.recorder.set_params(self.channels, 2, self.sample_rate, 2048)

        # TODO: format is hardcoded
        input_ringbuffer = ringbuffer.RingBuffer(slot_bytes=self.channels * 2 * 2048, slot_count=50)
        output_ringbuffer = ringbuffer.RingBuffer(slot_bytes=self.channels * 2 * 2048, slot_count=50)
        input_ringbuffer.new_writer()
        output_ringbuffer.new_writer()

        output_reader = output_ringbuffer.new_reader()
        input_reader = input_ringbuffer.new_reader()
        t = threading.Thread(target=self.process_frames,
                             args=(
                                 input_ringbuffer,
                                 input_reader,
                                 output_ringbuffer))
        t.daemon = True
        t.start()

        def stream_callback(in_data, frame_count, time_info, status):
            if status == pyaudio.paComplete:
                input_ringbuffer.writer_done()
            else:
                try:
                    input_ringbuffer.try_write(in_data)
                except ringbuffer.WaitingForReaderError:
                    input_ringbuffer.force_reader_sync()
                    print('Processing slow on input')

            try:
                out_data = bytes(output_ringbuffer.try_read(output_reader))
                return out_data, pyaudio.paContinue
            except ringbuffer.WriterFinishedError:
                return [], pyaudio.paComplete
            except ringbuffer.WaitingForWriterError:
                print('Processing slow on output')

            return in_data, pyaudio.paContinue

        self.stream = self.py_audio.open(
            rate=sample_rate,
            channels=in_channels,
            format=out_format,
            input=True,
            output=True,
            input_device_index=input_device['index'],
            output_device_index=output_device['index'],
            frames_per_buffer=2048,
            start=False,
            stream_callback=stream_callback,
        )

        self.stream.start_stream()
        return True

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.recorder:
            self.recorder.stop()
            self.recorder = None

    def process_frames(self, input_ringbuffer, input_reader, output_ringbuffer):
        while True:
            try:
                in_frames = bytes(input_ringbuffer.blocking_read(input_reader))
            except ringbuffer.WriterFinishedError:
                return

            # Convert the input device frame
            input_direct = audiohelper.convert_frame_from_bytes_to_numpy(in_frames, channels=self.channels)
            frame_length = input_direct.shape[1]
            #self.input_dbs[0] = self.db_meter(input_direct)

            # Get input2 frame and mix
            if self.input2 is not None:
                input2 = self.input2(frame_length)
                self.input_dbs[1] = self.db_meter(input_direct)
                buffer = input2
            else:
                buffer = input_direct

            # Execute on_frame callback (e.g. VST plugins)
            if self.on_frame:
                buffer = self.on_frame(buffer)

            # Convert back to bytes and write to output buffer / recorder
            out_frames = audiohelper.convert_frame_from_numpy_to_bytes(buffer)
            if self.recorder:
                self.recorder.write_byte_frames(out_frames)
            try:
                output_ringbuffer.try_write(out_frames)
            except ringbuffer.WaitingForReaderError:
                # This should 'never' happen
                print('Processing overtook the live output!')

    @staticmethod
    def db_meter(frame):
        rms = audiohelper.rms_func(frame)  # TODO hardcoded datatype
        db = 20 * np.log10(rms + np.finfo(np.float32).eps)
        return db

    def is_playing(self):
        return self.stream is not None and self.stream.is_active()

    def __del__(self):
        self.stop()
        self.py_audio.terminate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.py_audio.terminate()

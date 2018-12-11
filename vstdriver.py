from vstplugin import VSTPlugin
import matplotlib.pyplot as pyplot

import numpy

SampleRate = 48000
Samples = 2048 * 100
FreqMax = 20000


class VSTDriver:
    def __init__(self):
        self.plugins = []
        self.inputs = None
        self.outputs = None
        self.frame_pointer = 0
        self.is_internally_driving = False

    def load_plugin(self, plugin_name):
        new_plugin = VSTPlugin(plugin_name)

        new_plugin.open()
        new_plugin.set_sample_rate(SampleRate)
        new_plugin.set_block_size(2048)

        print("#Inputs %d" % new_plugin.get_number_of_inputs())
        print("#Outputs: %d" % new_plugin.get_number_of_outputs())

        if new_plugin.can_process_double():
            numpy_type = numpy.float64
        else:
            print("HELP SINGLE FLOAT")
            numpy_type = numpy.float32

        self.outputs = numpy.zeros((new_plugin.get_number_of_outputs(), Samples), dtype=numpy_type)
        self.plugins.append(new_plugin)

        return new_plugin

    def setup_internal_drive(self):
        self.inputs = numpy.zeros((self.plugins[0].get_number_of_inputs(), Samples))

        t = numpy.arange(Samples) / SampleRate
        self.inputs[0] = numpy.sin(numpy.pi * (SampleRate * 1000 / Samples) * t)
        self.inputs[1] = self.inputs[1].flatten()
        self.is_internally_driving = True

    def drive_internal(self, frame_data, frame_count):
        if self.frame_pointer >= Samples/2048:
            self.plot()

        frame_range = range(self.frame_pointer * 2048, (self.frame_pointer+1) * 2048)
        self.plugins[0].process(
            [self.inputs[0][frame_range], self.inputs[1][frame_range]],
            self.outputs[:, frame_range]
        )
        self.frame_pointer += 1

    def drive(self, frame_data):
        if len(self.plugins) > 0:
            output = numpy.zeros((self.plugins[0].get_number_of_outputs(), 2048), dtype=numpy.float64)
            self.plugins[0].process(
                frame_data,
                output
            )
        else:
            return frame_data

    def plot(self, NFFT=8192, noverlap=1024):
        pyplot.figure()
        a = pyplot.subplot(2, len(self.outputs), 1)
        pyplot.title("Input L")
        pyplot.specgram(self.inputs[0], NFFT=NFFT, Fs=SampleRate, noverlap=noverlap)
        # pyplot.plot(inputs[0])
        if len(self.outputs) > 1:
            a = pyplot.subplot(2, 2, 2)
            pyplot.title("Input R")
            pyplot.specgram(self.inputs[1], NFFT=NFFT, Fs=SampleRate, noverlap=noverlap)
            # pyplot.plot(inputs[1])

        a = pyplot.subplot(2, len(self.outputs), len(self.outputs) + 1)
        pyplot.title("Output L")
        pyplot.specgram(self.outputs[0], NFFT=NFFT, Fs=SampleRate, noverlap=noverlap)
        # pyplot.plot(outputs[0])

        if len(self.outputs) > 1:
            a = pyplot.subplot(2, 2, 4)
            pyplot.title("Output R")
            pyplot.specgram(self.outputs[1], NFFT=NFFT, Fs=SampleRate, noverlap=noverlap)
    # pyplot.plot(outputs[1])

    def resume(self):
        for plugin in self.plugins:
            plugin.resume()

#!/usr/bin/env python
import scipy
import scipy.io
from scipy.io import wavfile
import time
import wave

import matplotlib.pyplot as pyplot
import numpy

import audiohelper
import wavrecorder
import wavplayer

from vstplugin import VSTPlugin

FreqMax = 20000


def raise_gui(plugin):
    import wx

    app = wx.App()
    frame = wx.Frame(None, -1, "Plugin editor")

    plugin.open_edit(frame.GetHandle())
    rect = plugin.get_erect()
    frame.SetClientSize((rect.right, rect.bottom))
    frame.Show()
    app.MainLoop()
    plugin.close_edit()


def display(plugin, input1, input2):
    output = numpy.zeros((plugin.number_of_outputs, player.file.getnframes()), dtype=numpy.float64)

    for i in range(int(player.file.getnframes() / 2048)):
        plugin.process([input1[i * 2048:(i + 1) * 2048], input2[i * 2048:(i + 1) * 2048]],
                       output[:, i * 2048:(i + 1) * 2048])

    return (input1, input2), output


def plot(inputs, outputs, NFFT=8192, noverlap=1024):
    pyplot.figure()
    a = pyplot.subplot(2, len(outputs), 1)
    pyplot.title("Input L")
    pyplot.specgram(inputs[0], NFFT=NFFT, Fs=44100, noverlap=noverlap)
    # pyplot.plot(inputs[0])
    if len(outputs) > 1:
        a = pyplot.subplot(2, 2, 2)
        pyplot.title("Input R")
        pyplot.specgram(inputs[1], NFFT=NFFT, Fs=44100, noverlap=noverlap)
        # pyplot.plot(inputs[1])

    a = pyplot.subplot(2, len(outputs), len(outputs) + 1)
    pyplot.title("Output L")
    pyplot.specgram(outputs[0], NFFT=NFFT, Fs=44100, noverlap=noverlap)
    # pyplot.plot(outputs[0])
    if len(outputs) > 1:
        a = pyplot.subplot(2, 2, 4)
        pyplot.title("Output R")
        pyplot.specgram(outputs[1], NFFT=NFFT, Fs=44100, noverlap=noverlap)
        # pyplot.plot(outputs[1])


player = wavplayer.WavPlayer()
player.load("test.wav")
inputwav = player.get_frames_numpy(player.file.getnframes())
inputwav1 = inputwav[0, :]
inputwav2 = inputwav[1, :]


nframes = player.file.getnframes()
sample_rate = player.file.getframerate()

t = numpy.arange(nframes, dtype=numpy.float64) / sample_rate
inputsin1 = numpy.sin(numpy.pi * (sample_rate * FreqMax / nframes * (t + .1)) * t)
inputsin2 = inputsin1[::-1].flatten()



plugin = VSTPlugin("plugins/Scarlett Gate 64.dll")
plugin.open()
plugin.set_sample_rate(44100)
plugin.set_block_size(2048)

if plugin.has_editor():
    raise_gui(plugin)
plugin.resume()
inputs, outputs = display(plugin, inputwav1, inputwav2)
plugin.suspend()

print(inputwav1.shape)

recorder = wavrecorder.WavRecorder("test_out_vst.wav")
recorder.set_params(2, 2, sample_rate, nframes)

out_frames = audiohelper.convert_frame_from_numpy_to_bytes(outputs)
print(outputs.shape)
recorder.write_byte_frames(out_frames)
recorder.stop()

plot(inputs, outputs)
pyplot.show()


import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os


class WAVPlayerGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.wav_player = None

        wav_frame = ttk.Labelframe(self, text='WAV Player')
        wav_frame.pack(fill=tk.BOTH)

        self.load_button = ttk.Button(wav_frame, text="Load File")
        self.load_button.bind("<Button>", self.open_file)
        self.load_button.grid(row=0, column=0, sticky=tk.W)
        self.file_label = ttk.Label(wav_frame, text="")
        self.start_label = ttk.Label(wav_frame, text="Start:")
        self.start_slider = ttk.Scale(wav_frame, orient=tk.HORIZONTAL, from_=0, to=100, command=self.on_start_changed)
        self.end_label = ttk.Label(wav_frame, text="End:")
        self.end_slider = ttk.Scale(wav_frame, orient=tk.HORIZONTAL, from_=0, to=100, command=self.on_end_changed)

        self.current_label = ttk.Label(wav_frame, text="Current:")
        self.current_slider = ttk.Scale(wav_frame, orient=tk.HORIZONTAL, from_=0, to=100)
        self.current_slider.state(["readonly"])

    def on_start_changed(self, value):
        self.wav_player.set_start(float(value))

    def on_end_changed(self, value):
        self.wav_player.set_end(float(value))

    def show_file_loaded(self):
        duration = self.wav_player.get_duration()

        for slider in [self.start_slider, self.end_slider, self.current_slider]:
            slider.configure(to=duration)

        self.end_slider.set(duration)
        self.file_label.grid(row=0, column=1, sticky=tk.W)
        self.start_label.grid(row=1, column=0, sticky=tk.W)
        self.start_slider.grid(row=1, column=1, sticky=tk.W)
        self.end_label.grid(row=2, column=0, sticky=tk.W)
        self.end_slider.grid(row=2, column=1, sticky=tk.W)
        self.current_label.grid(row=3, column=0, sticky=tk.W)
        self.current_slider.grid(row=3, column=1, sticky=tk.W)

    def connect_wav_player(self, wav_player):
        self.wav_player = wav_player

    def open_file(self, event=None):
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=[("WAV Audio Files", "*.wav")],
            title="Choose a file."
        )
        if filename:
            self.wav_player.load(filename)
            self.file_label['text'] = filename
            self.wav_player.register_on_changed_pos(self.on_player_changed_pos)
            self.show_file_loaded()

    def on_player_changed_pos(self, new_pos):
        self.current_slider.set(new_pos)


class VSTControlGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.load_plugin = None

        vst_frame = ttk.Labelframe(self, text='VST Plugin')
        vst_frame.pack(fill=tk.BOTH)

        self.load_button = ttk.Button(vst_frame, text="Load Plugin")
        self.load_button.bind("<Button>", self.open_file)
        self.load_button.grid(row=0, column=0, sticky=tk.W)
        self.file_label = ttk.Label(vst_frame, text="")

    def set_load_plugin(self, callback):
        self.load_plugin = callback

    def open_file(self, event=None):
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=[("VST plugins", "*.dll")],
            title="Choose a plugin."
        )
        if filename is not None and self.load_plugin():
            self.file_label['text'] = filename
            self.file_label.grid(row=0, column=1, sticky=tk.W)


class MetersGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)


class PlayerControlsGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self._is_playing = False
        self.record_filename = None

        player_controls = ttk.Labelframe(self, text='Player Controls')
        player_controls.pack(fill=tk.BOTH)

        self.record_button = ttk.Button(player_controls, text="Record to File")
        self.record_button.bind("<Button>", self.select_record_file)
        self.record_button.grid(row=0, column=0, sticky=tk.E)
        self.file_label = ttk.Label(player_controls, text="")
        self.file_label.grid(row=0, column=1, sticky=tk.E)

        self.play_button = ttk.Button(player_controls, text="")
        self.play_button.grid(row=1, column=0, sticky=tk.E)
        self.set_playing(False)

    def set_playing(self, is_playing):
        self._is_playing = is_playing

        if is_playing:
            self.play_button['text'] = "Stop"
        else:
            self.play_button['text'] = "Play"

    def is_playing(self):
        return self._is_playing

    def should_record(self):
        return self._should_record

    def get_record_filename(self):
        return self.record_filename

    def select_record_file(self, event=None):
        filename = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            filetypes=[("WAV Audio Files", "*.wav")],
            title="Choose a file."
        )
        if filename:
            self.record_filename = filename
            self.file_label['text'] = filename


class SettingsGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # API selection at the top
        api_frame = ttk.Labelframe(self, text='API')
        api_frame.pack(fill=tk.X)

        self.api_list = ttk.Combobox(api_frame, state="readonly")
        self.api_list.bind('<<ComboboxSelected>>', self.on_changed_api_list)
        self.api_list.pack(fill=tk.BOTH)

        # Input device selection
        input_frame = ttk.Labelframe(self, text='Input')
        input_frame.pack(fill=tk.X)

        self.input_device_list = ttk.Combobox(input_frame, state="readonly")
        self.input_device_list.bind('<<ComboboxSelected>>', self.on_changed_input_device)
        self.input_device_list.grid(row=0, sticky=tk.W)

        ttk.Label(input_frame, text="Channels:").grid(row=1, column=0, sticky=tk.W)
        self.input_channel_list = ttk.Combobox(input_frame, state="readonly")
        self.input_channel_list.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(input_frame, text="Sample Rate:").grid(row=2, column=0, sticky=tk.W)
        self.input_samplerate_list = ttk.Entry(input_frame)
        self.input_samplerate_list.grid(row=2, column=1, sticky=tk.W)

        ttk.Label(input_frame, text="Format:").grid(row=3, column=0, sticky=tk.W)
        self.input_format_list = ttk.Combobox(input_frame, state="readonly")
        self.input_format_list.grid(row=3, column=1, sticky=tk.W)

        # Output device selection
        output_frame = ttk.Labelframe(self, text='Output')
        output_frame.pack(fill=tk.X)

        self.output_device_list = ttk.Combobox(output_frame, state="readonly")
        self.output_device_list.bind('<<ComboboxSelected>>', self.on_changed_output_device)
        self.output_device_list.grid(row=0, sticky=tk.W)

        ttk.Label(output_frame, text="Channels:").grid(row=1, column=0, sticky=tk.W)
        self.output_channel_list = ttk.Combobox(output_frame, state="readonly")
        self.output_channel_list.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(output_frame, text="Sample Rate:").grid(row=2, column=0, sticky=tk.W)
        self.output_samplerate_list = ttk.Entry(output_frame)
        self.output_samplerate_list.grid(row=2, column=1, sticky=tk.W)

        ttk.Label(output_frame, text="Format:").grid(row=3, column=0, sticky=tk.W)
        self.output_format_list = ttk.Combobox(output_frame, state="readonly")
        self.output_format_list.grid(row=3, column=1, sticky=tk.W)

    def load_defaults(self, defaults):
        self.defaults = defaults

        api_names = [api['name'] for api in defaults['apis']]
        self.api_list['values'] = api_names
        self.api_list.current(defaults['default_api'])
        self.on_changed_api_list()

    def get_settings(self):
        settings = dict()

        api_index = self.api_list.current()
        api = self.defaults['apis'][api_index]
        input_device = [d for d in api['devices'] if d['name'] == self.input_device_list.get()]
        output_device = [d for d in api['devices'] if d['name'] == self.output_device_list.get()]

        settings['api'] = api
        if len(input_device) > 0:
            settings['inputDevice'] = input_device[0]
            settings['inputChannels'] = int(self.input_channel_list.get())
            settings['sampleRate'] = int(self.input_samplerate_list.get())

        if len(output_device) > 0:
            settings['outputDevice'] = output_device[0]
            settings['outputChannels'] = int(self.output_channel_list.get())

        return settings

    def on_changed_api_list(self, event=None):
        new_index = self.api_list.current()
        api = self.defaults['apis'][new_index]
        devices_for_api = api['devices']

        input_devices = [d for d in devices_for_api if d['maxInputChannels'] > 0]
        self.input_device_list.set('')
        self.input_device_list['values'] = [d['name'] for d in input_devices]
        if 'defaultInputDevice' in api:
            for index, device in enumerate(input_devices):
                if device['index'] == api['defaultInputDevice']:
                    self.input_device_list.current(index)
                    break
        self.on_changed_input_device()

        output_devices = [d for d in devices_for_api if d['maxOutputChannels'] > 0]
        self.output_device_list.set('')
        self.output_device_list['values'] = [d['name'] for d in output_devices]
        if 'defaultOutputDevice' in api:
            for index, device in enumerate(output_devices):
                if device['index'] == api['defaultOutputDevice']:
                    self.output_device_list.current(index)
                    break
        self.on_changed_output_device()

    def on_changed_input_device(self, event=None):
        api_index = self.api_list.current()
        api = self.defaults['apis'][api_index]

        input_device = [d for d in api['devices'] if d['name'] == self.input_device_list.get()]
        self.input_samplerate_list.delete(0, tk.END)
        self.input_channel_list.set('')
        if len(input_device) > 0:
            input_device = input_device[0]
            self.input_channel_list['values'] = list(range(0, input_device['maxInputChannels'] + 1))
            self.input_channel_list.current(input_device['maxInputChannels'])
            self.input_samplerate_list.delete(0, tk.END)
            self.input_samplerate_list.insert(0, int(input_device['defaultSampleRate']))

    def on_changed_output_device(self, event=None):
        api_index = self.api_list.current()
        api = self.defaults['apis'][api_index]

        output_device = [d for d in api['devices'] if d['name'] == self.output_device_list.get()]
        self.output_samplerate_list.delete(0, tk.END)
        self.output_channel_list.set('')
        if len(output_device) > 0:
            output_device = output_device[0]
            self.output_channel_list['values'] = list(range(0, output_device['maxOutputChannels'] + 1))
            self.output_channel_list.current(output_device['maxOutputChannels'])
            self.output_samplerate_list.insert(tk.END, int(output_device['defaultSampleRate']))


class VSTWindow:
    def __init__(self, parent, plugin):
        self.window = tk.Toplevel(parent)
        self.window.title(plugin.get_name())
        rect = plugin.get_erect()
        plugin.open_edit(self.window.winfo_id())
        self.window.minsize(rect.right, rect.bottom)
        self.window.maxsize(rect.right, rect.bottom)


class MainGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        parent.title("Audio Project")
        parent.minsize(400, 400)

        self.settings_panel = SettingsGUI(self)
        self.wav_player = WAVPlayerGUI(self)
        self.player_controls = PlayerControlsGUI(self)

        self.settings_panel.pack(fill=tk.X, padx=10, pady=10)
        self.wav_player.pack(fill=tk.X, padx=10, pady=10)
        self.player_controls.pack(fill=tk.X, padx=10, pady=10)


def init_gui(tk_root):
    main_view = MainGUI(tk_root)
    main_view.pack(side="top", fill="both", expand=True)
    return main_view


# class Plotter:
#     def __init__(self, parent, player):
#         self.window = tk.Toplevel(parent)
#         self.figure = plt.figure()
#         self.player = player
#         self.animation = None
#
#         self.x = []
#         self.y = []
#
#         self.ax = self.figure.add_subplot(1, 1, 1)
#         self.ax.set_title('dB Meter')
#         self.ax.set_ylabel('dB')
#         plt.xticks(rotation=25, ha='right')
#         plt.yticks([0, -10, -20, -30, -40, -50])
#
#         canvas = FigureCanvasTkAgg(self.figure, master=self.window)
#         canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
#         canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
#
#         plt.show()
#
#     def animate(self, i):
#         print("hi")
#         self.x.append(str(i))
#         self.y.append(self.player.input_dbs[1])
#
#         self.x = self.x[-15:]
#         self.y = self.y[-15:]
#
#         self.ax.clear()
#         self.ax.plot(self.x, self.y)
#
#     def stop(self):
#         if self.animation:
#             self.animation = None
#         self.window.destroy()
#
#     def start(self):
#         self.animation = animation.FuncAnimation(self.figure, self.animate, interval=100)

class Plotter:
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    y_axis = [0, -10, -20, -30, -40, -50]

    def __init__(self, indata):
        self.x = []
        self.y = []
        self.streamdata = indata

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def animate(self, i, x, y):
        print("HI")
        self.x.append(str(i))
        self.y.append(self.streamdata.input_dbs[0])

        self.x = self.x[-15:]
        self.y = self.y[-15:]

        self.ax.clear()
        self.ax.plot(self.x, self.y)

        plt.xticks(rotation=25, ha='right')
        plt.yticks(self.y_axis)
        plt.subplots_adjust(bottom=0.30)
        plt.title('dB Meter')
        plt.ylabel('dB')

    def stop(self):
        return

    def start(self):
        ani = animation.FuncAnimation(self.fig, self.animate, fargs=(self.get_x(), self.get_y()), interval=100)
        plt.show()
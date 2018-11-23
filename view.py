import tkinter as tk
from tkinter import ttk


class PlayerControlsGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        col_idx = 0
        self._is_recording = False
        self.record_button = ttk.Button(self, text="")
        self.record_button.grid(row=0, column=col_idx, sticky=tk.E)
        self.set_recoding(False)

        col_idx += 1
        self._is_playing = False
        self.play_button = ttk.Button(self, text="")
        self.play_button.grid(row=0, column=col_idx, sticky=tk.E)
        self.set_playing(False)

    def set_playing(self, is_playing):
        self._is_playing = is_playing

        if is_playing:
            self.play_button['text'] = "Stop"
        else:
            self.play_button['text'] = "Start"

    def set_recoding(self, is_recording):
        self._is_recording = is_recording

        if not is_recording:
            self.record_button['text'] = "Record"
        else:
            self.record_button['text'] = "Stop Recoding"

    def is_recoding(self):
        return self._is_recording

    def is_playing(self):
        return self._is_playing


class SettingsGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        row_idx = 0

        self.apis_var = tk.StringVar()
        self.api_label = ttk.Label(self, text="API")
        self.api_label.grid(row=row_idx, column=0, sticky=tk.W)
        self.api_list = ttk.Combobox(self, textvariable=self.apis_var, state="readonly")
        self.api_list.bind('<<ComboboxSelected>>', self.on_changed_api_list)
        self.api_list.grid(row=row_idx, column=1, sticky=tk.W)

        row_idx += 1
        self.input_label = ttk.Label(self, text="Input")
        self.input_label.grid(row=row_idx, column=0, sticky=tk.W)
        self.input = ttk.Label(self, text="")
        self.input.grid(row=row_idx, column=1, sticky=tk.W)

        row_idx += 1
        self.output_label = ttk.Label(self, text="Output")
        self.output_label.grid(row=row_idx, column=0, sticky=tk.W)
        self.output = ttk.Label(self, text="")
        self.output.grid(row=row_idx, column=1, sticky=tk.W)

        row_idx += 1
        self.channel_label = ttk.Label(self, text="Channels")
        self.channel_label.grid(row=row_idx, column=0, sticky=tk.W)
        self.channel = ttk.Label(self, text="")
        self.channel.grid(row=row_idx, column=1, sticky=tk.W)

        row_idx += 1
        self.samplerate_label = ttk.Label(self, text="Sample Rate")
        self.samplerate_label.grid(row=row_idx, column=0, sticky=tk.W)
        self.samplerate = ttk.Label(self, text="kHz")
        self.samplerate.grid(row=row_idx, column=1, sticky=tk.W)

        row_idx += 1
        self.format_label = ttk.Label(self, text="Format")
        self.format_label.grid(row=row_idx, column=0, sticky=tk.W)
        self.format = ttk.Label(self, text="")
        self.format.grid(row=row_idx, column=1, sticky=tk.W)
        
    def load_defaults(self, defaults):
        self.defaults = defaults

        api_names = [api['name'] for api in defaults['apis']]
        self.api_list['values'] = api_names
        self.api_list.current(defaults['default_api'])
        self.on_changed_api_list()

    def get_settings(self):
        settings = dict()

        api_index = self.api_list.current()
        settings['api'] = self.defaults['apis'][api_index]
        return settings

    def on_changed_api_list(self, event=None):
        new_index = self.api_list.current()
        api = self.defaults['apis'][new_index]

        device_count = len(self.defaults['devices'])
        if api['defaultInputDevice'] >= 0 or api['defaultInputDevice'] < device_count:
            input_device = self.defaults['devices'][api['defaultInputDevice']]
            self.input['text'] = input_device['name']
        else:
            self.input['text'] = ""

        if api['defaultOutputDevice'] >= 0 or api['defaultOutputDevice'] < device_count:
            output_device = self.defaults['devices'][api['defaultOutputDevice']]
            self.output['text'] = output_device['name']
            self.channel['text'] = output_device['maxOutputChannels']
            self.samplerate['text'] = str(int(output_device['defaultSampleRate'])) + " Hz"
        else:
            self.output['text'] = ""
            self.channel['text'] = ""
            self.samplerate['text'] = ""


class MainGUI(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        parent.title("Audio Project")
        self.settings_panel = SettingsGUI(self)
        self.player_controls = PlayerControlsGUI(self)

        self.settings_panel.grid(row=0)
        self.player_controls.grid(row=1)


def init_gui(tk_root):
    main_view = MainGUI(tk_root)
    main_view.pack(side="top", fill="both", expand=True)
    return main_view

import view
import player
from tkinter import Tk

from vstdriver import VSTDriver
from wavplayer import WavPlayer


class MainController:
    def __init__(self):
        self.player = player.Player()
        self.vst = VSTDriver()
        self.wav_player = WavPlayer()

        self.tk_root = Tk()
        self.tk_root.protocol("WM_DELETE_WINDOW", exit)
        self.main_view = view.init_gui(self.tk_root)

        self.main_view.player_controls.play_button.bind("<Button>", self.on_pressed_play)
        self.main_view.wav_player.connect_wav_player(self.wav_player)
        self.main_view.vst_control.set_load_plugin(self.load_plugin)

    def run(self):
        self.load_defaults()
        self.tk_root.mainloop()

    def load_defaults(self):
        self.main_view.settings_panel.load_defaults(self.player.get_defaults())

    def on_pressed_play(self, event):
        if self.player.is_playing():
            self.main_view.player_controls.set_playing(False)
            self.player.stop()
            return

        settings = self.main_view.settings_panel.get_settings()

        if self.wav_player.is_ready():
            input2 = self.wav_player.get_frames_numpy
        else:
            input2 = None

        record_filename = self.main_view.player_controls.get_record_filename()
        if record_filename:
            settings['recordFilename'] = record_filename

        self.vst.resume()
        has_started = self.player.start(settings,
                          on_frame=self.vst.drive,
                          input2=input2)

        if has_started:
            self.main_view.player_controls.set_playing(True)
            #view.Plotter.run(self.tk_root, self.player)

    def load_plugin(self, name):
        new_plugin = self.vst.load_plugin(name)

        if new_plugin is None:
            return False

        if new_plugin.has_editor():
            self.vst_window = view.VSTWindow(self.main_view, plugin=new_plugin)

        return True


if __name__ == '__main__':
    c = MainController()
    c.run()

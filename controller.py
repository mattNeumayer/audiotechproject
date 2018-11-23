import view
import player
from tkinter import Tk


class MainController:
    def __init__(self):
        self.player = player.Player()

        self.tk_root = Tk()
        self.main_view = view.init_gui(self.tk_root)
        self.main_view.player_controls.play_button.bind("<Button>", self.on_pressed_play)

    def run(self):
        self.load_defaults()
        self.tk_root.mainloop()

    def load_defaults(self):
        self.main_view.settings_panel.load_defaults(self.player.get_defaults())

    def on_started_playing(self, started_playing):
        if started_playing:
            print("STARTED PLAYING")
            self.main_view.player_controls.set_playing(True)
        else:
            print("ERROR")
            self.main_view.player_controls.set_playing(False)

    def on_pressed_play(self, event):
        if not self.main_view.player_controls.is_playing():
            self.main_view.player_controls.set_playing(True)
            settings = self.main_view.settings_panel.get_settings()
            self.player.start(settings, self.on_started_playing)
        else:
            self.main_view.player_controls.set_playing(False)
            self.player.stop()


if __name__ == '__main__':
    c = MainController()
    c.run()

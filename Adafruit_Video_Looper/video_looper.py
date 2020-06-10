# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt

import configparser
import importlib
import os
import re
import subprocess
import sys
import signal
import time
import pygame
import threading
from inputs import get_gamepad


from .alsa_config import parse_hw_device
from .model import Playlist, Movie
from .playlist_builders import build_playlist_m3u


# Basic video looper architecure:
#
# - VideoLooper class contains all the main logic for running the looper program.
#
# - Almost all state is configured in a .ini config file which is required for
#   loading and using the VideoLooper class.
#
# - VideoLooper has loose coupling with file reader and video player classes that
#   are used to find movie files and play videos respectively.  The configuration
#   defines which file reader and video player module will be loaded.
#
# - A file reader module needs to define at top level create_file_reader function
#   that takes as a parameter a ConfigParser config object.  The function should
#   return an instance of a file reader class.  See usb_drive.py and directory.py
#   for the two provided file readers and their public interface.
#
# - Similarly a video player modules needs to define a top level create_player
#   function that takes in configuration.  See omxplayer.py and hello_video.py
#   for the two provided video players and their public interface.
#
# - Future file readers and video players can be provided and referenced in the
#   config to extend the video player use to read from different file sources
#   or use different video players.
class VideoLooper:

    def __init__(self, config_path):
        """Create an instance of the main video looper application class. Must
        pass path to a valid video looper ini configuration file.
        """
        # Load the configuration.
        self._config = configparser.ConfigParser()
        if len(self._config.read(config_path)) == 0:
            raise RuntimeError('Failed to find configuration file at {0}, is the application properly installed?'.format(config_path))
        self._console_output = self._config.getboolean('video_looper', 'console_output')
        # Load other configuration values.
        self._osd = self._config.getboolean('video_looper', 'osd')
        self._is_random = self._config.getboolean('video_looper', 'is_random')
        self._keyboard_control = self._config.getboolean('video_looper', 'keyboard_control')
        # Get seconds for countdown from config
        self._countdown_time = self._config.getint('video_looper', 'countdown_time')
        # Get seconds for waittime bewteen files from config
        self._wait_time = self._config.getint('video_looper', 'wait_time')
        # Parse string of 3 comma separated values like "255, 255, 255" into
        # list of ints for colors.
        self._bgcolor = list(map(int, self._config.get('video_looper', 'bgcolor')
                                             .translate(str.maketrans('','', ','))
                                             .split()))
        self._fgcolor = list(map(int, self._config.get('video_looper', 'fgcolor')
                                             .translate(str.maketrans('','', ','))
                                             .split()))
        # Initialize pygame and display a blank screen.
        pygame.joystick.init()


        # Load configured video player and file reader modules.
        self._player = self._load_player()
        # Load ALSA hardware configuration.
        self._alsa_hw_device = parse_hw_device(self._config.get('alsa', 'hw_device'))
        self._alsa_hw_vol_control = self._config.get('alsa', 'hw_vol_control')
        self._alsa_hw_vol_file = self._config.get('alsa', 'hw_vol_file')
        # default ALSA hardware volume (volume will not be changed)
        self._alsa_hw_vol = None
        # Load sound volume file name value
        self._sound_vol_file = self._config.get('omxplayer', 'sound_vol_file')
        # default value to 0 millibels (omxplayer)
        self._sound_vol = 0
        # Set other static internal state.
        self._running    = True
        self._playbackStopped = False
        #used for not waiting the first time
        self._firstStart = True

        # start keyboard handler thread:
        # Event handling for key press, if keyboard control is enabled
        if self._keyboard_control:
            self._keyboard_thread = threading.Thread(target=self._handle_keyboard_shortcuts, daemon=True)
            self._keyboard_thread.start()

    def _print(self, message):
        """Print message to standard output if console output is enabled."""
        if self._console_output:
            print(message)

    def _load_player(self):
        """Load the configured video player and return an instance of it."""
        module = self._config.get('video_looper', 'video_player')
        return importlib.import_module('.' + module, 'Adafruit_Video_Looper').create_player(self._config)

    def _is_number(self, s):
        try:
            float(s) 
            return True
        except ValueError:
            return False

    def _blank_screen(self):
        return

    def _render_text(self, message, font=None):
        return

    def _animate_countdown(self, playlist):
        return

    def _idle_message(self):
        return

    def display_message(self,message):
        return


    def _prepare_to_run_playlist(self, playlist):
        return

    def _set_hardware_volume(self):
        if self._alsa_hw_vol != None:
            msg = 'setting hardware volume (device: {}, control: {}, value: {})'
            self._print(msg.format(
                self._alsa_hw_device,
                self._alsa_hw_vol_control,
                self._alsa_hw_vol
            ))
            cmd = ['amixer', '-M']
            if self._alsa_hw_device != None:
                cmd.extend(('-c', str(self._alsa_hw_device[0])))
            cmd.extend(('set', self._alsa_hw_vol_control, '--', self._alsa_hw_vol))
            subprocess.check_call(cmd)
            
    def _handle_keyboard_shortcuts(self):
        while self._running:
            events = get_gamepad()
            for event in events:
                if event.ev_type == 'Key' and event.state:
                    self._player.play(Movie(self._config.get('directory', 'path') + '/' + event.code + '.mp4'))
                    # BTN_TRIGGER
                    # BTN_THUMB
                    # BTN_THUMB2
                    # BTN_TOP
                    # BTN_TOP2
                    # BTN_PINKIE



    def run(self):
        os.system('clear')  # For Linux/OS X

        """Main program loop.  Will never return!"""
        # Main loop to play videos in the playlist and listen for file changes.
        self._player.play(Movie(self._config.get('directory', 'path') + '/loop.mp4'), True, vol = self._sound_vol)

        while self._running:
            # Load and play a new movie if nothing is playing.
            if not self._player.is_playing() and not self._playbackStopped:
                self._player.play(Movie(self._config.get('directory', 'path') + '/loop.mp4'), True, vol = self._sound_vol)

            # Give the CPU some time to do other tasks. low values increase "responsiveness to changes" and reduce the pause between files
            # but increase CPU usage
            # since keyboard commands are handled in a seperate thread this sleeptime mostly influences the pause between files

            time.sleep(0.002)

    def quit(self):
        """Shut down the program"""
        self._print("quitting Video Looper")
        self._running = False
        if self._player is not None:
            self._player.stop()
        pygame.quit()



    def signal_quit(self, signal, frame):
        """Shut down the program, meant to by called by signal handler."""
        self._print("received signal to quit")
        self.quit()

# Main entry point.
if __name__ == '__main__':
    print('Starting Adafruit Video Looper.')
    # Default config path to /boot.
    config_path = '/boot/video_looper.ini'
    # Override config path if provided as parameter.
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    # Create video looper.
    videolooper = VideoLooper(config_path)
    # Configure signal handlers to quit on TERM or INT signal.
    signal.signal(signal.SIGTERM, videolooper.signal_quit)
    signal.signal(signal.SIGINT, videolooper.signal_quit)
    # Run the main loop.
    videolooper.run()

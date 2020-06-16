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
import threading
from inputs import get_gamepad
from gpiozero import LED



from .model import Playlist, Movie


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
        self._running = True

        # Load configured video player and file reader modules.
        self._player = self._load_player()

        # Init LEDs
        self.init_leds()

        # Set up USB button control
        self._keyboard_thread = threading.Thread(target=self._handle_keyboard_shortcuts, daemon=True)
        self._keyboard_thread.start()

    def _print(self, message):
        """Print message to standard output if console output is enabled."""
        if self._console_output:
            print(message)

    def _load_player(self):
        """Load the configured video player and return an instance of it."""
        module = self._config.get('video_looper', 'video_player')
        return importlib.import_module('.' + module, 'Oxys_Video_Looper').create_player(self._config)

    def _is_number(self, s):
        try:
            float(s) 
            return True
        except ValueError:
            return False

    def _handle_keyboard_shortcuts(self):
        while self._running:
            events = get_gamepad()
            for event in events:
                if event.ev_type == 'Key' and event.state:
                    self._player.play(Movie( event.code + '.mp4'))
                    print(event.code)
                    # BTN_TRIGGER
                    # BTN_THUMB
                    # BTN_THUMB2
                    # BTN_TOP
                    # BTN_TOP2
                    # BTN_PINKIE

    def run(self):

        """Main program loop.  Will never return!"""
        # Main loop to play videos in the playlist and listen for file changes.

        while self._running:
            # Just wait for inputs

            # Give the CPU some time to do other tasks. low values increase "responsiveness to changes" and reduce the pause between files
            # but increase CPU usage
            # since keyboard commands are handled in a seperate thread this sleeptime mostly influences the pause between files
            if self.led_state != self._player.playing_file:
                if self._player.playing_file == 'LOOP':
                    self.reset_leds()
                else:
                    self.single_led(self._player.playing_file)

            time.sleep(0.5)

    def init_leds(self):
        """Shut down the program"""
        self.leds = {
            'BTN_TRIGGER': LED(13),
            'BTN_THUMB': LED(16),
            'BTN_THUMB2': LED(19),
            'BTN_TOP': LED(20),
            'BTN_TRIGGER': LED(21),
            'BTN_PINKIE': LED(26)
        }
        self.reset_leds()

    def reset_leds(self):
        self.led_state = 'LOOP'
        for key in self.leds:
            self.leds[key].on()

    def single_led(self, led):
        self.led_state = led
        for key in self.leds:
            if led == key:
                self.leds[key].on()
            else:
                self.leds[key].off()

    def quit(self):
        """Shut down the program"""
        self._print("quitting Video Looper")
        self._running = False
        if self._player is not None:
            self._player.stop()


    def signal_quit(self, signal, frame):
        """Shut down the program, meant to by called by signal handler."""
        self._print("received signal to quit")
        self.quit()

# Main entry point.
if __name__ == '__main__':
    print('Starting Oxys Video Looper.')
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

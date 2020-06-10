# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os
import subprocess
import time
from .vlcclient import VLCClient

class VlcPlayer:

    def __init__(self, config):
        """Connect to VLC telnet instance run by supervisord
        """

        self._vlc = VLCClient('localhost')
        self._vlc.connect()
        self._vlc.loop()

    def play(self, movie, loop=False, **kwargs):
        """Play the provided movied file, optionally looping it repeatedly."""
        self._vlc.enqueue(movie.filename)
        self._vlc.next()
        self._vlc.play()


    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        return True

    def stop(self):
        self._vlc.stop()

    @staticmethod
    def can_loop_count():
        return True


def create_player(config):
    """Create new video player based on hello_video."""
    return VlcPlayer(config)

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
        self.config=config
        self._vlc = VLCClient('localhost')
        time.sleep(2)
        self._vlc.connect()
        time.sleep(2)
        self._vlc.clear()
        self._vlc.enqueue(config.get('directory', 'path') + '/' + config.get('video_looper', 'loop'))
        self._vlc.play()
        self._vlc.loop()
        self.loop_index = self._vlc.search(config.get('video_looper', 'loop'))
        print("Loop index" + self.loop_index)

    def play(self, movie, **kwargs):
        """Play the provided movied file, if we are in the loop"""
        playing_index=self._vlc.playing_index()
        print("PLAY! Now paying " + playing_index)
        if playing_index == self.loop_index:
            self._vlc.add(self.config.get('directory', 'path') + '/' + movie.filename)
            index=self._vlc.search(movie.filename)
            print("New index " + index)
            playing_index=index
            while playing_index==index:
                time.sleep(2)
                playing_index=self._vlc.playing_index()

            print("Delete index " + index)
            self._vlc.delete(index)

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

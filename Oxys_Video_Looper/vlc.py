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
        self.loop_index = None
        self.ensure_loop()
        self._vlc.play()
        self._vlc.loop()
        self.playing_index = self.loop_index
        self.playing_file='LOOP'
        print("Loop index" + self.loop_index)

    def play(self, movie, **kwargs):
        """Play the provided movied file, if we are in the loop"""
        self.playing_index=self._vlc.playing_index()
        print("PLAY! Now paying " + self.playing_index)
        if self.playing_index == self.loop_index:
            self._vlc.add(self.config.get('directory', 'path') + '/' + movie.filename  + '.mp4')
            self.ensure_loop()
            index=self._vlc.search(movie.filename)
            print("New index " + index)
            self.playing_index=index
            self.playing_file=movie.filename
            while self.playing_index==index:
                time.sleep(2)
                self.playing_index=self._vlc.playing_index()

            self.playing_file='LOOP'
            print("Delete index " + index)
            self._vlc.delete(index)

    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        return True

    def stop(self):
        self._vlc.stop()

    def ensure_loop(self):
        has_loop=self._vlc.search(self.config.get('video_looper', 'loop'))
        # Make sure we have the loop after this
        if not has_loop:
            print('No loop exists')
            self._vlc.enqueue(self.config.get('directory', 'path') + '/' + self.config.get('video_looper', 'loop'))
            self.loop_index = self._vlc.search(self.config.get('video_looper', 'loop'))
        else:
            print('Loop exists at:' + has_loop)

    @staticmethod
    def can_loop_count():
        return True


def create_player(config):
    """Create new video player based on hello_video."""
    return VlcPlayer(config)

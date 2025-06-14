"""
This code or file is pertinent to the 'DeepCore' Project
Copyright (c) 2024-2025, 'Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.

@author : Aymen Brahim Djelloul
date : 03.08.2024
version : 0.1
License : MIT


"""

# IMPORTS
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent
from PyQt5.Qt import QUrl
from .const import *
import sys


class SoundEngine:

    def __init__(self, volume: int = 100):

        # initialize basic parameters
        self._volume = volume

        # Create Media Player object
        self._media_player = QMediaPlayer()

    def play_move_sound(self):
        """ This method will play the piece move sound"""

        # Set the media content
        content = QMediaContent(QUrl.fromLocalFile(MOVE_SOUND))
        # Set media and play it
        self._media_player.setMedia(content)
        self._media_player.play()

    def play_capture_sound(self):
        """ This method will play the piece capture sound"""

        # Set the media content
        content = QMediaContent(QUrl.fromLocalFile(CAPTURE_SOUND))
        self._media_player.setMedia(content)
        self._media_player.play()

    def set_mute(self):
        """ This method will mute the sound"""
        self._media_player.setMuted(True)

    def set_unmute(self):
        """ This method will unmute the sound"""
        self._media_player.setMuted(False)


if __name__ == "__main__":
    sys.exit(0)

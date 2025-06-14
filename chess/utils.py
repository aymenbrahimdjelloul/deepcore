"""
@author : Aymen Brahim DJelloul
version : 0.1
license : MIT
date : 24.05.2025


    \\ This file contain utilities functions for
     chess such as : .pgn and .chess files import and export and more

"""

# IMPORTS
import sys
import os
import configparser
from dataclasses import dataclass


@dataclass
class Const:
    pass


# class License(Const):
#
#     def __init__(self) -> None:
#         super().__init__()
#
#
#     def is_licensed(self) -> bool:
#         """ This method will check if the software is licensed or not"""
#
#     def is_valid_key(self, key: str) -> bool:
#         """ This method will check if the key is valid"""
#
#     def license_it(self) -> None:
#         """ This method will license this software"""


class Settings(Const):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def load_settings(cls) -> dict:
        """ This method will load stored settings for ini file"""

    @classmethod
    def save_settings(cls) -> dict:
        """ This method will save settings for ini file"""

    def _load_default_settings(self) -> dict:
        """ This method will load default settings"""


class PgnFile:

    @classmethod
    def file_import(cls, filepath: str) -> dict[str, str]:
        """ This method will import game in PGN format"""

    @classmethod
    def file_export(cls, filepath: str) -> None:
        """ This method will export game in PGN format"""


class ChessFile:

    @classmethod
    def file_import(cls, filepath: str) -> dict[str, str]:
        """ This method will import game in .chess format"""

    @classmethod
    def file_export(self, filepath: str) -> None:
        """ This method will export game in .chess format"""


if __name__ == '__main__':
    sys.exit(0)

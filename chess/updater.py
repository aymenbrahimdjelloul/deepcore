"""
@author : Aymen Brahim Djelloul
version : 0.1
date : 22.05.2025
license : MIT

"""

# IMPORTS
import sys
import os
import re
import requests
import socket
from .const import VERSION



class Updater:

    def __init__(self) -> None:
        pass

    def _is_connected(self) -> bool:
        """ This method will check for internet connection."""

    @classmethod
    def is_new_update(cls) -> dict[str, str] | bool:
        """ This method will check if there is a new update by checking the latest version
         tag in 'DeepCore' GitHub repository and compare it with current version"""
        return False

    def _download_update(self) -> None:
        """ This method will download the latest version of DeepCore"""

    def _install_update(self) -> None:
        """ This method will download the latest version of DeepCore"""

    def _finish_update(self) -> None:
        """ This method will finish the installed update"""

    def update(self) -> None:
        """ This method will update DeepCore"""


if __name__ == '__main__':
    sys.exit(0)

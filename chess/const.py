"""
This code or file is pertinent to the 'DeepCore' Project
Copyright (c) 2024-2025, 'Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.

@author : Aymen Brahim Djelloul
version : 0.1
date    : 21.05.2025
license : MIT License


"""

# IMPORTS
import sys
import configparser
from time import perf_counter
from pathlib import Path

try:
    from PyQt5.QtGui import QColor

except ImportError:
    QColor = None

# DEFINE START TIME OF EXECUTION
S_TIME: float = perf_counter()

# DEFINE GLOBAL VARIABLES
AUTHOR: str = "Aymen Brahim Djelloul"
VERSION: str = "0.1"
BUILD_DATE: str = "31.07.2024"

# DEFINE App variables
WIDTH: int = 600
HEIGHT: int = 600
BOARD_SIZE: int = 8
SQSize: int = min(WIDTH, HEIGHT) // BOARD_SIZE

# DEFINE GEOMETRY VARIABLES
OFFSET_X: int = (WIDTH - BOARD_SIZE * SQSize) // 2
OFFSET_Y: int = (HEIGHT - BOARD_SIZE * SQSize) // 2

# DEFINE ROOK MOVE DIRECTIONS
ROOK_DIRECTIONS: list = [(1, 0), (6, 0), (1, 7), (6, 7)]

# DEFINE RGB COLORS
SELECTED_COLOR: tuple = (206, 206, 206)
MOVES_COLOR: tuple = (254, 240, 118)
CHECKMATE_COLOR: tuple = (230, 90, 90)

# DEFINE BOARD THEMES
GREEN_COLOR: tuple = (118, 150, 86)
WHITE_COLOR: tuple = (238, 238, 210)

APP_ICON = Path("assets/images/icons/icon.png")

# Define urls
DEEP_CORE_REPO: str = "https://github.com/aymenbrahimdjelloul/deepcore"
DEEP_CORE_WEBSITE: str = "https://aymenbrahimdjelloul.github.io/deepcore/"
DONATE_URL: str = "https://www.deepcore.com/donate"
AUTHOR_MAIL: str = "brahimdjelloulaymen@gmail.com"

# DEFINE
WHITE_PAWN: str = "♙"
WHITE_BISHOP: str = "♗"
WHITE_ROOK: str = "♖"
WHITE_KNIGHT: str = "♘"
WHITE_QUEEN: str = "♕"
WHITE_KING: str = "♔"

BLACK_PAWN: str = "♟"
BLACK_BISHOP: str = "♝"
BLACK_ROOK: str = "♜"
BLACK_KNIGHT: str = "♞"
BLACK_QUEEN: str = "♛"
BLACK_KING: str = "♚"

# DEFINE SOUNDS FILES
MOVE_SOUND: str = "assets/sounds/move.wav"
CAPTURE_SOUND: str = "assets/sounds/capture.wav"

# DEFINE SETTINGS
SETTINGS: configparser.ConfigParser = configparser.ConfigParser()
SETTINGS = SETTINGS.read('settings.ini')

# Enhanced colors for a professional look
DARK_SQUARE = QColor(181, 136, 99)  # Warm brown for dark squares
LIGHT_SQUARE = QColor(240, 217, 181)  # Light beige for light squares
HIGHLIGHT_COLOR = QColor(106, 168, 79, 180)  # Green highlight for pieces
MOVE_COLOR = QColor(106, 168, 79, 120)  # Lighter green for possible moves
BACKGROUND_COLOR = QColor(42, 39, 37)  # Dark charcoal background
PANEL_COLOR = QColor(55, 52, 50)  # Panel background

# Button style for a modern look
BUTTON_STYLE: str = """
    QPushButton {
        background-color: #3c3836;
        color: #ebdbb2;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #504945;
    }
    QPushButton:pressed {
        background-color: #665c54;
    }
"""

# Define the HTML content for the main text
ABOUT_TEXT: str = f"""
<h2>DeepCore Chess</h2>
<p><b>Version {VERSION}</b></p>
<p>A feature-rich chess application with customizable interface, 
AI opponents, and game analysis tools.</p>
<p>Created by <a href='mailto:{AUTHOR_MAIL}'>{AUTHOR}</a></p>
<p><small>© 2024 All rights reserved.</small></p>
"""

LINKS_TEXT: str = f"<p><a href='{DEEP_CORE_WEBSITE}'>Visit website</a> | <a href='{DEEP_CORE_REPO}'>GitHub</a></p>"

if __name__ == "__main__":
    sys.exit(0)

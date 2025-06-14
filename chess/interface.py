#!/usr/bin/env python3

"""
This code or file is pertinent to the 'DeepCore' Project
Copyright (c) 2024-2025, 'Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.

@author : Aymen Brahim Djelloul
version : 0.1
date : 22.05.2025
license : MIT

"""

# IMPORTS
from .const import *
from .game import *
from .updater import Updater
from .sound import SoundEngine
from engine.deepcore import DeepCore
from .utils import Settings, PgnFile, ChessFile

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMenuBar, QAction, QFileDialog, QMessageBox, QDialog,
    QCheckBox, QComboBox, QSlider, QGroupBox, QFormLayout, QSpinBox,
    QColorDialog, QButtonGroup, QRadioButton, QTabWidget, QApplication
)

from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QRect, QTimer, QPoint
from PyQt5.QtGui import QIcon, QFont, QDesktopServices, QPixmap, QPainter, QPen, QBrush, QKeyEvent
from typing import Tuple, Optional, List


class Chess(QWidget):
    """
    Main widget for the DeepCore chess game GUI.

    This class sets up the game window, initializes the game logic and sound engine,
    and manages user interactions such as piece selection and move highlighting.

    Attributes:
        game (Game): Handles chess logic and state.
        sound (SoundEngine): Plays sound effects for moves and events.
        selected_piece (tuple | None): The currently selected piece (row, col), or None.
        possible_moves (list): List of legal moves for the selected piece.
    """

    def __init__(self, parent=None) -> None:
        super(Chess, self).__init__(parent=parent)

        # set up the Game window
        self.q_painter: QPainter = QPainter()
        self.setFixedSize(WIDTH, HEIGHT)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR.name()};")

        # Create Game and Sounds objects
        self.game = Game()
        self.sound = SoundEngine()

        self.selected_piece: tuple | None = None
        self.possible_moves: list = []

    def paintEvent(self, event) -> None:
        """ This method will handle paintEvent to draw stuff"""

        self.q_painter.begin(self)
        self.q_painter.setRenderHint(QPainter.Antialiasing)

        # Draw a border around the board
        board_rect: int = QRect(OFFSET_X - 5, OFFSET_Y - 5, SQSize * 8 + 10, SQSize * 8 + 10)

        self.q_painter.setPen(QPen(QColor(30, 30, 30), 2))
        self.q_painter.setBrush(QBrush(QColor(40, 40, 40)))
        self.q_painter.drawRect(board_rect)

        # Draw the board and pieces
        self.draw_board()
        self.draw_coordinates()
        self.draw_pieces()

        # Highlight king checks
        if hasattr(self, 'check_position') and self.check_position:
            painter = QPainter(self)
            row, col = self.check_position

            square_size = self.width() // 8
            x = col * square_size
            y = row * square_size

            # Draw red rectangle
            painter.setPen(QPen(Qt.red, 3))
            painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
            painter.drawRect(x, y, square_size, square_size)

        self.q_painter.end()

    def draw_board(self) -> None:
        """ This method will draw the chess board with enhanced visuals"""

        # Drawing the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                x: int = (row + col) % 2
                # Set Color - using professional chess colors
                color = DARK_SQUARE if x == 0 else LIGHT_SQUARE

                # For selected piece coloring
                if (row, col) == self.selected_piece:
                    color = HIGHLIGHT_COLOR

                # For possible moves coloring
                if self.possible_moves is not None and (row, col) in self.possible_moves:
                    # Draw different indicators for empty squares vs. captures
                    rect = QRect(OFFSET_X + col * SQSize, OFFSET_Y + row * SQSize, SQSize, SQSize)
                    self.q_painter.fillRect(rect, color)

                    if not self.game.is_piece((row, col)):
                        # Empty square - draw a dot
                        self.q_painter.setPen(Qt.NoPen)
                        self.q_painter.setBrush(QBrush(MOVE_COLOR))
                        center_x = OFFSET_X + col * SQSize + SQSize // 2
                        center_y = OFFSET_Y + row * SQSize + SQSize // 2
                        self.q_painter.drawEllipse(center_x - SQSize // 8, center_y - SQSize // 8, SQSize // 4, SQSize // 4)
                        continue
                    else:
                        # Capture - draw a highlighted border
                        self.q_painter.setPen(QPen(MOVE_COLOR, 3))
                        self.q_painter.setBrush(Qt.NoBrush)
                        self.q_painter.drawRect(rect)
                        continue

                # Draw Board
                self.q_painter.fillRect(OFFSET_X + col * SQSize, OFFSET_Y + row * SQSize, SQSize, SQSize, color)

    def draw_coordinates(self) -> None:
        """Draw board coordinates (a-h, 1-8)"""
        self.q_painter.setPen(QColor(180, 180, 180))
        self.q_painter.setFont(QFont('Arial', 10))

        # Draw column coordinates (a-h)
        for col in range(BOARD_SIZE):
            x = OFFSET_X + col * SQSize + SQSize - 14
            y = OFFSET_Y + 8 * SQSize + 20
            self.q_painter.drawText(x, y, chr(97 + col))

        # Draw row coordinates (1-8)
        for row in range(BOARD_SIZE):
            x = OFFSET_X - 14
            y = OFFSET_Y + row * SQSize + 20
            self.q_painter.drawText(x, y, str(8 - row))

    def draw_pieces(self) -> None:
        """ This method will draw pieces on the board with enhanced styling"""

        # Drawing the pieces
        for pos, piece in self.game.board.items():
            row, col = pos
            x = OFFSET_X + col * SQSize + SQSize // 4
            y = OFFSET_Y + row * SQSize + 3 * SQSize // 4
            if piece is not None:
                # Set color based on piece color
                if piece.color == 'white':
                    self.q_painter.setPen(QColor(255, 255, 255))
                else:
                    self.q_painter.setPen(QColor(0, 0, 0))

                # Draw the piece with better font
                self.q_painter.setFont(QFont('Arial', SQSize // 2, QFont.Bold))
                self.q_painter.drawText(x, y, piece.texture)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events for piece selection and movement."""

        x: int = event.x()
        y: int = event.y()

        # Determine the clicked square
        col: int = (x - OFFSET_X) // SQSize
        row: int = (y - OFFSET_Y) // SQSize

        # Check if the mouse press is inside the board
        if not (0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE):
            self.clear_selection()
            self.update()
            return

        clicked_position = (row, col)
        clicked_piece = self.game.get_piece(clicked_position)

        # Handle piece selection logic
        if self.selected_piece is None:
            self._handle_piece_selection(clicked_position, clicked_piece)
        else:
            self._handle_move_or_reselection(clicked_position, clicked_piece)

        # Update the display
        self.update()

    def _handle_piece_selection(self, position: Tuple[int, int], piece: Optional[Piece]) -> None:
        """Handle initial piece selection."""
        # Check if clicked square contains a piece of the current player
        if piece and piece.color == self.game.current_turn:
            # Get legal moves for the selected piece
            legal_moves = self._get_legal_moves_for_piece(position)

            if legal_moves:  # Only select if a piece has legal moves
                self.selected_piece = position
                self.possible_moves = legal_moves
                self.draw_board()
            else:
                # The Piece has no legal moves, show feedback
                self._show_no_moves_feedback(position)
        else:
            # Clicked on empty square or opponent's piece
            self.clear_selection()

    def _handle_move_or_reselection(self, position: Tuple[int, int], piece: Optional[Piece]) -> None:
        """Handle move execution or piece reselection."""
        # Check if clicking on the same piece (deselect)
        if self.selected_piece == position:
            self.clear_selection()
            return

        # Check if clicking on another piece of the same color (reselect)
        if piece and piece.color == self.game.current_turn:
            legal_moves = self._get_legal_moves_for_piece(position)
            if legal_moves:
                self.selected_piece = position
                self.possible_moves = legal_moves
                self.draw_board()
            else:
                self._show_no_moves_feedback(position)
            return

        # Attempt to make a move
        if position in self.possible_moves:
            self._execute_move(self.selected_piece, position)
        else:
            # Invalid move, clear selection
            self.clear_selection()
            # self._show_invalid_move_feedback(position)

    def _get_legal_moves_for_piece(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all legal moves for a piece at the given position."""
        piece = self.game.get_piece(position)
        if not piece:
            return []

        # Get possible moves from the piece
        possible_moves = piece.possible_moves(position, self.game.board)

        # Filter to only include legal moves (don't leave king in check)
        legal_moves: list = []
        for move in possible_moves:
            if self.game.is_legal_move(position, move):
                legal_moves.append(move)

        # Add castling moves for king
        if isinstance(piece, King):
            legal_moves.extend(self._get_castling_moves(piece.color))

        return legal_moves

    def _get_castling_moves(self, color: str) -> List[Tuple[int, int]]:
        """Get available castling moves for the given color."""
        castling_moves = []
        row = 0 if color == 'black' else 7

        if self.game.can_castle(color, 'kingside'):
            castling_moves.append((row, 6))

        if self.game.can_castle(color, 'queenside'):
            castling_moves.append((row, 2))

        return castling_moves

    def _execute_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        """Execute a move and handle all associated game logic."""
        piece = self.game.get_piece(from_pos)

        # Check for pawn promotion
        promotion_piece = 'queen'  # Default promotion
        if isinstance(piece, Pawn) and self.game.is_promotion(from_pos, to_pos):
            promotion_piece = self._get_promotion_choice()

        # Execute the move
        move_successful = self.game.make_move(from_pos, to_pos, promotion_piece)

        if move_successful:
            # Play move sound
            if hasattr(self, 'sound'):
                self._play_move_sound(from_pos, to_pos)

            # Clear selection
            self.clear_selection()

            # Check game state and show appropriate feedback
            self._handle_game_state_change()

            # Update board display
            self.draw_board()
        else:
            # Move failed, clear selection and show error
            self.clear_selection()
            self._show_move_failed_feedback()

    def _get_promotion_choice(self) -> str:
        """Get the player's choice for pawn promotion."""
        # This could be enhanced with a dialog box for piece selection
        # For now, return queen as default
        # TODO: Implement promotion dialog
        return 'queen'

    def _play_move_sound(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        """Play the appropriate sound based on a move type."""
        last_move = self.game.move_history[-1] if self.game.move_history else None

        if not last_move:
            return

        try:
            if last_move.is_castling:
                self.sound.play_castle_sound()
            elif last_move.captured_piece:
                self.sound.play_capture_sound()
            elif last_move.is_promotion:
                self.sound.play_promotion_sound()
            elif self.game.game_state == GameState.CHECK:
                self.sound.play_check_sound()
            else:
                self.sound.play_move_sound()
        except AttributeError:
            # Fallback to basic move sound if specific sounds don't exist
            self.sound.play_move_sound()

    def _handle_game_state_change(self) -> None:
        """Handle changes in game state (check, checkmate, etc.)."""
        if self.game.game_state == GameState.CHECKMATE:
            winner = 'Black' if self.game.current_turn == 'white' else 'White'
            self._show_game_over_message(f"Checkmate! {winner} wins!")
        elif self.game.game_state == GameState.STALEMATE:
            self._show_game_over_message("Stalemate! The game is a draw.")
        elif self.game.game_state == GameState.DRAW:
            self._show_game_over_message("Draw! (50-move rule)")
        elif self.game.game_state == GameState.CHECK:
            self._check_highlight(self.game.current_turn)

    def clear_selection(self) -> None:
        """Clear the current piece selection and possible moves."""
        self.selected_piece = None
        self.possible_moves = []

    def _show_no_moves_feedback(self, position: Tuple[int, int]) -> None:
        """Show feedback when a piece has no legal moves."""
        # This could be enhanced with visual feedback
        # For now, just clear selection
        self.clear_selection()

    def _show_game_over_message(self, status: str, show_restart: bool = True) -> bool:
        """Show a sleek, modern game-over dialog with glassmorphism styling."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Game Over")
        msg_box.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Create custom content with iOS-style typography
        content = f"""
        <div style='text-align: center; padding: 16px;'>
            <div style='font-size: 32px; margin-bottom: 12px;'>🎮</div>
            <h2 style='color: #1c1c1e; font-weight: 600; margin: 0 0 6px 0; font-size: 18px;'>Game Over</h2>
            <p style='color: #8e8e93; margin: 0; font-size: 14px; line-height: 1.3;'>{status}</p>
        </div>
        """
        msg_box.setText(content)

        if show_restart:
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.button(QMessageBox.Yes).setText("Play Again")
            msg_box.button(QMessageBox.No).setText("Exit")
            msg_box.setDefaultButton(QMessageBox.Yes)
        else:
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)

        # iOS-style clean white/gray styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: rgba(255, 255, 255, 0.95);
                border: none;
                border-radius: 14px;
                min-width: 280px;
                max-width: 320px;
                min-height: 140px;
            }

            QMessageBox QLabel {
                background: transparent;
                color: #1c1c1e;
                border: none;
                padding: 20px 16px 16px 16px;
            }

            QPushButton {
                background-color: transparent;
                color: #007aff;
                border: none;
                border-top: 0.5px solid rgba(60, 60, 67, 0.29);
                border-radius: 0px;
                padding: 16px 12px;
                font-size: 17px;
                font-weight: 400;
                min-height: 44px;
            }

            QPushButton:hover {
                background-color: rgba(0, 122, 255, 0.05);
            }

            QPushButton:pressed {
                background-color: rgba(0, 122, 255, 0.1);
            }

            QPushButton:default {
                color: #007aff;
                font-weight: 600;
            }

            QPushButton:default:hover {
                background-color: rgba(0, 122, 255, 0.05);
            }

            QPushButton:default:pressed {
                background-color: rgba(0, 122, 255, 0.1);
            }

            QPushButton:first-child {
                border-bottom-left-radius: 14px;
            }

            QPushButton:last-child {
                border-bottom-right-radius: 14px;
            }

            QPushButton:only-child {
                border-bottom-left-radius: 14px;
                border-bottom-right-radius: 14px;
            }
        """)

        # Center the dialog on screen
        msg_box.move(
            self.geometry().center() - msg_box.rect().center()
        )

        result = msg_box.exec_()
        return result == QMessageBox.Yes if show_restart else False

    def _check_highlight(self, player: str) -> None:
        """ This method will color the king in check"""

        king_pos: tuple = self.game.get_king_position(player)

        print(king_pos)

    def reset_game(self) -> None:
        """Reset the game to initial state"""

        # Clear all variables
        self.selected_piece, self.possible_moves = None, []
        # Create a new board
        self.game.new_game()
        # Update the game
        self.update()

    def undo_move(self) -> None:
        """Undo the last move"""

        # get Undo move
        self.game.undo_move()
        # Update the board
        self.update()

    def redo_move(self) -> None:
        """Redo the last undone move"""

        # get Redo move
        # Update the board
        self.update()



    @staticmethod
    def _load_default_settings() -> dict:
        """Load default application settings."""
        return {
            'sound_enabled': True,
            'show_coordinates': True,
            'animate_moves': True,
            'theme': 'Classic',
            'board_size': 600,
            'highlight_color': '#FFD700',
            'auto_save': True,
            'deepcore_level': 3,
            'time_limit': 0,  # 0 means no time limit
        }


class MainWindow(QMainWindow):
    """
    Enhanced main application window for the DeepCore chess GUI.

    Features a clean, modern interface with improved organization,
    better styling, and integrated settings management.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"DeepCore Chess - v{VERSION}")
        self.setGeometry(100, 100, WIDTH + 300, HEIGHT + 100)
        self.setWindowIcon(QIcon(str(APP_ICON)))
        self.setMinimumSize(800, 600)

        # Initialize central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Initialize utils
        updater = Updater()

        # Initialize Widgets
        self.settings_widget = SettingsWidget(self)
        self.update_widget: UpdateWidget | None = UpdateWidget() if updater.is_new_update() else None

        # Main layout with improved spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Chess board widget
        self.chess_board = Chess()

        # Enhanced right panel
        self.right_panel = self._create_right_panel()

        # Add widgets to the main layout
        main_layout.addWidget(self.chess_board, 3)  # Give more space to board
        main_layout.addWidget(self.right_panel, 1)

        # Set time to call '_update' method every 50 ms
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update)
        self.update_timer.start(50)

        # Enhanced status bar
        self._setup_status_bar()
        self._create_menu_bar()
        self._apply_theme()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:

            for widget in [self.settings_widget, self.about_box, self.shortcuts_msg]:
                if widget.isVisible():
                    widget.hide()

        elif event.key() == Qt.Key_Left:
            self.chess_board.undo_move()

        elif event.key() == Qt.Key_Right:
            self.chess_board.redo_move()

    def _apply_theme(self):
        """Apply the current theme styling."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_COLOR.name()};
            }}
            QFrame#rightPanel {{
                background-color: {PANEL_COLOR.name()};
                border-radius: 12px;
                border: 1px solid #504945;
            }}
            QLabel#turnLabel {{
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(102, 92, 84, 0.3);
                border-radius: 8px;
                margin: 5px;
            }}
            QLabel#statusLabel {{
                color: white;
                font-size: 14px;
                padding: 5px;
            }}
            QPushButton {{
                {BUTTON_STYLE}
                min-height: 45px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #7C6F64;
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: #504945;
                transform: translateY(1px);
            }}
            QStatusBar {{
                background-color: {PANEL_COLOR.name()};
                border-top: 1px solid #504945;
            }}
        """)

    def _create_right_panel(self) -> QFrame:
        """Create the enhanced right control panel."""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setMinimumWidth(250)
        panel.setMaximumWidth(280)

        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Game status section
        self.turn_label = QLabel("White's Turn")
        self.turn_label.setObjectName("turnLabel")
        self.turn_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.turn_label)

        # Add separator
        layout.addSpacing(10)

        # Add stretch to push everything to the top
        layout.addStretch()

        # Game info section (expandable)
        info_label = QLabel("Game Information")
        info_label.setStyleSheet("color: #A89984; font-weight: bold; margin-top: 20px;")
        layout.addWidget(info_label)

        self.moves_label = QLabel("Moves: 0")
        self.moves_label.setStyleSheet("color: white; margin-left: 10px;")
        layout.addWidget(self.moves_label)

        self.time_label = QLabel("Time: --:--")
        self.time_label.setStyleSheet("color: white; margin-left: 10px;")
        layout.addWidget(self.time_label)

        return panel

    def _setup_status_bar(self):
        """Set up the enhanced status bar."""
        self.status_label = QLabel("Game Ready - Welcome to DeepCore Chess")
        self.status_label.setObjectName("statusLabel")
        self.statusBar().addWidget(self.status_label)

        # Add additional status information
        self.game_mode_label = QLabel("Mode: Human vs AI")
        self.game_mode_label.setStyleSheet("color: #A89984;")
        self.statusBar().addPermanentWidget(self.game_mode_label)

    def _create_menu_bar(self):
        """Create and configure the enhanced menu bar."""
        self.setStyleSheet(self.styleSheet() + f"""
            QMenuBar {{
                background-color: {PANEL_COLOR.name()};
                color: white;
                padding: 4px;
                border-bottom: 1px solid #504945;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 6px;
                margin: 2px;
            }}
            QMenuBar::item:selected {{
                background-color: #665C54;
            }}
            QMenu {{
                background-color: {PANEL_COLOR.name()};
                color: white;
                border: 1px solid #504945;
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 30px 8px 25px;
                border-radius: 4px;
                margin: 1px;
            }}
            QMenu::item:selected {{
                background-color: #665C54;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #504945;
                margin: 4px 8px;
            }}
        """)

        menubar = self.menuBar()
        # File menu
        self._create_file_menu(menubar)
        # Edit menu
        self._create_edit_menu(menubar)
        # View a menu
        self._create_view_menu(menubar)
        # Help a menu
        self._create_help_menu(menubar)

    def _create_file_menu(self, menubar):
        """Create the File menu."""
        file_menu = menubar.addMenu(' File')

        actions = [
            ('🎮 New Game', 'Ctrl+N', self._new_game),
            (' Open Game...', 'Ctrl+O', self._open_game),
            (' Save Game', 'Ctrl+S', self._save_game),
            (' Save As...', 'Ctrl+Shift+S', self._save_game_as),
            None,  # Separator

            (' Export PGN...', None, self._export_pgn),
            (' Import PGN...', None, self._import_pgn),
            None,  # Separator

            (' Exit', 'Ctrl+Q', self.close),
        ]

        for action_data in actions:
            if action_data is None:
                file_menu.addSeparator()
            else:
                text, shortcut, callback = action_data
                action = QAction(text, self)
                if shortcut:
                    action.setShortcut(shortcut)
                action.triggered.connect(callback)
                file_menu.addAction(action)

    def _create_edit_menu(self, menubar):
        """Create the Edit menu."""
        edit_menu = menubar.addMenu(' Edit')

        undo_action = QAction('↶ Undo Move', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.chess_board.undo_move)

        redo_action = QAction('↷ Redo Move', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.chess_board.redo_move)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()

        preferences_action = QAction('⚙️ Preferences...', self)
        preferences_action.setShortcut('Ctrl+,')
        preferences_action.triggered.connect(self.settings_widget.show)
        edit_menu.addAction(preferences_action)

    def _create_view_menu(self, menubar):
        """Create the View menu."""
        view_menu = menubar.addMenu(' View')

        fullscreen_action = QAction(' Fullscreen', self, checkable=True)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self._toggle_fullscreen)

        coordinates_action = QAction(' Show Coordinates', self, checkable=True)
        coordinates_action.setChecked(True)
        coordinates_action.triggered.connect(self._toggle_coordinates)

        view_menu.addAction(fullscreen_action)
        view_menu.addAction(coordinates_action)

    def _create_help_menu(self, menubar):
        """Create the Help menu."""
        help_menu = menubar.addMenu(' Help')

        help_menu.addAction(' Keyboard Shortcuts', self._show_shortcuts)
        help_menu.addSeparator()
        help_menu.addAction(' About DeepCore', self._show_about)

    def _new_game(self) -> None:
        """ This method will restart a new game"""
        self.chess_board.reset_game()

    def _open_game(self):
        """Open a saved game file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Chess Game", "",
            "Chess Game Files (*.chess);;PGN Files (*.pgn);;All Files (*)"
        )
        if file_name:
            self._update_status(f"Opened: {file_name}")

    def _save_game(self):
        """Save the current game."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Chess Game", "",
            "Chess Game Files (*.chess);;PGN Files (*.pgn);;All Files (*)"
        )
        if file_name:
            self._update_status(f"Saved: {file_name}")

    def _save_game_as(self):
        """Save game with a new name."""
        self._save_game()

    def _export_pgn(self):
        """Export game in PGN format."""
        print("PGN export feature coming soon")

    def _import_pgn(self):
        """Import game from PGN format."""
        print("PGN import feature coming soon")

    def _toggle_fullscreen(self, checked):
        """Toggle fullscreen mode."""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def _toggle_coordinates(self, checked):
        """Toggle coordinate display."""
        self._update(f"Coordinates {'shown' if checked else 'hidden'}")

    def _show_shortcuts(self):
        """Show keyboard shortcuts."""
        self.shortcuts_msg = QMessageBox(self)
        self.shortcuts_msg.setWindowTitle("Keyboard Shortcuts")
        self.shortcuts_msg.setIcon(QMessageBox.Information)
        self.shortcuts_msg.setText("DeepCore Chess Shortcuts")
        self.shortcuts_msg.setInformativeText(
            "File Operations:\n"
            "• Ctrl+N: New Game\n"
            "• Ctrl+O: Open Game\n"
            "• Ctrl+S: Save Game\n"
            "• Ctrl+Q: Exit\n\n"
            
            "Game Controls:\n"
            "• Ctrl+Z: Undo Move\n"
            "• Ctrl+Y: Redo Move\n"
            "• F11: Toggle Fullscreen\n\n"
            
            "Settings:\n"
            "• Ctrl+,: Open Preferences\n\n"
            
            "View:\n"
            "• F11: Fullscreen Mode"
        )
        self.shortcuts_msg.exec()

    def _show_about(self) -> None:
        """Show an About dialog with detailed information and clickable links."""

        self.about_box = QMessageBox(self)
        self.about_box.setWindowTitle("About DeepCore")

        # Check if APP_ICON exists and is valid
        if APP_ICON and os.path.exists(APP_ICON):
            self.about_box.setIconPixmap(QIcon(APP_ICON).pixmap(64, 64))

        # Set the main text
        self.about_box.setTextFormat(Qt.RichText)
        self.about_box.setText(ABOUT_TEXT)

        # Informative text with clickable links for website and GitHub
        self.about_box.setInformativeText(LINKS_TEXT)

        # Add Donate button
        donate_button = self.about_box.addButton("Donate", QMessageBox.ActionRole)
        self.about_box.addButton(QMessageBox.Ok)

        # Show the dialog modally
        self.about_box.exec()

        # If Donate clicked, open donation URL
        if self.about_box.clickedButton() == donate_button:
            donation_url: str = DONATE_URL  # Replace it with your real URL
            QDesktopServices.openUrl(QUrl(donation_url))

    def _update(self) -> None:
        """ This method will update stuff"""

        # update the turn label
        play_turn: str = self.chess_board.game.current_turn
        self.turn_label.setText(f"{play_turn.capitalize()}' turn")
        self.turn_label.setStyleSheet(f"color: {play_turn};")



class SettingsWidget(QWidget):
    """
    Settings configuration dialog for the chess application.

    Provides a comprehensive interface for customizing game preferences,
    appearance, and behavior settings.
    """

    def __init__(self, parent):
        super().__init__(parent=parent)

        # Load settings
        self.settings: dict = Settings.load_settings()



class UpdateWidget(QWidget):

    STYLE: str = """
    QLabel {
        color: #4E4D4D;
        weight: 500;
    }

    QPushButton {
        width: 80px;
        height: 35px;
        color: #4E4D4D;

        border: 1px;
        border-radius: 4px;
        border-color: #54656C;
        background-color: transparent;
    }

    QPushButton::hover {
        font-size: 16px;
    }
    """

    def __init__(self):
        super().__init__(parent=None)

        # Set up the Updater window
        self.setFixedSize(500, 120)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #DCDDDD;")

        # Create Updater label
        self.update_label = QLabel(f"New update available! Please download the latest version.", self)
        self.update_label.setFont(QFont("Ubuntu", 11))
        self.update_label.move(10, 20)
        self.update_label.setStyleSheet(self.STYLE)

        # Create Cancel button
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.move(15, 80)
        self.cancel_button.setStyleSheet(self.STYLE)
        self.cancel_button.setFont(QFont("Ubuntu", 11))
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self._cancel)

        # Create Install now button
        self.install_button = QPushButton("Install Now", self)
        self.install_button.move(110, 80)
        self.install_button.setStyleSheet(self.STYLE)
        self.install_button.setFont(QFont("Ubuntu", 10))
        self.install_button.setCursor(Qt.PointingHandCursor)
        self.install_button.clicked.connect(self._install)

        # Show Updater widget
        self.show()

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
        except TypeError:
            pass

    def _install(self) -> None:
        """ This method will start software update"""

    def _cancel(self) -> None:
        """ This method will hide the updater widget and kill it """




def __main__() -> None:
    """ This function will start the DeepCore interface"""

    # Create QApplication object
    app: QApplication = QApplication(sys.argv)

    # Create MainWindow object
    window = MainWindow()
    window.show()

    print(f"Executed in : {perf_counter() - S_TIME:.4f} s")
    sys.exit(app.exec_())


if __name__ == '__main__':
    sys.exit(0)

"""
This code or file is pertinent to the 'DeepCore' Project
Copyright (c) 2024-2025, 'Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.

@author : Aymen Brahim Djelloul
date    : 31.07.2024
version : 0.1
license : MIT
"""

# IMPORTS
import sys
from .utils import *
from .const import *
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional


class Piece(ABC):
    """
    Abstract base class for all chess pieces.

    :param color: The color of the piece ('white' or 'black')
    :param value: The point value of the piece
    """

    def __init__(self, color: str, value: float):
        if color not in ('white', 'black'):
            raise ValueError("Color must be 'white' or 'black'")

        self.color = color
        self.value = value
        self.captured = False
        self.has_moved = False  # Track if piece has moved (useful for castling, pawn first move)

    @abstractmethod
    def possible_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional['Piece']]) -> List[Tuple[int, int]]:
        """
        Calculate all possible moves for this piece from the given position.

        :param piece_position: Current position of the piece (row, col)
        :param board: Dictionary representing the board state
        :return: List of valid move positions
        """
        pass

    @staticmethod
    def is_valid_position(row: int, col: int) -> bool:
        """Check if a position is within the board boundaries."""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def is_enemy_piece(self, piece: Optional['Piece']) -> bool:
        """Check if a piece is an enemy piece."""
        return piece is not None and piece.color != self.color

    @staticmethod
    def is_empty_square(piece: Optional['Piece']) -> bool:
        """Check if a square is empty."""
        return piece is None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.color}, {self.value})"


class Pawn(Piece):
    """Chess Pawn piece implementation."""

    def __init__(self, color: str, value: float = 1.0):
        super().__init__(color, value)
        self.texture = WHITE_PAWN if self.color == 'white' else BLACK_PAWN

    def possible_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]]) -> List[Tuple[int, int]]:
        """Calculate possible moves for the pawn."""
        possible_moves = []
        row, col = piece_position

        # Determine move direction based on color
        direction = 1 if self.color == 'black' else -1
        start_row = 1 if self.color == 'black' else 6

        # Forward moves
        forward_one = (row + direction, col)
        if self.is_valid_position(*forward_one) and self.is_empty_square(board.get(forward_one)):
            possible_moves.append(forward_one)

            # Double move from starting position
            if row == start_row:
                forward_two = (row + 2 * direction, col)
                if self.is_valid_position(*forward_two) and self.is_empty_square(board.get(forward_two)):
                    possible_moves.append(forward_two)

        # Capture moves (diagonal)
        for col_offset in [-1, 1]:
            capture_pos = (row + direction, col + col_offset)
            if (self.is_valid_position(*capture_pos) and
                self.is_enemy_piece(board.get(capture_pos))):
                possible_moves.append(capture_pos)

        return possible_moves


class Knight(Piece):
    """Chess Knight piece implementation."""

    def __init__(self, color: str, value: float = 3.0):
        super().__init__(color, value)
        self.texture = WHITE_KNIGHT if self.color == 'white' else BLACK_KNIGHT

    def possible_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]]) -> List[Tuple[int, int]]:
        """Calculate possible moves for the knight."""
        possible_moves = []
        row, col = piece_position

        # All possible knight moves (L-shaped)
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc

            if self.is_valid_position(new_row, new_col):
                target_piece = board.get((new_row, new_col))
                if self.is_empty_square(target_piece) or self.is_enemy_piece(target_piece):
                    possible_moves.append((new_row, new_col))

        return possible_moves


class Rook(Piece):
    """Chess Rook piece implementation."""

    def __init__(self, color: str, value: float = 5.0):
        super().__init__(color, value)
        self.texture = WHITE_ROOK if self.color == "white" else BLACK_ROOK

    def possible_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]]) -> List[Tuple[int, int]]:
        """Calculate possible moves for the rook."""
        return self._get_line_moves(piece_position, board, [(0, 1), (1, 0), (-1, 0), (0, -1)])

    def _get_line_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]], directions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Helper method to get moves along straight lines."""
        possible_moves = []
        row, col = piece_position

        for dr, dc in directions:
            current_row, current_col = row, col

            while True:
                current_row += dr
                current_col += dc

                if not self.is_valid_position(current_row, current_col):
                    break

                target_piece = board.get((current_row, current_col))

                if self.is_empty_square(target_piece):
                    possible_moves.append((current_row, current_col))
                elif self.is_enemy_piece(target_piece):
                    possible_moves.append((current_row, current_col))
                    break  # Can't move past an enemy piece after capturing
                else:
                    break  # Blocked by own piece

        return possible_moves


class Bishop(Piece):
    """Chess Bishop piece implementation."""

    def __init__(self, color: str, value: float = 3.0):
        super().__init__(color, value)
        self.texture = WHITE_BISHOP if self.color == 'white' else BLACK_BISHOP

    def possible_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]]) -> List[Tuple[int, int]]:
        """Calculate possible moves for the bishop."""
        return self._get_diagonal_moves(piece_position, board)

    def _get_diagonal_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]]) -> List[Tuple[int, int]]:
        """Helper method to get moves along diagonal lines."""
        possible_moves = []
        row, col = piece_position
        diagonal_directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]

        for dr, dc in diagonal_directions:
            current_row, current_col = row, col

            while True:
                current_row += dr
                current_col += dc

                if not self.is_valid_position(current_row, current_col):
                    break

                target_piece = board.get((current_row, current_col))

                if self.is_empty_square(target_piece):
                    possible_moves.append((current_row, current_col))
                elif self.is_enemy_piece(target_piece):
                    possible_moves.append((current_row, current_col))
                    break
                else:
                    break

        return possible_moves


class Queen(Piece):
    """Chess Queen piece implementation."""

    def __init__(self, color: str, value: float = 9.0):
        super().__init__(color, value)
        self.texture = WHITE_QUEEN if self.color == 'white' else BLACK_QUEEN

    def possible_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]]) -> List[Tuple[int, int]]:
        """Calculate possible moves for the queen (combination of rook and bishop moves)."""
        possible_moves = []
        row, col = piece_position

        # Queen moves like both rook and bishop
        all_directions = [
            # Rook directions (horizontal/vertical)
            (1, 0), (0, 1), (0, -1), (-1, 0),
            # Bishop directions (diagonal)
            (-1, -1), (1, -1), (-1, 1), (1, 1)
        ]

        for dr, dc in all_directions:
            current_row, current_col = row, col

            while True:
                current_row += dr
                current_col += dc

                if not self.is_valid_position(current_row, current_col):
                    break

                target_piece = board.get((current_row, current_col))

                if self.is_empty_square(target_piece):
                    possible_moves.append((current_row, current_col))
                elif self.is_enemy_piece(target_piece):
                    possible_moves.append((current_row, current_col))
                    break
                else:
                    break

        return possible_moves


class King(Piece):
    """Chess King piece implementation."""

    def __init__(self, color: str, value: float = float('inf')):
        super().__init__(color, value)
        self.texture = WHITE_KING if color == 'white' else BLACK_KING

    def possible_moves(self, piece_position: Tuple[int, int], board: Dict[Tuple[int, int], Optional[Piece]]) -> List[Tuple[int, int]]:
        """Calculate possible moves for the king (one square in any direction)."""
        possible_moves = []
        row, col = piece_position

        # King can move one square in any direction
        king_directions = [
            (1, 0), (0, 1), (0, -1), (-1, 0),
            (-1, -1), (1, -1), (-1, 1), (1, 1)
        ]

        for dr, dc in king_directions:
            new_row, new_col = row + dr, col + dc

            if self.is_valid_position(new_row, new_col):
                target_piece = board.get((new_row, new_col))
                if self.is_empty_square(target_piece) or self.is_enemy_piece(target_piece):
                    possible_moves.append((new_row, new_col))

        return possible_moves

    def can_castle_kingside(self, board: Dict[Tuple[int, int], Optional[Piece]]) -> bool:
        """Check if kingside castling is possible."""
        if self.has_moved:
            return False

        row = 0 if self.color == 'black' else 7
        rook_pos = (row, 7)
        rook = board.get(rook_pos)

        # Check if rook exists and hasn't moved
        if not isinstance(rook, Rook) or rook.has_moved:
            return False

        # Check if squares between king and rook are empty
        for col in range(5, 7):
            if board.get((row, col)) is not None:
                return False

        return True

    def can_castle_queenside(self, board: Dict[Tuple[int, int], Optional[Piece]]) -> bool:
        """Check if queenside castling is possible."""
        if self.has_moved:
            return False

        row = 0 if self.color == 'black' else 7
        rook_pos = (row, 0)
        rook = board.get(rook_pos)

        # Check if rook exists and hasn't moved
        if not isinstance(rook, Rook) or rook.has_moved:
            return False

        # Check if squares between king and rook are empty
        for col in range(1, 4):
            if board.get((row, col)) is not None:
                return False

        return True


# # Factory function for creating pieces
# def create_piece(piece_type: str, color: str) -> Piece:
#     """
#     Factory function to create chess pieces.
#
#     :param piece_type: Type of piece ('pawn', 'knight', 'bishop', 'rook', 'queen', 'king')
#     :param color: Color of piece ('white' or 'black')
#     :return: Piece instance
#     """
#     piece_classes = {
#         'pawn': Pawn,
#         'knight': Knight,
#         'bishop': Bishop,
#         'rook': Rook,
#         'queen': Queen,
#         'king': King
#     }
#
#     piece_class = piece_classes.get(piece_type.lower())
#     if not piece_class:
#         raise ValueError(f"Unknown piece type: {piece_type}")
#
#     return piece_class(color)


if __name__ == "__main__":
    sys.exit()
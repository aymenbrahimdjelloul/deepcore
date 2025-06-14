"""
This code or file is pertinent to the 'DeepCore' Project
Copyright (c) 2024-2025, 'Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.

@author : Aymen Brahim Djelloul
version : 0.2
date    : 31.07.2024
license : MIT
"""

# IMPORTS
from .pieces import *
from .const import *
import sys
from typing import Optional, Tuple, List, Dict, Union
from enum import Enum
from dataclasses import dataclass
from copy import deepcopy


class GameState(Enum):
    """Enumeration for different game states."""

    ACTIVE = "active"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"


@dataclass
class Move:
    """Data class to represent a chess move."""
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    piece: Piece
    captured_piece: Optional[Piece] = None
    is_castling: bool = False
    is_en_passant: bool = False
    is_promotion: bool = False
    promoted_to: Optional[str] = None

    def __str__(self) -> str:
        """String representation of the move."""
        from_notation = f"{chr(97 + self.from_pos[1])}{8 - self.from_pos[0]}"
        to_notation = f"{chr(97 + self.to_pos[1])}{8 - self.to_pos[0]}"
        return f"{from_notation}-{to_notation}"


class Game:
    """Main chess game class that manages the game state and rules."""

    def __init__(self):
        # Game state variables
        self.current_turn: str = 'white'
        self.move_history: List[Move] = []
        self.board: Dict[Tuple[int, int], Optional[Piece]] = self.create_board()
        self.game_state: GameState = GameState.ACTIVE

        # King positions for efficient check detection
        self.white_king_pos: Tuple[int, int] = (7, 4)
        self.black_king_pos: Tuple[int, int] = (0, 4)

        # Castling rights
        self.castling_rights = {
            'white_kingside': True,
            'white_queenside': True,
            'black_kingside': True,
            'black_queenside': True
        }

        # En passant target square
        self.en_passant_target: Optional[Tuple[int, int]] = None

        # Move counters for draw rules
        self.halfmove_clock = 0  # Moves since last pawn move or capture
        self.fullmove_number = 1  # Full moves in the game

    @staticmethod
    def create_board() -> Dict[Tuple[int, int], Optional[Piece]]:
        """Create and return the initial chess board setup."""
        board = {}

        # Define piece placement for back ranks
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if row == 0:  # Black pieces back rank
                    board[(row, col)] = piece_order[col]('black')
                elif row == 1:  # Black pawns
                    board[(row, col)] = Pawn('black')
                elif row == 6:  # White pawns
                    board[(row, col)] = Pawn('white')
                elif row == 7:  # White pieces back rank
                    board[(row, col)] = piece_order[col]('white')
                else:  # Empty squares
                    board[(row, col)] = None

        return board

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within the board boundaries."""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_piece(self, position: Tuple[int, int]) -> Optional[Piece]:
        """Get the piece at the given position."""
        return self.board.get(position)

    def is_square_empty(self, position: Tuple[int, int]) -> bool:
        """Check if a square is empty."""
        return self.get_piece(position) is None

    def is_enemy_piece(self, position: Tuple[int, int], color: str) -> bool:
        """Check if there's an enemy piece at the given position."""
        piece = self.get_piece(position)
        return piece is not None and piece.color != color

    def is_own_piece(self, position: Tuple[int, int], color: str) -> bool:
        """Check if there's an own piece at the given position."""
        piece = self.get_piece(position)
        return piece is not None and piece.color == color

    def get_king_position(self, color: str) -> Tuple[int, int]:
        """Get the current position of the king for the given color."""
        return self.white_king_pos if color == 'white' else self.black_king_pos

    def update_king_position(self, color: str, new_position: Tuple[int, int]) -> None:
        """Update the stored king position."""
        if color == 'white':
            self.white_king_pos = new_position
        else:
            self.black_king_pos = new_position

    def is_square_under_attack(self, position: Tuple[int, int], by_color: str) -> bool:
        """Check if a square is under attack by pieces of the given color."""
        for board_pos, piece in self.board.items():
            if piece and piece.color == by_color:
                possible_moves = piece.possible_moves(board_pos, self.board)
                if position in possible_moves:
                    return True
        return False

    def is_in_check(self, color: str) -> bool:
        """Check if the king of the given color is in check."""
        king_pos = self.get_king_position(color)
        enemy_color = 'black' if color == 'white' else 'white'
        return self.is_square_under_attack(king_pos, enemy_color)

    def get_all_possible_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get all possible moves for pieces of the given color."""
        all_moves = []
        for position, piece in self.board.items():
            if piece and piece.color == color:
                possible_moves = piece.possible_moves(position, self.board)
                for move in possible_moves:
                    all_moves.append((position, move))
        return all_moves

    def simulate_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Dict[Tuple[int, int], Optional[Piece]]:
        """Simulate a move and return the resulting board state."""
        simulated_board = deepcopy(self.board)
        simulated_board[to_pos] = simulated_board[from_pos]
        simulated_board[from_pos] = None
        return simulated_board

    def is_legal_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Check if a move is legal (doesn't leave own king in check)."""
        piece = self.get_piece(from_pos)
        if not piece or piece.color != self.current_turn:
            return False

        # Check if the move is in the piece's possible moves
        possible_moves = piece.possible_moves(from_pos, self.board)
        if to_pos not in possible_moves:
            return False

        # Simulate the move to check if it leaves the king in check
        original_board = self.board
        self.board = self.simulate_move(from_pos, to_pos)

        # Update king position temporarily if king is moving
        original_king_pos = None
        if isinstance(piece, King):
            original_king_pos = self.get_king_position(piece.color)
            self.update_king_position(piece.color, to_pos)

        # Check if king is in check after the move
        in_check = self.is_in_check(piece.color)

        # Restore original state
        self.board = original_board
        if original_king_pos:
            self.update_king_position(piece.color, original_king_pos)

        return not in_check

    def get_legal_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get all legal moves for the given color."""
        legal_moves = []
        all_moves = self.get_all_possible_moves(color)

        for from_pos, to_pos in all_moves:
            if self.is_legal_move(from_pos, to_pos):
                legal_moves.append((from_pos, to_pos))

        return legal_moves

    def is_checkmate(self, color: str) -> bool:
        """Check if the given color is in checkmate."""
        if not self.is_in_check(color):
            return False
        return len(self.get_legal_moves(color)) == 0

    def is_stalemate(self, color: str) -> bool:
        """Check if the given color is in stalemate."""
        if self.is_in_check(color):
            return False
        return len(self.get_legal_moves(color)) == 0

    def can_castle(self, color: str, side: str) -> bool:
        """Check if castling is possible for the given color and side."""
        if self.is_in_check(color):
            return False

        castling_key = f"{color}_{side}"
        if not self.castling_rights.get(castling_key, False):
            return False

        king_pos = self.get_king_position(color)
        row = king_pos[0]

        if side == 'kingside':
            # Check if squares between king and rook are empty
            for col in range(5, 7):
                if not self.is_square_empty((row, col)):
                    return False
                # Check if squares king passes through are under attack
                if self.is_square_under_attack((row, col), 'black' if color == 'white' else 'white'):
                    return False
        else:  # queenside
            # Check if squares between king and rook are empty
            for col in range(1, 4):
                if not self.is_square_empty((row, col)):
                    return False
            # Check if squares king passes through are under attack
            for col in range(2, 4):
                if self.is_square_under_attack((row, col), 'black' if color == 'white' else 'white'):
                    return False

        return True

    def execute_castling(self, color: str, side: str) -> None:
        """Execute castling move."""
        row = 0 if color == 'black' else 7

        if side == 'kingside':
            # Move king
            self.board[(row, 6)] = self.board[(row, 4)]
            self.board[(row, 4)] = None
            self.update_king_position(color, (row, 6))

            # Move rook
            self.board[(row, 5)] = self.board[(row, 7)]
            self.board[(row, 7)] = None
        else:  # queenside
            # Move king
            self.board[(row, 2)] = self.board[(row, 4)]
            self.board[(row, 4)] = None
            self.update_king_position(color, (row, 2))

            # Move rook
            self.board[(row, 3)] = self.board[(row, 0)]
            self.board[(row, 0)] = None

        # Update castling rights
        self.castling_rights[f"{color}_kingside"] = False
        self.castling_rights[f"{color}_queenside"] = False

    def is_piece(self, position: tuple) -> bool:
        """ This method will check if a square is empty or not"""
        return False if self.board[position] is None else True

    def is_promotion(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Check if a move results in pawn promotion."""
        piece = self.get_piece(from_pos)
        if not isinstance(piece, Pawn):
            return False

        target_row = 0 if piece.color == 'white' else 7
        return to_pos[0] == target_row

    def promote_pawn(self, position: Tuple[int, int], piece_type: str = 'queen') -> None:
        """Promote a pawn to the specified piece type."""
        color = self.get_piece(position).color
        self.board[position] = create_piece(piece_type, color)

    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], promotion_piece: str = 'queen') -> bool:
        """
        Make a move on the board.

        :param from_pos: Starting position of the piece
        :param to_pos: Target position for the piece
        :param promotion_piece: Piece to promote pawn to (if applicable)
        :return: True if move was successful, False otherwise
        """
        if not self.is_legal_move(from_pos, to_pos):
            return False

        piece = self.get_piece(from_pos)
        captured_piece = self.get_piece(to_pos)

        # Create move object
        move = Move(
            from_pos=from_pos,
            to_pos=to_pos,
            piece=piece,
            captured_piece=captured_piece
        )

        # Handle special moves
        if isinstance(piece, King) and abs(to_pos[1] - from_pos[1]) == 2:
            # Castling
            side = 'kingside' if to_pos[1] > from_pos[1] else 'queenside'
            if self.can_castle(piece.color, side):
                self.execute_castling(piece.color, side)
                move.is_castling = True
            else:
                return False
        else:
            # Regular move
            self.board[to_pos] = piece
            self.board[from_pos] = None

            # Update king position if king moved
            if isinstance(piece, King):
                self.update_king_position(piece.color, to_pos)

        # Handle pawn promotion
        if self.is_promotion(from_pos, to_pos):
            self.promote_pawn(to_pos, promotion_piece)
            move.is_promotion = True
            move.promoted_to = promotion_piece

        # Update castling rights if rook or king moved
        if isinstance(piece, King):
            self.castling_rights[f"{piece.color}_kingside"] = False
            self.castling_rights[f"{piece.color}_queenside"] = False
        elif isinstance(piece, Rook):
            row = from_pos[0]
            col = from_pos[1]
            if (row, col) == (0, 0):
                self.castling_rights['black_queenside'] = False
            elif (row, col) == (0, 7):
                self.castling_rights['black_kingside'] = False
            elif (row, col) == (7, 0):
                self.castling_rights['white_queenside'] = False
            elif (row, col) == (7, 7):
                self.castling_rights['white_kingside'] = False

        # Mark piece as moved
        piece.has_moved = True

        # Update move counters
        if isinstance(piece, Pawn) or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.current_turn == 'black':
            self.fullmove_number += 1

        # Add move to history
        self.move_history.append(move)

        # Switch turns
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        # Update game state
        self.update_game_state()

        return True

    def update_game_state(self) -> None:
        """Update the current game state based on the board position."""
        if self.is_checkmate(self.current_turn):
            self.game_state = GameState.CHECKMATE
        elif self.is_stalemate(self.current_turn):
            self.game_state = GameState.STALEMATE
        elif self.is_in_check(self.current_turn):
            self.game_state = GameState.CHECK
        elif self.halfmove_clock >= 100:  # 50-move rule
            self.game_state = GameState.DRAW
        else:
            self.game_state = GameState.ACTIVE

    def undo_move(self) -> bool:
        """Undo the last move."""
        if not self.move_history:
            return False

        last_move = self.move_history.pop()

        # Restore the piece to its original position
        self.board[last_move.from_pos] = last_move.piece

        # Restore captured piece or clear destination
        self.board[last_move.to_pos] = last_move.captured_piece

        # Handle special move undos
        if last_move.is_castling:
            # Undo castling - restore rook position
            row = last_move.from_pos[0]
            if last_move.to_pos[1] == 6:  # Kingside
                self.board[(row, 7)] = self.board[(row, 5)]
                self.board[(row, 5)] = None
            else:  # Queenside
                self.board[(row, 0)] = self.board[(row, 3)]
                self.board[(row, 3)] = None

        # Update king position if king was moved
        if isinstance(last_move.piece, King):
            self.update_king_position(last_move.piece.color, last_move.from_pos)

        # Mark piece as not moved if it was the first move
        if len(self.move_history) == 0 or not any(
            move.piece == last_move.piece for move in self.move_history
        ):
            last_move.piece.has_moved = False

        # Switch turns back
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        # Update game state
        self.update_game_state()

        return True

    def new_game(self) -> None:
        """Start a new game by resetting all game state."""
        self.current_turn = 'white'
        self.move_history = []
        self.board = self.create_board()
        self.game_state = GameState.ACTIVE

        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)

        self.castling_rights = {
            'white_kingside': True,
            'white_queenside': True,
            'black_kingside': True,
            'black_queenside': True
        }

        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    # def get_game_status(self) -> str:
    #     """Get a human-readable description of the current game status."""
    #     if self.game_state == GameState.CHECKMATE:
    #         winner = 'Black' if self.current_turn == 'white' else 'White'
    #         return f"Checkmate! {winner} wins."
    #     elif self.game_state == GameState.STALEMATE:
    #         return "Stalemate! The game is a draw."
    #     elif self.game_state == GameState.DRAW:
    #         return "Draw! (50-move rule)"
    #     elif self.game_state == GameState.CHECK:
    #         return f"{self.current_turn.capitalize()} is in check."
    #     else:
    #         return f"{self.current_turn.capitalize()}'s turn."
    #
    # def get_board_display(self) -> str:
    #     """Get a simple text representation of the board for debugging."""
    #     display = "  a b c d e f g h\n"
    #     for row in range(8):
    #         display += f"{8-row} "
    #         for col in range(8):
    #             piece = self.get_piece((row, col))
    #             if piece:
    #                 symbol = piece.__class__.__name__[0]
    #                 if piece.color == 'black':
    #                     symbol = symbol.lower()
    #                 display += f"{symbol} "
    #             else:
    #                 display += ". "
    #         display += f"{8-row}\n"
    #     display += "  a b c d e f g h"
    #     return display


if __name__ == "__main__":
    sys.exit(0)

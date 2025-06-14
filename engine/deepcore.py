#!/usr/bin/env python3

"""
This code or file is pertinent to the 'DeepCore' Project
Copyright (c) 2024-2025, 'Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by an MIT license that can be
found in the LICENSE file.

@author : Aymen Brahim Djelloul
version : 0.1
date    : 21.05.2025
license : MIT

References:
    - https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
    - https://en.wikipedia.org/wiki/Zobrist_hashing
    - https://en.wikipedia.org/wiki/Minimax
    - https://en.wikipedia.org/wiki/Branch_and_bound
    - https://en.wikipedia.org/wiki/Decision_tree_pruning
"""

# IMPORTS
import sys
import random
from .utils import *
from .search import *
from dataclasses import dataclass
from typing import Tuple, Optional


class Const:
    pass  # Placeholder for constants (Zobrist keys, evaluation weights, etc.)


class DeepCore:

    def __init__(self, depth: int = 10,
                 threads: int = 2,
                 use_openbook: bool = True,
                 time_limit: int = 60,
                 dev_mode: bool = False) -> None:

        self._config: dict = {
            "depth": depth,
            "threads": threads,
            "use_openbook": use_openbook,
            "time_limit": time_limit,
            "dev_mode": dev_mode,
        }

        self.board = {}  # Placeholder: should be a board dictionary mapping (row, col) to Piece
        self.turn = 'white'  # 'white' or 'black'

    def config(self, **kwargs) -> None:
        """
        Update DeepCore engine parameters.

        Example:
            engine.config(depth=12, dev_mode=True)
        """
        for key, value in kwargs.items():
            if key in self._config:
                self._config[key] = value
            else:
                raise KeyError(f"Invalid config key: '{key}'")

    def get_config(self) -> dict:
        """Return the current configuration."""
        return self._config.copy()

    def get_best_move(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Return a randomly selected legal move for the current player.
        This is a placeholder method to simulate move generation.

        Returns:
            tuple: ((from_row, from_col), (to_row, to_col)) if a legal move is available.
                   None if no moves are found.
        """
        legal_moves = []

        for position, piece in self.board.items():
            if piece and piece.color == self.turn:
                moves = piece.possible_moves(position, self.board)
                for move in moves:
                    legal_moves.append((position, move))

        return random.choice(legal_moves) if legal_moves else None


if __name__ == '__main__':
    sys.exit(0)

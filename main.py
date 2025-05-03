#!/usr/bin/env python3
import argparse
import sys
import time

from Chess-Engine-in-python.engine.board import Board
from Chess-Engine-in-python.engine.search import Search
from Chess-Engine-in-python.ui.cli import CLI
from Chess-Engine-in-python.ui.gui import GUI

def main():
    parser = argparse.ArgumentParser(description='Chess Engine')
    parser.add_argument('--fen', type=str, help='FEN string for initial position')
    parser.add_argument('--depth', type=int, default=4, help='Search depth')
    parser.add_argument('--time', type=float, default=5.0, help='Search time limit in seconds')
    parser.add_argument('--gui', action='store_true', help='Use GUI interface')
    parser.add_argument('--perft', type=int, help='Run perft test to specified depth')
    args = parser.parse_args()
    
    # Initialize board
    board = Board(args.fen)
    
    # Run perft test if requested
    if args.perft is not None:
        from chess_engine.tests.perft_tests import perft
        start_time = time.time()
        nodes = perft(board, args.perft)
        elapsed = time.time() - start_time
        print(f"Perft({args.perft}) = {nodes} nodes in {elapsed:.2f}s ({nodes/elapsed:.0f} nps)")
        return
    
    # Start UI
    if args.gui:
        ui = GUI(board, args.depth, args.time)
    else:
        ui = CLI(board, args.depth, args.time)
    
    ui.run()

if __name__ == "__main__":
    main()

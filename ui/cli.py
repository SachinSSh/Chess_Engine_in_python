import re
import sys
import time

from Chess-engine-in-python.engine.board import Board, Color, PieceType
from Chess-engine-in-python.engine.move import Move, MoveGenerator
from Chess-engine-in-python.engine.search import Search

class CLI:
    def __init__(self, board, depth=4, time_limit=5.0):
        self.board = board
        self.depth = depth
        self.time_limit = time_limit
        self.move_generator = MoveGenerator(board)
    
    def run(self):
        """Run the CLI interface"""
        print("Chess Engine CLI")
        print("Type 'help' for a list of commands")
        
        while True:
            print(self.board)
            print(f"{'White' if self.board.active_color == Color.WHITE else 'Black'} to move")
            
            command = input("> ").strip().lower()
            
            if command == "quit" or command == "exit":
                break
            elif command == "help":
                self._print_help()
            elif command == "board":
                print(self.board)
            elif command == "fen":
                print(self.board.to_fen())
            elif command == "moves":
                self._print_legal_moves()
            elif command == "go":
                self._computer_move()
            elif command.startswith("depth "):
                try:
                    self.depth = int(command.split()[1])
                    print(f"Search depth set to {self.depth}")
                except (IndexError, ValueError):
                    print("Invalid depth value")
            elif command.startswith("time "):
                try:
                    self.time_limit = float(command.split()[1])
                    print(f"Search time limit set to {self.time_limit} seconds")
                except (IndexError, ValueError):
                    print("Invalid time value")
            elif command.startswith("position "):
                try:
                    fen = command[9:].strip()
                    self.board = Board(fen)
                    self.move_generator = MoveGenerator(self.board)
                    print("Position set")
                except Exception as e:
                    print(f"Error setting position: {e}")
            elif self._is_move(command):
                self._make_move(command)
            else:
                print("Unknown command")
    
    def _print_help(self):
        """Print help information"""
        print("Available commands:")
        print("  help       - Show this help")
        print("  quit/exit  - Exit the program")
        print("  board      - Display the current board")
        print("  fen        - Display the current position in FEN notation")
        print("  moves      - List all legal moves")
        print("  go         - Let the computer make a move")
        print("  depth N    - Set search depth to N")
        print("  time N     - Set search time limit to N seconds")
        print("  position FEN - Set the board position from FEN string")
        print("  e2e4       - Make a move (in coordinate notation)")
    
    def _print_legal_moves(self):
        """Print all legal moves"""
        legal_moves = self.move_generator.generate_legal_moves()
        if not legal_moves:
            print("No legal moves available")
            return
        
        for i, move in enumerate(legal_moves):
            print(f"{i+1:2d}. {move}", end="  ")
            if (i + 1) % 5 == 0:
                print()
        print()
    
    def _is_move(self, command):
        """Check if the command is a move in coordinate notation"""
        # Match patterns like e2e4, e7e8q, etc.
        return re.match(r'^[a-h][1-8][a-h][1-8][qrbnQRBN]?$', command) is not None
    
    def _make_move(self, move_str):
        """Make a move on the board"""
        # Parse move string
        from_file = ord(move_str[0]) - ord('a')
        from_rank = 8 - int(move_str[1])
        to_file = ord(move_str[2]) - ord('a')
        to_rank = 8 - int(move_str[3])
        
        promotion_piece = None
        if len(move_str) == 5:
            promotion_map = {
                'q': PieceType.QUEEN,
                'r': PieceType.ROOK,
                'b': PieceType.BISHOP,
                'n': PieceType.KNIGHT
            }
            promotion_piece = promotion_map.get(move_str[4].lower())
        
        # Find matching legal move
        legal_moves = self.move_generator.generate_legal_moves()
        matching_move = None
        
        for move in legal_moves:
            if (move.from_square == (from_rank, from_file) and 
                move.to_square == (to_rank, to_file) and 
                move.promotion_piece == promotion_piece):
                matching_move = move
                break
        
        if matching_move:
            self.board = self.board.make_move(matching_move)
            self.move_generator = MoveGenerator(self.board)
            print(f"Move: {move_str}")
        else:
            print("Illegal move")
    
    def _computer_move(self):
        """Let the computer make a move"""
        print("Thinking...")
        start_time = time.time()
        
        search = Search(self.board, self.depth)
        best_move = search.iterative_deepening(self.time_limit)
        
        elapsed = time.time() - start_time
        
        if best_move:
            self.board = self.board.make_move(best_move)
            self.move_generator = MoveGenerator(self.board)
            print(f"Computer move: {best_move} (in {elapsed:.2f}s)")
        else:
            print("No legal moves available")

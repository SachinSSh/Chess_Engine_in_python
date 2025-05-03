from enum import Enum, auto
import copy
from Chess_Engine_in_python.utils.fen import parse_fen, generate_fen

class PieceType(Enum):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()

class Color(Enum):
    WHITE = auto()
    BLACK = auto()

class Piece:
    def __init__(self, piece_type, color):
        self.piece_type = piece_type
        self.color = color
    
    def __str__(self):
        symbols = {
            (PieceType.PAWN, Color.WHITE): 'P',
            (PieceType.KNIGHT, Color.WHITE): 'N',
            (PieceType.BISHOP, Color.WHITE): 'B',
            (PieceType.ROOK, Color.WHITE): 'R',
            (PieceType.QUEEN, Color.WHITE): 'Q',
            (PieceType.KING, Color.WHITE): 'K',
            (PieceType.PAWN, Color.BLACK): 'p',
            (PieceType.KNIGHT, Color.BLACK): 'n',
            (PieceType.BISHOP, Color.BLACK): 'b',
            (PieceType.ROOK, Color.BLACK): 'r',
            (PieceType.QUEEN, Color.BLACK): 'q',
            (PieceType.KING, Color.BLACK): 'k',
        }
        return symbols.get((self.piece_type, self.color), '?')

class Board:
    def __init__(self, fen=None):
        # Initialize an 8x8 board with None (empty squares)
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        
        # Game state
        self.active_color = Color.WHITE
        self.castling_rights = {
            Color.WHITE: {'kingside': True, 'queenside': True},
            Color.BLACK: {'kingside': True, 'queenside': True}
        }
        self.en_passant_target = None  # Square coordinates or None
        self.halfmove_clock = 0  # For 50-move rule
        self.fullmove_number = 1  # Incremented after Black's move
        
        # Initialize from FEN if provided, otherwise use starting position
        if fen:
            self.load_from_fen(fen)
        else:
            self.load_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    def load_from_fen(self, fen):
        """Load board position from FEN string"""
        board_state, active_color, castling, en_passant, halfmove, fullmove = parse_fen(fen)
        
        # Set pieces on the board
        for rank in range(8):
            for file in range(8):
                piece_char = board_state[rank][file]
                if piece_char != '.':
                    self.squares[rank][file] = self._char_to_piece(piece_char)
        
        # Set game state
        self.active_color = Color.WHITE if active_color == 'w' else Color.BLACK
        
        # Set castling rights
        self.castling_rights = {
            Color.WHITE: {'kingside': 'K' in castling, 'queenside': 'Q' in castling},
            Color.BLACK: {'kingside': 'k' in castling, 'queenside': 'q' in castling}
        }
        
        # Set en passant target
        self.en_passant_target = en_passant if en_passant != '-' else None
        
        # Set move counters
        self.halfmove_clock = int(halfmove)
        self.fullmove_number = int(fullmove)
    
    def _char_to_piece(self, char):
        """Convert character to piece object"""
        piece_map = {
            'P': (PieceType.PAWN, Color.WHITE),
            'N': (PieceType.KNIGHT, Color.WHITE),
            'B': (PieceType.BISHOP, Color.WHITE),
            'R': (PieceType.ROOK, Color.WHITE),
            'Q': (PieceType.QUEEN, Color.WHITE),
            'K': (PieceType.KING, Color.WHITE),
            'p': (PieceType.PAWN, Color.BLACK),
            'n': (PieceType.KNIGHT, Color.BLACK),
            'b': (PieceType.BISHOP, Color.BLACK),
            'r': (PieceType.ROOK, Color.BLACK),
            'q': (PieceType.QUEEN, Color.BLACK),
            'k': (PieceType.KING, Color.BLACK),
        }
        if char in piece_map:
            piece_type, color = piece_map[char]
            return Piece(piece_type, color)
        return None
    
    def to_fen(self):
        """Convert current board state to FEN string"""
        return generate_fen(self)
    
    def make_move(self, move):
        """Execute a move on the board and update game state"""
        # Create a copy of the board to avoid modifying the original
        new_board = copy.deepcopy(self)
        
        # Extract move information
        from_rank, from_file = move.from_square
        to_rank, to_file = move.to_square
        
        # Get the piece being moved
        piece = new_board.squares[from_rank][from_file]
        
        # Handle special moves
        if move.is_castling:
            # Implement castling logic
            if to_file > from_file:  # Kingside
                # Move rook
                rook = new_board.squares[from_rank][7]
                new_board.squares[from_rank][5] = rook
                new_board.squares[from_rank][7] = None
            else:  # Queenside
                # Move rook
                rook = new_board.squares[from_rank][0]
                new_board.squares[from_rank][3] = rook
                new_board.squares[from_rank][0] = None
        
        elif move.is_en_passant:
            # Remove the captured pawn
            capture_rank = from_rank
            capture_file = to_file
            new_board.squares[capture_rank][capture_file] = None
        
        # Move the piece
        new_board.squares[to_rank][to_file] = piece
        new_board.squares[from_rank][from_file] = None
        
        # Handle promotion
        if move.promotion_piece:
            new_board.squares[to_rank][to_file] = Piece(move.promotion_piece, piece.color)
        
        # Update castling rights
        if piece.piece_type == PieceType.KING:
            new_board.castling_rights[piece.color]['kingside'] = False
            new_board.castling_rights[piece.color]['queenside'] = False
        
        if piece.piece_type == PieceType.ROOK:
            if from_file == 0:  # Queenside rook
                new_board.castling_rights[piece.color]['queenside'] = False
            elif from_file == 7:  # Kingside rook
                new_board.castling_rights[piece.color]['kingside'] = False
        
        # Update en passant target
        if piece.piece_type == PieceType.PAWN and abs(to_rank - from_rank) == 2:
            # Set en passant target square
            ep_rank = (from_rank + to_rank) // 2
            new_board.en_passant_target = (ep_rank, from_file)
        else:
            new_board.en_passant_target = None
        
        # Update halfmove clock
        if piece.piece_type == PieceType.PAWN or move.is_capture:
            new_board.halfmove_clock = 0
        else:
            new_board.halfmove_clock += 1
        
        # Update fullmove number
        if piece.color == Color.BLACK:
            new_board.fullmove_number += 1
        
        # Switch active color
        new_board.active_color = Color.BLACK if piece.color == Color.WHITE else Color.WHITE
        
        return new_board
    
    def get_piece_at(self, rank, file):
        """Get the piece at the specified square"""
        if 0 <= rank < 8 and 0 <= file < 8:
            return self.squares[rank][file]
        return None
    
    def is_square_attacked(self, rank, file, by_color):
        """Check if a square is attacked by any piece of the specified color"""
        # Implementation will be added
        pass
    
    def __str__(self):
        """String representation of the board"""
        result = ""
        for rank in range(8):
            for file in range(8):
                piece = self.squares[rank][file]
                result += str(piece) if piece else "."
            result += "\n"
        return result

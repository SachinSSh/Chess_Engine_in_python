import random
from Chess-Engine-in-python.engine.board import PieceType, Color

class ZobristHash:
    def __init__(self):
        # Initialize random numbers for each piece at each position
        self.piece_keys = {}
        for piece_type in PieceType:
            for color in Color:
                for rank in range(8):
                    for file in range(8):
                        self.piece_keys[(piece_type, color, rank, file)] = random.getrandbits(64)
        
        # Random numbers for castling rights
        self.castling_keys = {
            (Color.WHITE, 'kingside'): random.getrandbits(64),
            (Color.WHITE, 'queenside'): random.getrandbits(64),
            (Color.BLACK, 'kingside'): random.getrandbits(64),
            (Color.BLACK, 'queenside'): random.getrandbits(64)
        }
        
        # Random numbers for en passant files
        self.en_passant_keys = {}
        for file in range(8):
            self.en_passant_keys[file] = random.getrandbits(64)
        
        # Random number for side to move
        self.side_to_move_key = random.getrandbits(64)
    
    def hash(self, board):
        """Compute Zobrist hash for a board position"""
        h = 0
        
        # Hash pieces
        for rank in range(8):
            for file in range(8):
                piece = board.get_piece_at(rank, file)
                if piece:
                    h ^= self.piece_keys[(piece.piece_type, piece.color, rank, file)]
        
        # Hash castling rights
        for color in Color:
            for side in ['kingside', 'queenside']:
                if board.castling_rights[color][side]:
                    h ^= self.castling_keys[(color, side)]
        
        # Hash en passant target
        if board.en_passant_target:
            ep_rank, ep_file = board.en_passant_target
            h ^= self.en_passant_keys[ep_file]
        
        # Hash side to move
        if board.active_color == Color.BLACK:
            h ^= self.side_to_move_key
        
        return h

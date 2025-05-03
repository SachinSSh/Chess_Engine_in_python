import os
import json
from Chess_Engine_in_python.engine.board import Board, Color, PieceType
from Chess_Engine_in_python.engine.move import MoveGenerator

class Evaluator:
    def __init__(self):
        # Material values
        self.piece_values = {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000  # High value to ensure king safety
        }
        
        # Load piece-square tables
        self.piece_tables = self._load_piece_tables()
    
    def _load_piece_tables(self):
        """Load piece-square tables from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'piece_tables.json')
            with open(data_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Use default tables if file not found or invalid
            return self._default_piece_tables()
    
    def _default_piece_tables(self):
        """Default piece-square tables if file not available"""
        return {
            "pawn": [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [5,  5, 10, 25, 25, 10,  5,  5],
                [0,  0,  0, 20, 20,  0,  0,  0],
                [5, -5,-10,  0,  0,-10, -5,  5],
                [5, 10, 10,-20,-20, 10, 10,  5],
                [0,  0,  0,  0,  0,  0,  0,  0]
            ],
            "knight": [
                [-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 20, 20, 15,  5,-30],
                [-30,  0, 15, 20, 20, 15,  0,-30],
                [-30,  5, 10, 15, 15, 10,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]
            ],
            "bishop": [
                [-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0, 10, 10, 10, 10,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5,  5,  5,  5,  5,-10],
                [-10,  0,  5,  0,  0,  5,  0,-10],
                [-20,-10,-10,-10,-10,-10,-10,-20]
            ],
            "rook": [
                [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [0,  0,  0,  5,  5,  0,  0,  0]
            ],
            "queen": [
                [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]
            ],
            "king_middle": [
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-20,-30,-30,-40,-40,-30,-30,-20],
                [-10,-20,-20,-20,-20,-20,-20,-10],
                [20, 20,  0,  0,  0,  0, 20, 20],
                [20, 30, 10,  0,  0, 10, 30, 20]
            ],
            "king_end": [
                [-50,-40,-30,-20,-20,-30,-40,-50],
                [-30,-20,-10,  0,  0,-10,-20,-30],
                [-30,-10, 20, 30, 30, 20,-10,-30],
                [-30,-10, 30, 40, 40, 30,-10,-30],
                [-30,-10, 30, 40, 40, 30,-10,-30],
                [-30,-10, 20, 30, 30, 20,-10,-30],
                [-30,-20,-10,  0,  0,-10,-20,-30],
                [-50,-40,-30,-20,-20,-30,-40,-50]
            ]
        }
    
    def evaluate(self, board):
        """Evaluate the current board position"""
        # If checkmate, return extreme value
        move_generator = MoveGenerator(board)
        legal_moves = move_generator.generate_legal_moves()
        
        if not legal_moves:
            # Check if king is in check
            king_pos = self._find_king(board, board.active_color)
            if king_pos and board.is_square_attacked(king_pos[0], king_pos[1], 
                                                   Color.BLACK if board.active_color == Color.WHITE else Color.WHITE):
                # Checkmate
                return -10000 if board.active_color == Color.WHITE else 10000
            else:
                # Stalemate
                return 0
        
        # Material evaluation
        material_score = self._evaluate_material(board)
        
        # Piece-square table evaluation
        position_score = self._evaluate_position(board)
        
        # Mobility evaluation (number of legal moves)
        mobility_score = len(legal_moves) * 5  # 5 points per legal move
        
        # Pawn structure evaluation
        pawn_structure_score = self._evaluate_pawn_structure(board)
        
        # King safety
        king_safety_score = self._evaluate_king_safety(board)
        
        # Total score
        total_score = material_score + position_score + mobility_score + pawn_structure_score + king_safety_score
        
        # Return score from white's perspective
        return total_score if board.active_color == Color.WHITE else -total_score
    
    def _evaluate_material(self, board):
        """Evaluate material balance"""
        white_score = 0
        black_score = 0
        
        for rank in range(8):
            for file in range(8):
                piece = board.get_piece_at(rank, file)
                if piece:
                    value = self.piece_values[piece.piece_type]
                    if piece.color == Color.WHITE:
                        white_score += value
                    else:
                        black_score += value
        
        return white_score - black_score
    
    def _evaluate_position(self, board):
        """Evaluate piece positions using piece-square tables"""
        white_score = 0
        black_score = 0
        
        # Determine game phase (middle or endgame)
        total_material = 0
        for rank in range(8):
            for file in range(8):
                piece = board.get_piece_at(rank, file)
                if piece and piece.piece_type != PieceType.KING and piece.piece_type != PieceType.PAWN:
                    total_material += self.piece_values[piece.piece_type]
        
        is_endgame = total_material < 2500  # Threshold for endgame
        
        for rank in range(8):
            for file in range(8):
                piece = board.get_piece_at(rank, file)
                if piece:
                    # Get appropriate piece-square table
                    if piece.piece_type == PieceType.PAWN:
                        table = self.piece_tables["pawn"]
                    elif piece.piece_type == PieceType.KNIGHT:
                        table = self.piece_tables["knight"]
                    elif piece.piece_type == PieceType.BISHOP:
                        table = self.piece_tables["bishop"]
                    elif piece.piece_type == PieceType.ROOK:
                        table = self.piece_tables["rook"]
                    elif piece.piece_type == PieceType.QUEEN:
                        table = self.piece_tables["queen"]
                    elif piece.piece_type == PieceType.KING:
                        table = self.piece_tables["king_end"] if is_endgame else self.piece_tables["king_middle"]
                    else:
                        continue
                    
                    # Get position value
                    if piece.color == Color.WHITE:
                        position_value = table[rank][file]
                        white_score += position_value
                    else:
                        # Flip board for black pieces
                        position_value = table[7 - rank][file]
                        black_score += position_value
        
        return white_score - black_score
    
    def _evaluate_pawn_structure(self, board):
        """Evaluate pawn structure (doubled, isolated, passed pawns)"""
        white_score = 0
        black_score = 0
        
        # Count pawns in each file
        white_pawns_in_file = [0] * 8
        black_pawns_in_file = [0] * 8
        
        for rank in range(8):
            for file in range(8):
                piece = board.get_piece_at(rank, file)
                if piece and piece.piece_type == PieceType.PAWN:
                    if piece.color == Color.WHITE:
                        white_pawns_in_file[file] += 1
                    else:
                        black_pawns_in_file[file] += 1
        
        # Evaluate doubled pawns (penalty)
        for file in range(8):
            if white_pawns_in_file[file] > 1:
                white_score -= 20 * (white_pawns_in_file[file] - 1)
            if black_pawns_in_file[file] > 1:
                black_score -= 20 * (black_pawns_in_file[file] - 1)
        
        # Evaluate isolated pawns (penalty)
        for file in range(8):
            if white_pawns_in_file[file] > 0:
                is_isolated = True
                if file > 0 and white_pawns_in_file[file - 1] > 0:
                    is_isolated = False
                if file < 7 and white_pawns_in_file[file + 1] > 0:
                    is_isolated = False
                
                if is_isolated:
                    white_score -= 10
            
            if black_pawns_in_file[file] > 0:
                is_isolated = True
                if file > 0 and black_pawns_in_file[file - 1] > 0:
                    is_isolated = False
                if file < 7 and black_pawns_in_file[file + 1] > 0:
                    is_isolated = False
                
                if is_isolated:
                    black_score -= 10
        
        # Evaluate passed pawns (bonus)
        for file in range(8):
            # Find the most advanced white pawn in this file
            white_pawn_rank = -1
            for rank in range(7, -1, -1):
                piece = board.get_piece_at(rank, file)
                if piece and piece.piece_type == PieceType.PAWN and piece.color == Color.WHITE:
                    white_pawn_rank = rank
                    break
            
            # Check if it's a passed pawn
            if white_pawn_rank != -1:
                is_passed = True
                # Check if any black pawn can block or capture
                for check_file in range(max(0, file - 1), min(8, file + 2)):
                    for check_rank in range(white_pawn_rank - 1, -1, -1):
                        piece = board.get_piece_at(check_rank, check_file)
                        if piece and piece.piece_type == PieceType.PAWN and piece.color == Color.BLACK:
                            is_passed = False
                            break
                
                if is_passed:
                    # Bonus increases as pawn advances
                    white_score += (7 - white_pawn_rank) * 10
            
            # Find the most advanced black pawn in this file
            black_pawn_rank = -1
            for rank in range(8):
                piece = board.get_piece_at(rank, file)
                if piece and piece.piece_type == PieceType.PAWN and piece.color == Color.BLACK:
                    black_pawn_rank = rank
                    break
            
            # Check if it's a passed pawn
            if black_pawn_rank != -1:
                is_passed = True
                # Check if any white pawn can block or capture
                for check_file in range(max(0, file - 1), min(8, file + 2)):
                    for check_rank in range(black_pawn_rank + 1, 8):
                        piece = board.get_piece_at(check_rank, check_file)
                        if piece and piece.piece_type == PieceType.PAWN and piece.color == Color.WHITE:
                            is_passed = False
                            break
                
                if is_passed:
                    # Bonus increases as pawn advances
                    black_score += black_pawn_rank * 10
        
        return white_score - black_score
    
    def _evaluate_king_safety(self, board):
        """Evaluate king safety"""
        white_score = 0
        black_score = 0
        
        # Find kings
        white_king_pos = self._find_king(board, Color.WHITE)
        black_king_pos = self._find_king(board, Color.BLACK)
        
        if white_king_pos:
            # Count defenders around white king
            white_defenders = self._count_defenders(board, white_king_pos, Color.WHITE)
            white_score += white_defenders * 5
            
            # Penalize exposed king
            white_king_rank, white_king_file = white_king_pos
            if white_king_rank < 6:  # King has moved away from back rank
                white_score -= 20
        
        if black_king_pos:
            # Count defenders around black king
            black_defenders = self._count_defenders(board, black_king_pos, Color.BLACK)
            black_score += black_defenders * 5
            
            # Penalize exposed king
            black_king_rank, black_king_file = black_king_pos
            if black_king_rank > 1:  # King has moved away from back rank
                black_score -= 20
        
        return white_score - black_score
    
    def _find_king(self, board, color):
        """Find the position of a king"""
        for rank in range(8):
            for file in range(8):
                piece = board.get_piece_at(rank, file)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return (rank, file)
        return None
    
    def _count_defenders(self, board, position, color):
        """Count friendly pieces defending the area around a position"""
        rank, file = position
        defenders = 0
        
        for r in range(max(0, rank - 1), min(8, rank + 2)):
            for f in range(max(0, file - 1), min(8, file + 2)):
                if r == rank and f == file:
                    continue  # Skip the position itself
                
                piece = board.get_piece_at(r, f)
                if piece and piece.color == color:
                    defenders += 1
        
        return defenders

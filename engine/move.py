from chess-engine-in-python.engine.board import PieceType, Color

class Move:
    def __init__(self, from_square, to_square, is_capture=False, is_castling=False, 
                 is_en_passant=False, promotion_piece=None):
        self.from_square = from_square  # (rank, file) tuple
        self.to_square = to_square      # (rank, file) tuple
        self.is_capture = is_capture
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
        self.promotion_piece = promotion_piece  # PieceType or None
    
    def __str__(self):
        """Convert move to algebraic notation"""
        files = 'abcdefgh'
        ranks = '87654321'
        
        from_file, from_rank = files[self.from_square[1]], ranks[self.from_square[0]]
        to_file, to_rank = files[self.to_square[1]], ranks[self.to_square[0]]
        
        move_str = f"{from_file}{from_rank}{to_file}{to_rank}"
        
        if self.promotion_piece:
            promotion_symbols = {
                PieceType.KNIGHT: 'n',
                PieceType.BISHOP: 'b',
                PieceType.ROOK: 'r',
                PieceType.QUEEN: 'q'
            }
            move_str += promotion_symbols.get(self.promotion_piece, '')
        
        return move_str

class MoveGenerator:
    def __init__(self, board):
        self.board = board
    
    def generate_legal_moves(self):
        """Generate all legal moves for the active color"""
        legal_moves = []
        
        for rank in range(8):
            for file in range(8):
                piece = self.board.get_piece_at(rank, file)
                
                if piece and piece.color == self.board.active_color:
                    # Generate moves for this piece
                    piece_moves = self._generate_piece_moves(rank, file, piece)
                    legal_moves.extend(piece_moves)
        
        return legal_moves
    
    def _generate_piece_moves(self, rank, file, piece):
        """Generate all possible moves for a specific piece"""
        if piece.piece_type == PieceType.PAWN:
            return self._generate_pawn_moves(rank, file, piece.color)
        elif piece.piece_type == PieceType.KNIGHT:
            return self._generate_knight_moves(rank, file, piece.color)
        elif piece.piece_type == PieceType.BISHOP:
            return self._generate_bishop_moves(rank, file, piece.color)
        elif piece.piece_type == PieceType.ROOK:
            return self._generate_rook_moves(rank, file, piece.color)
        elif piece.piece_type == PieceType.QUEEN:
            return self._generate_queen_moves(rank, file, piece.color)
        elif piece.piece_type == PieceType.KING:
            return self._generate_king_moves(rank, file, piece.color)
        
        return []
    
    def _generate_pawn_moves(self, rank, file, color):
        """Generate all possible pawn moves"""
        moves = []
        direction = -1 if color == Color.WHITE else 1
        
        # Single push
        new_rank = rank + direction
        if 0 <= new_rank < 8 and not self.board.get_piece_at(new_rank, file):
            # Check for promotion
            if new_rank == 0 or new_rank == 7:
                for promotion_piece in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                    moves.append(Move((rank, file), (new_rank, file), promotion_piece=promotion_piece))
            else:
                moves.append(Move((rank, file), (new_rank, file)))
            
            # Double push from starting position
            if (color == Color.WHITE and rank == 6) or (color == Color.BLACK and rank == 1):
                new_rank = rank + 2 * direction
                if 0 <= new_rank < 8 and not self.board.get_piece_at(new_rank, file) and not self.board.get_piece_at(rank + direction, file):
                    moves.append(Move((rank, file), (new_rank, file)))
        
        # Captures
        for file_offset in [-1, 1]:
            new_file = file + file_offset
            if 0 <= new_file < 8:
                # Regular capture
                new_rank = rank + direction
                if 0 <= new_rank < 8:
                    target_piece = self.board.get_piece_at(new_rank, new_file)
                    if target_piece and target_piece.color != color:
                        # Check for promotion
                        if new_rank == 0 or new_rank == 7:
                            for promotion_piece in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                                moves.append(Move((rank, file), (new_rank, new_file), is_capture=True, promotion_piece=promotion_piece))
                        else:
                            moves.append(Move((rank, file), (new_rank, new_file), is_capture=True))
                
                # En passant capture
                if self.board.en_passant_target:
                    ep_rank, ep_file = self.board.en_passant_target
                    if ep_rank == rank + direction and ep_file == new_file:
                        moves.append(Move((rank, file), (ep_rank, ep_file), is_capture=True, is_en_passant=True))
        
        return moves
    
    def _generate_knight_moves(self, rank, file, color):
        """Generate all possible knight moves"""
        moves = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for rank_offset, file_offset in offsets:
            new_rank, new_file = rank + rank_offset, file + file_offset
            
            if 0 <= new_rank < 8 and 0 <= new_file < 8:
                target_piece = self.board.get_piece_at(new_rank, new_file)
                
                if not target_piece:
                    # Empty square
                    moves.append(Move((rank, file), (new_rank, new_file)))
                elif target_piece.color != color:
                    # Capture
                    moves.append(Move((rank, file), (new_rank, new_file), is_capture=True))
        
        return moves
    
    def _generate_sliding_moves(self, rank, file, color, directions):
        """Generate sliding moves (bishop, rook, queen)"""
        moves = []
        
        for rank_dir, file_dir in directions:
            for distance in range(1, 8):
                new_rank = rank + rank_dir * distance
                new_file = file + file_dir * distance
                
                if not (0 <= new_rank < 8 and 0 <= new_file < 8):
                    # Out of bounds
                    break
                
                target_piece = self.board.get_piece_at(new_rank, new_file)
                
                if not target_piece:
                    # Empty square
                    moves.append(Move((rank, file), (new_rank, new_file)))
                elif target_piece.color != color:
                    # Capture
                    moves.append(Move((rank, file), (new_rank, new_file), is_capture=True))
                    break
                else:
                    # Blocked by own piece
                    break
        
        return moves
    
    def _generate_bishop_moves(self, rank, file, color):
        """Generate all possible bishop moves"""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonals
        return self._generate_sliding_moves(rank, file, color, directions)
    
    def _generate_rook_moves(self, rank, file, color):
        """Generate all possible rook moves"""
        directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]  # Horizontals and verticals
        return self._generate_sliding_moves(rank, file, color, directions)
    
    def _generate_queen_moves(self, rank, file, color):
        """Generate all possible queen moves"""
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]  # All directions
        return self._generate_sliding_moves(rank, file, color, directions)
    
    def _generate_king_moves(self, rank, file, color):
        """Generate all possible king moves"""
        moves = []
        
        # Regular king moves
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        
        for rank_dir, file_dir in directions:
            new_rank, new_file = rank + rank_dir, file + file_dir
            
            if 0 <= new_rank < 8 and 0 <= new_file < 8:
                target_piece = self.board.get_piece_at(new_rank, new_file)
                
                if not target_piece:
                    # Empty square
                    moves.append(Move((rank, file), (new_rank, new_file)))
                elif target_piece.color != color:
                    # Capture
                    moves.append(Move((rank, file), (new_rank, new_file), is_capture=True))
        
        # Castling
        if self.board.castling_rights[color]['kingside']:
            if self._can_castle_kingside(rank, file, color):
                moves.append(Move((rank, file), (rank, file + 2), is_castling=True))
        
        if self.board.castling_rights[color]['queenside']:
            if self._can_castle_queenside(rank, file, color):
                moves.append(Move((rank, file), (rank, file - 2), is_castling=True))
        
        return moves
    
    def _can_castle_kingside(self, rank, file, color):
        """Check if kingside castling is possible"""
        # Check if squares between king and rook are empty
        for f in range(file + 1, 7):
            if self.board.get_piece_at(rank, f):
                return False
        
        # Check if king or squares it moves through are in check
        for f in range(file, file + 3):
            if self.board.is_square_attacked(rank, f, Color.BLACK if color == Color.WHITE else Color.WHITE):
                return False
        
        return True
    
    def _can_castle_queenside(self, rank, file, color):
        """Check if queenside castling is possible"""
        # Check if squares between king and rook are empty
        for f in range(1, file):
            if self.board.get_piece_at(rank, f):
                return False
        
        # Check if king or squares it moves through are in check
        for f in range(file - 2, file + 1):
            if self.board.is_square_attacked(rank, f, Color.BLACK if color == Color.WHITE else Color.WHITE):
                return False
        
        return True
    
    def is_move_legal(self, move):
        """Check if a move is legal"""
        # Implementation will be added
        pass

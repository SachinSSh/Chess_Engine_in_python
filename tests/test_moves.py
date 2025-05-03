import unittest
from Chess_Engine_in_python.engine.board import Board, PieceType, Color
from Chess_Engine_in_python.engine.move import Move, MoveGenerator

class TestMoves(unittest.TestCase):
    def test_pawn_moves(self):
        """Test pawn move generation"""
        # Initial position
        board = Board()
        move_generator = MoveGenerator(board)
        
        # Get all pawn moves for white
        pawn_moves = []
        for file in range(8):
            piece = board.get_piece_at(6, file)
            if piece and piece.piece_type == PieceType.PAWN:
                pawn_moves.extend(move_generator._generate_pawn_moves(6, file, Color.WHITE))
        
        # Should have 16 moves (8 pawns can each move 1 or 2 squares)
        self.assertEqual(len(pawn_moves), 16)
        
        # Test blocked pawn
        board = Board("rnbqkbnr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the pawn at a3
        pawn_moves = move_generator._generate_pawn_moves(5, 0, Color.WHITE)
        
        # Should have 1 move (can only move 1 square forward)
        self.assertEqual(len(pawn_moves), 1)
        
        # Test pawn captures
        board = Board("rnbqkbnr/ppp1p1pp/8/3p1p2/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the pawn at e4
        pawn_moves = move_generator._generate_pawn_moves(4, 4, Color.WHITE)
        
        # Should have 3 moves (forward, capture left, capture right)
        self.assertEqual(len(pawn_moves), 3)
        
        # Test en passant
        board = Board("rnbqkbnr/ppp2ppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the pawn at e5
        pawn_moves = move_generator._generate_pawn_moves(3, 4, Color.WHITE)
        
        # Should have 2 moves (forward and en passant capture)
        self.assertEqual(len(pawn_moves), 2)
        
        # Check that one of the moves is an en passant capture
        en_passant_moves = [move for move in pawn_moves if move.is_en_passant]
        self.assertEqual(len(en_passant_moves), 1)
        
        # Test promotion
        board = Board("8/P7/8/8/8/8/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the pawn at a7
        pawn_moves = move_generator._generate_pawn_moves(1, 0, Color.WHITE)
        
        # Should have 4 moves (promotion to Q, R, B, N)
        self.assertEqual(len(pawn_moves), 4)
        
        # Check that all moves are promotions
        promotion_types = [move.promotion_piece for move in pawn_moves]
        self.assertIn(PieceType.QUEEN, promotion_types)
        self.assertIn(PieceType.ROOK, promotion_types)
        self.assertIn(PieceType.BISHOP, promotion_types)
        self.assertIn(PieceType.KNIGHT, promotion_types)
    
    def test_knight_moves(self):
        """Test knight move generation"""
        # Initial position
        board = Board()
        move_generator = MoveGenerator(board)
        
        # Get moves for the knight at b1
        knight_moves = move_generator._generate_knight_moves(7, 1, Color.WHITE)
        
        # Should have 2 moves (a3, c3)
        self.assertEqual(len(knight_moves), 2)
        
        # Test knight in the center
        board = Board("8/8/8/8/4N3/8/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the knight at e4
        knight_moves = move_generator._generate_knight_moves(4, 4, Color.WHITE)
        
        # Should have 8 moves
        self.assertEqual(len(knight_moves), 8)
        
        # Test knight with captures
        board = Board("8/8/3p1p2/8/4N3/8/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the knight at e4
        knight_moves = move_generator._generate_knight_moves(4, 4, Color.WHITE)
        
        # Should have 8 moves, 2 of which are captures
        self.assertEqual(len(knight_moves), 8)
        captures = [move for move in knight_moves if move.is_capture]
        self.assertEqual(len(captures), 2)
    
    def test_bishop_moves(self):
        """Test bishop move generation"""
        # Bishop in the center
        board = Board("8/8/8/8/4B3/8/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the bishop at e4
        bishop_moves = move_generator._generate_bishop_moves(4, 4, Color.WHITE)
        
        # Should have 13 moves (diagonals in all directions)
        self.assertEqual(len(bishop_moves), 13)
        
        # Test bishop with obstacles
        board = Board("8/8/2P5/8/4B3/6p1/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the bishop at e4
        bishop_moves = move_generator._generate_bishop_moves(4, 4, Color.WHITE)
        
        # Should have 9 moves (some diagonals blocked)
        self.assertEqual(len(bishop_moves), 9)
        
        # Should have 1 capture
        captures = [move for move in bishop_moves if move.is_capture]
        self.assertEqual(len(captures), 1)
    
    def test_rook_moves(self):
        """Test rook move generation"""
        # Rook in the center
        board = Board("8/8/8/8/4R3/8/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the rook at e4
        rook_moves = move_generator._generate_rook_moves(4, 4, Color.WHITE)
        
        # Should have 14 moves (horizontals and verticals)
        self.assertEqual(len(rook_moves), 14)
        
        # Test rook with obstacles
        board = Board("8/8/4P3/8/4R3/8/4p3/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the rook at e4
        rook_moves = move_generator._generate_rook_moves(4, 4, Color.WHITE)
        
        # Should have 10 moves (some directions blocked)
        self.assertEqual(len(rook_moves), 10)
        
        # Should have 1 capture
        captures = [move for move in rook_moves if move.is_capture]
        self.assertEqual(len(captures), 1)
    
    def test_queen_moves(self):
        """Test queen move generation"""
        # Queen in the center
        board = Board("8/8/8/8/4Q3/8/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the queen at e4
        queen_moves = move_generator._generate_queen_moves(4, 4, Color.WHITE)
        
        # Should have 27 moves (horizontals, verticals, and diagonals)
        self.assertEqual(len(queen_moves), 27)
    
    def test_king_moves(self):
        """Test king move generation"""
        # King in the center
        board = Board("8/8/8/8/4K3/8/8/8 w - - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the king at e4
        king_moves = move_generator._generate_king_moves(4, 4, Color.WHITE)
        
        # Should have 8 moves (all surrounding squares)
        self.assertEqual(len(king_moves), 8)
        
        # Test castling
        board = Board("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
        move_generator = MoveGenerator(board)
        
        # Get moves for the king at e1
        king_moves = move_generator._generate_king_moves(7, 4, Color.WHITE)
        
        # Should have 7 moves (5 regular moves + 2 castling)
        self.assertEqual(len(king_moves), 7)
        
        # Check that two of the moves are castling
        castling_moves = [move for move in king_moves if move.is_castling]
        self.assertEqual(len(castling_moves), 2)
    
    def test_legal_moves(self):
        """Test legal move generation"""
        # Initial position
        board = Board()
        move_generator = MoveGenerator(board)
        
        legal_moves = move_generator.generate_legal_moves()
        
        # Should have 20 legal moves in the initial position
        self.assertEqual(len(legal_moves), 20)
        
        # Test position with check
        board = Board("rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1")
        move_generator = MoveGenerator(board)
        
        legal_moves = move_generator.generate_legal_moves()
        
        # Should have specific number of legal moves
        self.assertTrue(len(legal_moves) > 0)
        
        # Test checkmate position
        board = Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1")
        move_generator = MoveGenerator(board)
        
        legal_moves = move_generator.generate_legal_moves()
        
        # Should have 0 legal moves in checkmate
        self.assertEqual(len(legal_moves), 0)

if __name__ == "__main__":
    unittest.main()

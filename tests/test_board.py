import unittest
from Chess-engine-in-python.engine.board import Board, PieceType, Color, Piece

class TestBoard(unittest.TestCase):
    def test_initial_position(self):
        """Test that the initial position is set up correctly"""
        board = Board()
        
        # Check white pieces
        self.assertEqual(board.get_piece_at(7, 0).piece_type, PieceType.ROOK)
        self.assertEqual(board.get_piece_at(7, 1).piece_type, PieceType.KNIGHT)
        self.assertEqual(board.get_piece_at(7, 2).piece_type, PieceType.BISHOP)
        self.assertEqual(board.get_piece_at(7, 3).piece_type, PieceType.QUEEN)
        self.assertEqual(board.get_piece_at(7, 4).piece_type, PieceType.KING)
        self.assertEqual(board.get_piece_at(7, 5).piece_type, PieceType.BISHOP)
        self.assertEqual(board.get_piece_at(7, 6).piece_type, PieceType.KNIGHT)
        self.assertEqual(board.get_piece_at(7, 7).piece_type, PieceType.ROOK)
        
        for file in range(8):
            self.assertEqual(board.get_piece_at(6, file).piece_type, PieceType.PAWN)
            self.assertEqual(board.get_piece_at(6, file).color, Color.WHITE)
        
        # Check black pieces
        self.assertEqual(board.get_piece_at(0, 0).piece_type, PieceType.ROOK)
        self.assertEqual(board.get_piece_at(0, 1).piece_type, PieceType.KNIGHT)
        self.assertEqual(board.get_piece_at(0, 2).piece_type, PieceType.BISHOP)
        self.assertEqual(board.get_piece_at(0, 3).piece_type, PieceType.QUEEN)
        self.assertEqual(board.get_piece_at(0, 4).piece_type, PieceType.KING)
        self.assertEqual(board.get_piece_at(0, 5).piece_type, PieceType.BISHOP)
        self.assertEqual(board.get_piece_at(0, 6).piece_type, PieceType.KNIGHT)
        self.assertEqual(board.get_piece_at(0, 7).piece_type, PieceType.ROOK)
        
        for file in range(8):
            self.assertEqual(board.get_piece_at(1, file).piece_type, PieceType.PAWN)
            self.assertEqual(board.get_piece_at(1, file).color, Color.BLACK)
        
        # Check empty squares
        for rank in range(2, 6):
            for file in range(8):
                self.assertIsNone(board.get_piece_at(rank, file))
        
        # Check game state
        self.assertEqual(board.active_color, Color.WHITE)
        self.assertTrue(board.castling_rights[Color.WHITE]['kingside'])
        self.assertTrue(board.castling_rights[Color.WHITE]['queenside'])
        self.assertTrue(board.castling_rights[Color.BLACK]['kingside'])
        self.assertTrue(board.castling_rights[Color.BLACK]['queenside'])
        self.assertIsNone(board.en_passant_target)
        self.assertEqual(board.halfmove_clock, 0)
        self.assertEqual(board.fullmove_number, 1)
    
    def test_fen_parsing(self):
        """Test FEN string parsing"""
        fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"
        board = Board(fen)
        
        # Check a few key pieces
        self.assertEqual(board.get_piece_at(0, 0).piece_type, PieceType.ROOK)
        self.assertEqual(board.get_piece_at(0, 0).color, Color.BLACK)
        
        self.assertEqual(board.get_piece_at(2, 2).piece_type, PieceType.KNIGHT)
        self.assertEqual(board.get_piece_at(2, 2).color, Color.BLACK)
        
        self.assertEqual(board.get_piece_at(4, 4).piece_type, PieceType.PAWN)
        self.assertEqual(board.get_piece_at(4, 4).color, Color.WHITE)
        
        self.assertEqual(board.get_piece_at(5, 5).piece_type, PieceType.KNIGHT)
        self.assertEqual(board.get_piece_at(5, 5).color, Color.WHITE)
        
        # Check game state
        self.assertEqual(board.active_color, Color.WHITE)
        self.assertTrue(board.castling_rights[Color.WHITE]['kingside'])
        self.assertTrue(board.castling_rights[Color.WHITE]['queenside'])
        self.assertTrue(board.castling_rights[Color.BLACK]['kingside'])
        self.assertTrue(board.castling_rights[Color.BLACK]['queenside'])
        self.assertIsNone(board.en_passant_target)
        self.assertEqual(board.halfmove_clock, 0)
        self.assertEqual(board.fullmove_number, 3)
    
    def test_make_move(self):
        """Test making moves on the board"""
        board = Board()
        
        # Test pawn move
        from chess_engine.engine.move import Move
        move = Move((6, 4), (4, 4))  # e2-e4
        new_board = board.make_move(move)
        
        # Check that the pawn moved
        self.assertIsNone(new_board.get_piece_at(6, 4))
        self.assertEqual(new_board.get_piece_at(4, 4).piece_type, PieceType.PAWN)
        self.assertEqual(new_board.get_piece_at(4, 4).color, Color.WHITE)
        
        # Check that the turn changed
        self.assertEqual(new_board.active_color, Color.BLACK)
        
        # Check en passant target
        self.assertEqual(new_board.en_passant_target, (5, 4))
        
        # Test capture
        move = Move((1, 3), (2, 3))  # d7-d6
        new_board = new_board.make_move(move)
        move = Move((4, 4), (3, 3), is_capture=True)  # e4-d5 capture
        new_board = new_board.make_move(move)
        
        # Check that the capture happened
        self.assertIsNone(new_board.get_piece_at(4, 4))
        self.assertEqual(new_board.get_piece_at(3, 3).piece_type, PieceType.PAWN)
        self.assertEqual(new_board.get_piece_at(3, 3).color, Color.WHITE)
        
        # Test castling
        board = Board("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
        move = Move((7, 4), (7, 6), is_castling=True)  # White kingside castle
        new_board = board.make_move(move)
        
        # Check that the king and rook moved
        self.assertIsNone(new_board.get_piece_at(7, 4))
        self.assertIsNone(new_board.get_piece_at(7, 7))
        self.assertEqual(new_board.get_piece_at(7, 6).piece_type, PieceType.KING)
        self.assertEqual(new_board.get_piece_at(7, 5).piece_type, PieceType.ROOK)
        
        # Check castling rights
        self.assertFalse(new_board.castling_rights[Color.WHITE]['kingside'])
        self.assertFalse(new_board.castling_rights[Color.WHITE]['queenside'])
        
        # Test en passant capture
        board = Board("rnbqkbnr/ppp2ppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
        move = Move((4, 4), (3, 3), is_capture=True, is_en_passant=True)  # e5xd6 e.p.
        new_board = board.make_move(move)
        
        # Check that the en passant capture happened
        self.assertIsNone(new_board.get_piece_at(4, 4))
        self.assertIsNone(new_board.get_piece_at(4, 3))  # Captured pawn
        self.assertEqual(new_board.get_piece_at(3, 3).piece_type, PieceType.PAWN)
        self.assertEqual(new_board.get_piece_at(3, 3).color, Color.WHITE)

if __name__ == "__main__":
    unittest.main()

import unittest
from Chess_Engine_in_python.engine.board import Board
from Chess_Engine_in_python.engine.evaluation import Evaluator

class TestEvaluation(unittest.TestCase):
    def test_material_evaluation(self):
        """Test material evaluation"""
        evaluator = Evaluator()
        
        # Equal material
        board = Board()
        material_score = evaluator._evaluate_material(board)
        self.assertEqual(material_score, 0)
        
        # White advantage
        board = Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
        material_score = evaluator._evaluate_material(board)
        self.assertEqual(material_score, 0)  # Still equal
        
        # White up a pawn
        board = Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPPQPPP/RNB1KBNR w KQkq - 0 1")
        material_score = evaluator._evaluate_material(board)
        self.assertEqual(material_score, 100)  # White up a pawn (100 centipawns)
        
        # Black up a knight
        board = Board("rnbqkb1r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        material_score = evaluator._evaluate_material(board)
        self.assertEqual(material_score, -320)  # Black up a knight (-320 centipawns)
    
    def test_position_evaluation(self):
        """Test position evaluation"""
        evaluator = Evaluator()
        
        # Initial position
        board = Board()
        position_score = evaluator._evaluate_position(board)
        
        # Position score should be close to 0 in initial position
        self.assertTrue(abs(position_score) < 50)
        
        # Test position with better piece placement
        board = Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1")
        position_score = evaluator._evaluate_position(board)
        
        # White's knight is better placed than in the initial position
        self.assertTrue(position_score > 0)
    
    def test_pawn_structure_evaluation(self):
        """Test pawn structure evaluation"""
        evaluator = Evaluator()
        
        # Initial position
        board = Board()
        pawn_structure_score = evaluator._evaluate_pawn_structure(board)
        
        # Pawn structure score should be 0 in initial position
        self.assertEqual(pawn_structure_score, 0)
        
        # Test position with doubled pawns for white
        board = Board("rnbqkbnr/pppppppp/8/8/8/P7/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        pawn_structure_score = evaluator._evaluate_pawn_structure(board)
        
        # White has doubled pawns, should be negative
        self.assertTrue(pawn_structure_score < 0)
        
        # Test position with isolated pawn for black
        board = Board("rnbqkbnr/p1p1pppp/8/1p1p4/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        pawn_structure_score = evaluator._evaluate_pawn_structure(board)
        
        # Black has isolated pawns, should be positive for white
        self.assertTrue(pawn_structure_score > 0)
        
        # Test position with passed pawn for white
        board = Board("rnbqkbnr/ppp1pppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1")
        pawn_structure_score = evaluator._evaluate_pawn_structure(board)
        
        # White has a potential passed pawn, should be positive
        self.assertTrue(pawn_structure_score > 0)
    
    def test_king_safety_evaluation(self):
        """Test king safety evaluation"""
        evaluator = Evaluator()
        
        # Initial position
        board = Board()
        king_safety_score = evaluator._evaluate_king_safety(board)
        
        # King safety score should be 0 in initial position (both kings equally safe)
        self.assertEqual(king_safety_score, 0)
        
        # Test position with exposed white king
        board = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1")
        king_safety_score = evaluator._evaluate_king_safety(board)
        
        # White king has fewer defenders, should be negative
        self.assertTrue(king_safety_score < 0)
    
    def test_full_evaluation(self):
        """Test full board evaluation"""
        evaluator = Evaluator()
        
        # Initial position
        board = Board()
        score = evaluator.evaluate(board)
        
        # Score should be close to 0 in initial position
        self.assertTrue(abs(score) < 100)
        
        # Test position with advantage for white
        board = Board("rnbqkb1r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        score = evaluator.evaluate(board)
        
        # White is up a knight, should be positive
        self.assertTrue(score > 300)
        
        # Test position with advantage for black
        board = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKB1R b KQkq - 0 1")
        score = evaluator.evaluate(board)
        
        # Black is up a knight, should be negative
        self.assertTrue(score < -300)

if __name__ == "__main__":
    unittest.main()

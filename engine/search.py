

import time
from Chess-Engine-in-python.engine.evaluation import Evaluator
from Chess-Engine-in-python.engine.move import MoveGenerator

class Search:
    def __init__(self, board, max_depth=4):
        self.board = board
        self.max_depth = max_depth
        self.evaluator = Evaluator()
        self.nodes_count = 0
        self.transposition_table = {}
        
    def iterative_deepening(self, time_limit):
        """Perform iterative deepening search up to max_depth or time limit"""
        start_time = time.time()
        best_move = None
        
        for depth in range(1, self.max_depth + 1):
            self.nodes_count = 0
            score, move = self.alpha_beta(self.board, depth, float('-inf'), float('inf'), True)
            
            if move:
                best_move = move
                
                # Print info about the search
                move_str = f"{chr(move.from_square[1] + 97)}{8 - move.from_square[0]}{chr(move.to_square[1] + 97)}{8 - move.to_square[0]}"
                elapsed = time.time() - start_time
                print(f"Depth {depth}: Best move {move_str}, Score {score}, Nodes {self.nodes_count}, Time {elapsed:.2f}s")
            
            # Check if time limit reached - use a more aggressive cutoff
            if time.time() - start_time >= time_limit * 0.8:
                break
                
        return best_move
    
    def alpha_beta(self, board, depth, alpha, beta, maximizing_player):
        """Alpha-beta pruning search algorithm with optimizations for speed"""
        self.nodes_count += 1
        
        # Check transposition table for previously computed positions
        board_hash = hash(str(board))
        if board_hash in self.transposition_table and self.transposition_table[board_hash]['depth'] >= depth:
            return self.transposition_table[board_hash]['score'], self.transposition_table[board_hash]['move']
        
        # Check for immediate check resolution if in check
        move_generator = MoveGenerator(board)
        legal_moves = move_generator.generate_legal_moves()
        
        # Check for game end
        if not legal_moves:
            # Check if king is in check (checkmate)
            king_pos = self._find_king(board)
            if king_pos and board.is_square_attacked(king_pos[0], king_pos[1], 
                                                  not board.active_color):
                return -20000 if maximizing_player else 20000, None
            else:
                # Stalemate
                return 0, None
        
        # Base case: leaf node
        if depth == 0:
            return self.evaluator.evaluate(board), None
        
        # Prioritize moves that get out of check
        king_pos = self._find_king(board)
        in_check = king_pos and board.is_square_attacked(king_pos[0], king_pos[1], not board.active_color)
        
        # Order moves to improve pruning
        ordered_moves = self._order_moves(board, legal_moves, in_check)
        
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for move in ordered_moves:
                new_board = board.make_move(move)
                eval_score, _ = self.alpha_beta(new_board, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            # Store in transposition table
            self.transposition_table[board_hash] = {'depth': depth, 'score': max_eval, 'move': best_move}
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                new_board = board.make_move(move)
                eval_score, _ = self.alpha_beta(new_board, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            # Store in transposition table
            self.transposition_table[board_hash] = {'depth': depth, 'score': min_eval, 'move': best_move}
            return min_eval, best_move
    
    def _order_moves(self, board, moves, in_check):
        """Order moves to improve pruning efficiency with focus on check resolution"""
        move_scores = []
        
        for move in moves:
            score = 0
            
            # If in check, prioritize moves that get out of check
            if in_check:
                score += 10000
                
            # Prioritize captures by piece value
            if move.is_capture:
                victim = board.get_piece_at(*move.to_square)
                if victim:
                    score += 100 * self.evaluator.piece_values.get(victim.piece_type, 0)
            
            # Prioritize promotions
            if hasattr(move, 'promotion_piece') and move.promotion_piece:
                score += 900
            
            # Prioritize center control for pawns and knights in opening
            if board.get_piece_at(*move.from_square):
                piece_type = board.get_piece_at(*move.from_square).piece_type
                if piece_type == 1:  # Pawn
                    # Center control for pawns
                    if 2 <= move.to_square[0] <= 5 and 2 <= move.to_square[1] <= 5:
                        score += 50
                elif piece_type == 2:  # Knight
                    # Knights to the center
                    if 2 <= move.to_square[0] <= 5 and 2 <= move.to_square[1] <= 5:
                        score += 30
            
            move_scores.append((move, score))
        
        # Sort moves by score in descending order
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]
    
    def _find_king(self, board):
        """Find the king position for the active player"""
        for rank in range(8):
            for file in range(8):
                piece = board.get_piece_at(rank, file)
                if piece and piece.piece_type == 6 and piece.color == board.active_color:
                    return (rank, file)
        return None

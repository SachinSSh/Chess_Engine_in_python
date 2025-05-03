from chess-engine-in-python.utils.zobrist import ZobristHash

class TranspositionTable:
    def __init__(self, size=1000000):
        self.size = size
        self.table = {}
        self.zobrist = ZobristHash()
    
    def store(self, board, depth, score, best_move):
        """Store a position in the transposition table"""
        key = self.zobrist.hash(board)
        
        # Limit table size
        if len(self.table) >= self.size:
            # Simple strategy: clear the table when it gets too large
            self.table.clear()
        
        self.table[key] = {
            'depth': depth,
            'score': score,
            'best_move': best_move
        }
    
    def get(self, board):
        """Retrieve a position from the transposition table"""
        key = self.zobrist.hash(board)
        return self.table.get(key)

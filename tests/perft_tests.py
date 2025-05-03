from Chess-engine-in-python.engine.board import Board
from Chess-engine-in-python.engine.move import MoveGenerator

def perft(board, depth):
    """
    Performance test function to count the number of leaf nodes at a given depth
    Used to verify move generation correctness
    """
    if depth == 0:
        return 1
    
    nodes = 0
    move_generator = MoveGenerator(board)
    legal_moves = move_generator.generate_legal_moves()
    
    if depth == 1:
        return len(legal_moves)
    
    for move in legal_moves:
        new_board = board.make_move(move)
        nodes += perft(new_board, depth - 1)
    
    return nodes

def perft_divide(board, depth):
    """
    Divide perft function that shows the node count for each move
    Useful for debugging move generation
    """
    move_generator = MoveGenerator(board)
    legal_moves = move_generator.generate_legal_moves()
    total_nodes = 0
    
    for move in legal_moves:
        new_board = board.make_move(move)
        nodes = perft(new_board, depth - 1)
        total_nodes += nodes
        print(f"{move}: {nodes}")
    
    print(f"\nTotal: {total_nodes}")
    return total_nodes

def run_perft_tests():
    """Run a series of perft tests on known positions"""
    test_positions = [
        # Initial position
        ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", [
            (1, 20),
            (2, 400),
            (3, 8902),
            (4, 197281),
            # (5, 4865609),  # Uncomment for deeper tests (slower)
        ]),
        # Position 2 (Kiwipete)
        ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", [
            (1, 48),
            (2, 2039),
            (3, 97862),
            # (4, 4085603),  # Uncomment for deeper tests (slower)
        ]),
        # Position 3
        ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", [
            (1, 14),
            (2, 191),
            (3, 2812),
            (4, 43238),
            # (5, 674624),  # Uncomment for deeper tests (slower)
        ]),
    ]
    
    for fen, depths in test_positions:
        print(f"Testing position: {fen}")
        board = Board(fen)
        
        for depth, expected in depths:
            start_time = time.time()
            nodes = perft(board, depth)
            elapsed = time.time() - start_time
            
            result = "PASS" if nodes == expected else f"FAIL (expected {expected})"
            print(f"  Depth {depth}: {nodes} nodes in {elapsed:.2f}s ({nodes/elapsed:.0f} nps) - {result}")
        
        print()

if __name__ == "__main__":
    import time
    run_perft_tests()

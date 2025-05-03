def parse_fen(fen):
    """Parse a FEN string into board representation and game state"""
    parts = fen.split()
    
    # Parse board position
    board_str = parts[0]
    board = []
    
    for rank_str in board_str.split('/'):
        rank = []
        for char in rank_str:
            if char.isdigit():
                # Add empty squares
                rank.extend(['.'] * int(char))
            else:
                # Add piece
                rank.append(char)
        board.append(rank)
    
    # Parse active color
    active_color = parts[1]
    
    # Parse castling rights
    castling = parts[2]
    
    # Parse en passant target square
    en_passant = parts[3]
    
    # Parse halfmove clock
    halfmove = parts[4]
    
    # Parse fullmove number
    fullmove = parts[5]
    
    return board, active_color, castling, en_passant, halfmove, fullmove

def generate_fen(board):
    """Generate a FEN string from a board object"""
    # Generate board position
    fen_parts = []
    
    # Board position
    ranks = []
    for rank in range(8):
        empty_count = 0
        rank_str = ""
        
        for file in range(8):
            piece = board.squares[rank][file]
            
            if piece:
                if empty_count > 0:
                    rank_str += str(empty_count)
                    empty_count = 0
                rank_str += str(piece)
            else:
                empty_count += 1
        
        if empty_count > 0:
            rank_str += str(empty_count)
        
        ranks.append(rank_str)
    
    fen_parts.append('/'.join(ranks))
    
    # Active color
    fen_parts.append('w' if board.active_color.name == 'WHITE' else 'b')
    
    # Castling rights
    castling = ""
    if board.castling_rights[board.Color.WHITE]['kingside']:
        castling += 'K'
    if board.castling_rights[board.Color.WHITE]['queenside']:
        castling += 'Q'
    if board.castling_rights[board.Color.BLACK]['kingside']:
        castling += 'k'
    if board.castling_rights[board.Color.BLACK]['queenside']:
        castling += 'q'
    
    fen_parts.append(castling if castling else '-')
    
    # En passant target square
    if board.en_passant_target:
        ep_rank, ep_file = board.en_passant_target
        files = 'abcdefgh'
        ranks = '87654321'
        fen_parts.append(f"{files[ep_file]}{ranks[ep_rank]}")
    else:
        fen_parts.append('-')
    
    # Halfmove clock
    fen_parts.append(str(board.halfmove_clock))
    
    # Fullmove number
    fen_parts.append(str(board.fullmove_number))
    
    return ' '.join(fen_parts)

class BitBoard:
    def __init__(self, value=0):
        self.value = value
    
    def set_bit(self, square):
        """Set a bit at the specified square (0-63)"""
        self.value |= (1 << square)
    
    def clear_bit(self, square):
        """Clear a bit at the specified square (0-63)"""
        self.value &= ~(1 << square)
    
    def get_bit(self, square):
        """Get the bit value at the specified square (0-63)"""
        return (self.value >> square) & 1
    
    def count_bits(self):
        """Count the number of set bits"""
        count = 0
        v = self.value
        while v:
            count += 1
            v &= v - 1  # Clear the least significant bit
        return count
    
    def get_least_significant_bit(self):
        """Get the index of the least significant bit"""
        if self.value == 0:
            return -1
        return (self.value & -self.value).bit_length() - 1
    
    def pop_least_significant_bit(self):
        """Get and clear the least significant bit"""
        if self.value == 0:
            return -1
        lsb = self.get_least_significant_bit()
        self.clear_bit(lsb)
        return lsb
    
    def __and__(self, other):
        """Bitwise AND operation"""
        return BitBoard(self.value & other.value)
    
    def __or__(self, other):
        """Bitwise OR operation"""
        return BitBoard(self.value | other.value)
    
    def __xor__(self, other):
        """Bitwise XOR operation"""
        return BitBoard(self.value ^ other.value)
    
    def __invert__(self):
        """Bitwise NOT operation"""
        return BitBoard(~self.value & 0xFFFFFFFFFFFFFFFF)  # 64-bit mask
    
    def __lshift__(self, shift):
        """Left shift operation"""
        return BitBoard(self.value << shift)
    
    def __rshift__(self, shift):
        """Right shift operation"""
        return BitBoard(self.value >> shift)
    
    def __str__(self):
        """String representation of the bitboard"""
        result = ""
        for rank in range(8):
            for file in range(8):
                square = rank * 8 + file
                result += "1 " if self.get_bit(square) else "0 "
            result += "\n"
        return result

# Predefined bitboards for common patterns
class BitBoardPatterns:
    @staticmethod
    def rank_mask(rank):
        """Create a bitboard with all bits set in the specified rank"""
        return BitBoard(0xFF << (rank * 8))
    
    @staticmethod
    def file_mask(file):
        """Create a bitboard with all bits set in the specified file"""
        mask = 0
        for rank in range(8):
            mask |= 1 << (rank * 8 + file)
        return BitBoard(mask)
    
    @staticmethod
    def diagonal_mask(square):
        """Create a bitboard with all bits set in the diagonal containing the square"""
        rank, file = square // 8, square % 8
        mask = 0
        
        # Diagonal from top-left to bottom-right
        r, f = rank, file
        while r >= 0 and f >= 0:
            mask |= 1 << (r * 8 + f)
            r -= 1
            f -= 1
        
        r, f = rank + 1, file + 1
        while r < 8 and f < 8:
            mask |= 1 << (r * 8 + f)
            r += 1
            f += 1
        
        return BitBoard(mask)
    
    @staticmethod
    def anti_diagonal_mask(square):
        """Create a bitboard with all bits set in the anti-diagonal containing the square"""
        rank, file = square // 8, square % 8
        mask = 0
        
        # Diagonal from top-right to bottom-left
        r, f = rank, file
        while r >= 0 and f < 8:
            mask |= 1 << (r * 8 + f)
            r -= 1
            f += 1
        
        r, f = rank + 1, file - 1
        while r < 8 and f >= 0:
            mask |= 1 << (r * 8 + f)
            r += 1
            f -= 1
        
        return BitBoard(mask)
    
    @staticmethod
    def knight_attacks(square):
        """Create a bitboard with all possible knight moves from the square"""
        rank, file = square // 8, square % 8
        mask = 0
        
        # All possible knight moves
        moves = [
            (rank-2, file-1), (rank-2, file+1),
            (rank-1, file-2), (rank-1, file+2),
            (rank+1, file-2), (rank+1, file+2),
            (rank+2, file-1), (rank+2, file+1)
        ]
        
        for r, f in moves:
            if 0 <= r < 8 and 0 <= f < 8:
                mask |= 1 << (r * 8 + f)
        
        return BitBoard(mask)
    
    @staticmethod
    def king_attacks(square):
        """Create a bitboard with all possible king moves from the square"""
        rank, file = square // 8, square % 8
        mask = 0
        
        # All possible king moves
        for r in range(max(0, rank-1), min(8, rank+2)):
            for f in range(max(0, file-1), min(8, file+2)):
                if r != rank or f != file:
                    mask |= 1 << (r * 8 + f)
        
        return BitBoard(mask)
    
    @staticmethod
    def pawn_attacks(square, color):
        """Create a bitboard with all possible pawn attacks from the square"""
        from chess_engine.engine.board import Color
        
        rank, file = square // 8, square % 8
        mask = 0
        
        if color == Color.WHITE:
            # White pawns attack diagonally up
            if rank > 0:
                if file > 0:
                    mask |= 1 << ((rank-1) * 8 + file-1)
                if file < 7:
                    mask |= 1 << ((rank-1) * 8 + file+1)
        else:
            # Black pawns attack diagonally down
            if rank < 7:
                if file > 0:
                    mask |= 1 << ((rank+1) * 8 + file-1)
                if file < 7:
                    mask |= 1 << ((rank+1) * 8 + file+1)
        
        return BitBoard(mask)

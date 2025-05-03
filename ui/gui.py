import sys
import threading
import time
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("Tkinter not available. GUI mode requires Python with Tkinter support.")
    sys.exit(1)

from Chess_Engine_in_python.engine.board import Board, Color, PieceType
from Chess_Engine_in_python.engine.move import Move, MoveGenerator
from Chess_Engine_in_python.engine.search import Search

class GUI:
    def __init__(self, board, depth=4, time_limit=5.0):
        self.board = board
        self.depth = depth
        self.time_limit = time_limit
        self.move_generator = MoveGenerator(board)
        
        # Track player color (player is white by default)
        self.player_color = Color.WHITE
        
        # Add game state variable
        self.game_over = False
        
        self.selected_square = None
        self.legal_moves = []
        self.thinking = False
        
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Chess Engine")
        
        # Make the window full screen
        self.root.state('zoomed')  # This works on Windows to maximize the window
        
        # Remove this line as it conflicts with the 'zoomed' state
        # self.root.resizable(False, False)
        
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.root.resizable(False, False)
        
        # Create left frame for the board
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create right frame for info
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the menu
        self.create_menu()
        
        # Create the board display
        self.square_size = 60
        self.canvas = tk.Canvas(self.left_frame, width=8*self.square_size, height=8*self.square_size)
        self.canvas.pack()
        
        # Create info frame and labels
        self.info_frame = tk.Frame(self.right_frame)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.eval_label = tk.Label(self.info_frame, text="Evaluation: 0.0", font=("Arial", 12))
        self.eval_label.pack(side=tk.TOP, anchor=tk.W)
        
        self.best_move_label = tk.Label(self.info_frame, text="Best move: None", font=("Arial", 12))
        self.best_move_label.pack(side=tk.TOP, anchor=tk.W)
        
        self.depth_label = tk.Label(self.info_frame, text="Depth: 0", font=("Arial", 12))
        self.depth_label.pack(side=tk.TOP, anchor=tk.W)
        
        self.nodes_label = tk.Label(self.info_frame, text="Nodes: 0", font=("Arial", 12))
        self.nodes_label.pack(side=tk.TOP, anchor=tk.W)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_square_clicked)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("White to move")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load piece images
        self.piece_images = {}
        self.load_piece_images()
        
        # Add variables to track best move
        self.best_move = None
        self.best_move_squares = []
        
        # Draw the initial board
        self.draw_board()
        
        # Add analyze button
        self.analyze_button = tk.Button(self.right_frame, text="Analyze Position", 
                                      command=self.computer_move)  # Changed to computer_move
        self.analyze_button.pack(pady=5)
        
        self.draw_board()
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Game", command=self.new_game)
        file_menu.add_command(label="Choose Color", command=self.set_player_color)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Computer Move", command=self.computer_move)
        game_menu.add_separator()
        game_menu.add_command(label="Set Position from FEN", command=self.set_position)
        menubar.add_cascade(label="Game", menu=game_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Set Search Depth", command=self.set_depth)
        settings_menu.add_command(label="Set Time Limit", command=self.set_time_limit)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def load_piece_images(self):
        """Load piece images (placeholder - would use actual images in a real implementation)"""
        # In a real implementation, you would load actual PNG images for the pieces
        # For this example, we'll use text representations
        piece_symbols = {
            (PieceType.PAWN, Color.WHITE): "♙",
            (PieceType.KNIGHT, Color.WHITE): "♘",
            (PieceType.BISHOP, Color.WHITE): "♗",
            (PieceType.ROOK, Color.WHITE): "♖",
            (PieceType.QUEEN, Color.WHITE): "♕",
            (PieceType.KING, Color.WHITE): "♔",
            (PieceType.PAWN, Color.BLACK): "♟",
            (PieceType.KNIGHT, Color.BLACK): "♞",
            (PieceType.BISHOP, Color.BLACK): "♝",
            (PieceType.ROOK, Color.BLACK): "♜",
            (PieceType.QUEEN, Color.BLACK): "♛",
            (PieceType.KING, Color.BLACK): "♚",
        }
        
        for piece_type in PieceType:
            for color in Color:
                symbol = piece_symbols.get((piece_type, color), "?")
                self.piece_images[(piece_type, color)] = symbol
    
    def draw_board(self):
        """Draw the chess board and pieces"""
        self.canvas.delete("all")
        
        # Draw squares
        for rank in range(8):
            for file in range(8):
                x1 = file * self.square_size
                y1 = rank * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Alternate square colors
                color = "#FFFFFF" if (rank + file) % 2 == 0 else "#5D8AA8"
                
                # Highlight selected square
                if self.selected_square == (rank, file):
                    color = "#FFFF00"  # Yellow highlight
                
                # Highlight legal move targets
                for move in self.legal_moves:
                    if move.to_square == (rank, file):
                        color = "#90EE90"  # Light green highlight
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                
                # Draw piece
                piece = self.board.get_piece_at(rank, file)
                if piece:
                    symbol = self.piece_images.get((piece.piece_type, piece.color), "?")
                    text_color = "black"
                    self.canvas.create_text(x1 + self.square_size/2, y1 + self.square_size/2, 
                                           text=symbol, font=("Arial", 36), fill=text_color)
        
        # Highlight best move if available
        if self.best_move:
            from_rank, from_file = self.best_move.from_square
            to_rank, to_file = self.best_move.to_square
            
            # Highlight source square
            x1 = from_file * self.square_size
            y1 = from_rank * self.square_size
            self.canvas.create_rectangle(x1, y1, x1 + self.square_size, y1 + self.square_size, 
                                         outline="green", width=3)
            
            # Highlight target square
            x2 = to_file * self.square_size
            y2 = to_rank * self.square_size
            self.canvas.create_rectangle(x2, y2, x2 + self.square_size, y2 + self.square_size, 
                                         outline="green", width=3)
            
            # Draw arrow from source to target
            self.canvas.create_line(
                x1 + self.square_size // 2, 
                y1 + self.square_size // 2,
                x2 + self.square_size // 2, 
                y2 + self.square_size // 2,
                fill="green", width=3, arrow=tk.LAST
            )
        
        # Draw rank and file labels
        for i in range(8):
            # Rank labels (8-1)
            self.canvas.create_text(5, i * self.square_size + self.square_size/2, 
                                   text=str(8-i), anchor=tk.W, font=("Arial", 10))
            # File labels (a-h)
            self.canvas.create_text(i * self.square_size + self.square_size/2, 8 * self.square_size - 5, 
                                   text=chr(97+i), anchor=tk.S, font=("Arial", 10))
    
    def on_square_clicked(self, event):
        """Handle mouse clicks on the board"""
        if self.thinking or self.game_over:
            return
        
        # Ensure it's the player's turn
        if (self.board.active_color == Color.WHITE and self.player_color != Color.WHITE) or \
           (self.board.active_color == Color.BLACK and self.player_color != Color.BLACK):
            self.status_var.set("Not your turn!")
            return
        
        # Convert pixel coordinates to board coordinates
        file = event.x // self.square_size
        rank = event.y // self.square_size
        
        if not (0 <= file < 8 and 0 <= rank < 8):
            return
        
        # Check if game is already over
        if self.check_game_end():
            return
            
        # Get all legal moves for the current position
        all_legal_moves = self.move_generator.generate_legal_moves()
        
        # Filter moves to ensure they don't leave the king in check
        legal_moves = []
        for move in all_legal_moves:
            if self.is_move_legal(move):
                legal_moves.append(move)
        
        # Check if king is in check
        king_pos = self.find_king_position(self.board.active_color)
        is_in_check = king_pos and self.board.is_square_attacked(
            king_pos[0], king_pos[1], 
            Color.BLACK if self.board.active_color == Color.WHITE else Color.WHITE
        )
        
        if is_in_check:
            self.status_var.set(f"{'White' if self.board.active_color == Color.WHITE else 'Black'} is in check!")
        
        if self.selected_square is None:
            # First click - select a piece
            piece = self.board.get_piece_at(rank, file)
            if piece and piece.color == self.board.active_color:
                self.selected_square = (rank, file)
                self.legal_moves = [move for move in legal_moves 
                                   if move.from_square == (rank, file)]
                
                # If no legal moves for this piece, inform the user
                if not self.legal_moves:
                    if is_in_check and piece.piece_type == PieceType.KING:
                        self.status_var.set("King is in check with no legal moves!")
                    elif is_in_check:
                        self.status_var.set("This piece cannot move while king is in check!")
                    else:
                        self.status_var.set("This piece has no legal moves!")
                
                self.draw_board()
        else:
            # Second click - try to move the selected piece
            if (rank, file) == self.selected_square:
                # Clicked the same square again - deselect
                self.selected_square = None
                self.legal_moves = []
                self.draw_board()
            else:
                # Try to find a legal move to this square
                move = None
                for m in self.legal_moves:
                    if m.to_square == (rank, file):
                        move = m
                        break
                
                if move:
                    # Handle pawn promotion
                    if (move.from_square[0] == 1 and move.to_square[0] == 0 and 
                        self.board.get_piece_at(*move.from_square).piece_type == PieceType.PAWN):
                        move.promotion_piece = self.get_promotion_choice()
                    
                    # Make the move
                    self.board = self.board.make_move(move)
                    self.move_generator = MoveGenerator(self.board)
                    
                    # Update status
                    self.status_var.set(f"{'White' if self.board.active_color == Color.WHITE else 'Black'} to move")
                    
                    # Check for game end
                    if self.check_game_end():
                        # Game is over
                        pass
                    elif self.player_color != self.board.active_color:
                        # If it's computer's turn now, make a move
                        self.root.after(500, self.computer_move)
                else:
                    self.status_var.set("Invalid move!")
                
                # Reset selection
                self.selected_square = None
                self.legal_moves = []
                self.draw_board()
                
                # Check for game end
                self.check_game_end()
    
    def get_promotion_choice(self):
        """Ask the user for pawn promotion choice"""
        choices = {
            "Queen": PieceType.QUEEN,
            "Rook": PieceType.ROOK,
            "Bishop": PieceType.BISHOP,
            "Knight": PieceType.KNIGHT
        }
        
        # Create a simple dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Pawn Promotion")
        dialog.geometry("200x150")
        dialog.resizable(False, False)
        
        label = tk.Label(dialog, text="Choose promotion piece:")
        label.pack(pady=10)
        
        result = [PieceType.QUEEN]  # Default
        
        for text, piece_type in choices.items():
            button = tk.Button(dialog, text=text, 
                              command=lambda pt=piece_type: [result.pop(), result.append(pt), dialog.destroy()])
            button.pack(fill=tk.X, padx=20, pady=2)
        
        # Wait for the dialog to be closed
        self.root.wait_window(dialog)
        
        return result[0]
    
    def computer_move(self):
        """Let the computer make a move"""
        if self.thinking or self.game_over:
            return
        
        # Check if game is already over
        if self.check_game_end():
            return
            
        # Ensure it's the computer's turn
        if (self.board.active_color == Color.WHITE and self.player_color == Color.WHITE) or \
           (self.board.active_color == Color.BLACK and self.player_color == Color.BLACK):
            return
        
        self.thinking = True
        self.status_var.set("Computer is thinking...")
        self.root.update()
        
        # Run search in a separate thread to keep UI responsive
        def search_thread():
            search = Search(self.board, self.depth)
            start_time = time.time()
            
            best_move = None
            best_score = 0
            
            for current_depth in range(1, self.depth + 1):
                search.max_depth = current_depth
                score, move = search.alpha_beta(self.board, current_depth, float('-inf'), float('inf'), True)
                
                elapsed = time.time() - start_time
                nodes = search.nodes_count if hasattr(search, 'nodes_count') else 0
                
                # Update best move
                if move and self.is_move_legal(move):  # Ensure the move is legal
                    best_move = move
                    best_score = score
                    self.best_move = move
                    
                    # Update GUI with search results
                    move_str = f"{chr(move.from_square[1] + 97)}{8 - move.from_square[0]}{chr(move.to_square[1] + 97)}{8 - move.to_square[0]}"
                    
                    # Print to console
                    print(f"Depth {current_depth}: Best move {move_str}, Score {score}, Nodes {nodes}, Time {elapsed:.2f}s")
                    
                    # Update GUI labels
                    self.root.after(0, lambda d=current_depth, s=score, n=nodes, t=elapsed, m=move_str: 
                                   self.update_info_labels(d, s, n, t, m))
                    
                    # Redraw board to show best move
                    self.root.after(0, self.draw_board)
                
                # Check if time limit reached
                if elapsed >= self.time_limit * 0.8:
                    break
            
            # Make the best move found
            if best_move:
                self.board = self.board.make_move(best_move)
                self.move_generator = MoveGenerator(self.board)
                
                # Update UI from the main thread
                self.root.after(0, lambda: self.status_var.set(
                    f"{'White' if self.board.active_color == Color.WHITE else 'Black'} to move"))
                self.root.after(0, self.draw_board)
                self.root.after(0, self.check_game_end)
            else:
                self.root.after(0, lambda: self.status_var.set("No legal moves available"))
            
            self.thinking = False
        
        threading.Thread(target=search_thread).start()
    
    def check_game_end(self):
        """Check if the game has ended"""
        # If game is already marked as over, return True
        if self.game_over:
            return True
            
        # Generate legal moves - these should already filter out moves that leave the king in check
        legal_moves = self.move_generator.generate_legal_moves()
        
        # Find king position
        king_pos = self.find_king_position(self.board.active_color)
        
        # Check if king is in check
        is_in_check = king_pos and self.board.is_square_attacked(
            king_pos[0], king_pos[1], 
            Color.BLACK if self.board.active_color == Color.WHITE else Color.WHITE
        )
        
        if not legal_moves:
            if is_in_check:
                # Checkmate
                winner = "Black" if self.board.active_color == Color.WHITE else "White"
                self.status_var.set(f"Checkmate! {winner} wins!")
                messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
                self.game_over = True
            else:
                # Stalemate
                self.status_var.set("Stalemate! The game is a draw.")
                messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
                self.game_over = True
            
            return True
        
        # Check if king is in check but has legal moves
        if is_in_check:
            self.status_var.set(f"{'White' if self.board.active_color == Color.WHITE else 'Black'} is in check!")
        
        return False
    
    def new_game(self):
        """Start a new game"""
        self.board = Board()
        self.move_generator = MoveGenerator(self.board)
        self.selected_square = None
        self.legal_moves = []
        self.game_over = False
        self.status_var.set("White to move")
        self.draw_board()
    
    def set_position(self):
        """Set a position from FEN string"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Position")
        dialog.geometry("400x100")
        
        tk.Label(dialog, text="Enter FEN:").pack(pady=5)
        
        fen_entry = tk.Entry(dialog, width=50)
        fen_entry.pack(pady=5)
        fen_entry.insert(0, self.board.to_fen())
        
        def apply():
            try:
                fen = fen_entry.get()
                self.board = Board(fen)
                self.move_generator = MoveGenerator(self.board)
                self.selected_square = None
                self.legal_moves = []
                self.status_var.set(f"{'White' if self.board.active_color == Color.WHITE else 'Black'} to move")
                self.draw_board()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid FEN: {e}")
        
        tk.Button(dialog, text="Apply", command=apply).pack(pady=5)
    
    def set_depth(self):
        """Set the search depth"""
        depth = tk.simpledialog.askinteger("Search Depth", "Enter search depth:", 
                                          initialvalue=self.depth, minvalue=1, maxvalue=10)
        if depth:
            self.depth = depth
    
    def set_time_limit(self):
        """Set the search time limit"""
        time_limit = tk.simpledialog.askfloat("Time Limit", "Enter time limit (seconds):", 
                                             initialvalue=self.time_limit, minvalue=0.1)
        if time_limit:
            self.time_limit = time_limit
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Chess Engine\nA simple chess engine written in Python")
    
    def set_player_color(self):
        """Let the player choose their color"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Color")
        dialog.geometry("200x100")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Play as:").pack(pady=5)
        
        def set_white():
            self.player_color = Color.WHITE
            self.status_var.set("You play as White. White to move.")
            dialog.destroy()
            # Reset the game
            self.new_game()
        
        def set_black():
            self.player_color = Color.BLACK
            self.status_var.set("You play as Black. White to move.")
            dialog.destroy()
            # Reset the game and let computer make first move
            self.new_game()
            self.root.after(500, self.computer_move)
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="White", command=set_white).pack(side=tk.LEFT, expand=True, padx=10)
        tk.Button(button_frame, text="Black", command=set_black).pack(side=tk.RIGHT, expand=True, padx=10)
        
    def run(self):
        """Run the GUI"""
        self.root.mainloop()
        
    def update_info_labels(self, depth, score, nodes, elapsed, move_str):
        """Update the information labels with search results"""
        self.eval_label.config(text=f"Evaluation: {score/100:.2f}")
        self.best_move_label.config(text=f"Best move: {move_str}")
        self.depth_label.config(text=f"Depth: {depth}")
        self.nodes_label.config(text=f"Nodes: {nodes}")
        
        # Force update of GUI
        self.root.update_idletasks()

    def find_king_position(self, color):
        """Find the position of the king of the given color"""
        for rank in range(8):
            for file in range(8):
                piece = self.board.get_piece_at(rank, file)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return (rank, file)
        return None

    def is_move_legal(self, move):
        """Check if a move is legal (doesn't leave the king in check)"""
        # Make the move on a temporary board
        temp_board = self.board.make_move(move)
        
        # Find the king position after the move
        king_pos = None
        for rank in range(8):
            for file in range(8):
                piece = temp_board.get_piece_at(rank, file)
                if piece and piece.piece_type == PieceType.KING and piece.color == self.board.active_color:
                    king_pos = (rank, file)
                    break
            if king_pos:
                break
        
        # If king not found, move is illegal
        if not king_pos:
            return False
        
        # Check if king is attacked after the move
        opponent_color = Color.BLACK if self.board.active_color == Color.WHITE else Color.WHITE
        return not temp_board.is_square_attacked(king_pos[0], king_pos[1], opponent_color)

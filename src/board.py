import copy
from enum import Enum

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Color(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    def __init__(self, piece_type, color):
        self.type = piece_type
        self.color = color
    
    def __repr__(self):
        color_symbol = 'w' if self.color == Color.WHITE else 'b'
        type_symbols = {
            PieceType.PAWN: 'P',
            PieceType.KNIGHT: 'N',
            PieceType.BISHOP: 'B',
            PieceType.ROOK: 'R',
            PieceType.QUEEN: 'Q',
            PieceType.KING: 'K'
        }
        return f"{color_symbol}{type_symbols[self.type]}"

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.move_history = []
        self.white_king_pos = None
        self.black_king_pos = None
        self._initialize_board()
    
    def _initialize_board(self):
        """Initialize the chess board with starting position"""
        # Place pawns
        for col in range(8):
            self.grid[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self.grid[6][col] = Piece(PieceType.PAWN, Color.WHITE)
        
        # Place rooks
        self.grid[0][0] = Piece(PieceType.ROOK, Color.BLACK)
        self.grid[0][7] = Piece(PieceType.ROOK, Color.BLACK)
        self.grid[7][0] = Piece(PieceType.ROOK, Color.WHITE)
        self.grid[7][7] = Piece(PieceType.ROOK, Color.WHITE)
        
        # Place knights
        self.grid[0][1] = Piece(PieceType.KNIGHT, Color.BLACK)
        self.grid[0][6] = Piece(PieceType.KNIGHT, Color.BLACK)
        self.grid[7][1] = Piece(PieceType.KNIGHT, Color.WHITE)
        self.grid[7][6] = Piece(PieceType.KNIGHT, Color.WHITE)
        
        # Place bishops
        self.grid[0][2] = Piece(PieceType.BISHOP, Color.BLACK)
        self.grid[0][5] = Piece(PieceType.BISHOP, Color.BLACK)
        self.grid[7][2] = Piece(PieceType.BISHOP, Color.WHITE)
        self.grid[7][5] = Piece(PieceType.BISHOP, Color.WHITE)
        
        # Place queens
        self.grid[0][3] = Piece(PieceType.QUEEN, Color.BLACK)
        self.grid[7][3] = Piece(PieceType.QUEEN, Color.WHITE)
        
        # Place kings
        self.grid[0][4] = Piece(PieceType.KING, Color.BLACK)
        self.grid[7][4] = Piece(PieceType.KING, Color.WHITE)
        self.black_king_pos = (0, 4)
        self.white_king_pos = (7, 4)
    
    def get_piece(self, row, col):
        """Get piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        """Set piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.grid[row][col] = piece
    
    def is_valid_position(self, row, col):
        """Check if position is within board bounds"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def is_square_attacked(self, row, col, by_color):
        """Check if a square is attacked by a specific color"""
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece.color == by_color:
                    if self._can_piece_attack(r, c, row, col):
                        return True
        return False
    
    def _can_piece_attack(self, from_row, from_col, to_row, to_col):
        """Check if a piece can attack a specific square"""
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return False
        
        target = self.get_piece(to_row, to_col)
        
        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            if from_row + direction == to_row and abs(from_col - to_col) == 1:
                return True
        
        elif piece.type == PieceType.KNIGHT:
            if (abs(from_row - to_row), abs(from_col - to_col)) in [(1, 2), (2, 1)]:
                return True
        
        elif piece.type == PieceType.BISHOP:
            if abs(from_row - to_row) == abs(from_col - to_col):
                return self._is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece.type == PieceType.ROOK:
            if from_row == to_row or from_col == to_col:
                return self._is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece.type == PieceType.QUEEN:
            if from_row == to_row or from_col == to_col or abs(from_row - to_row) == abs(from_col - to_col):
                return self._is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece.type == PieceType.KING:
            if abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1:
                return True
        
        return False
    
    def _is_path_clear(self, from_row, from_col, to_row, to_col):
        """Check if path between two positions is clear"""
        row_dir = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_dir = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row = from_row + row_dir
        current_col = from_col + col_dir
        
        while (current_row, current_col) != (to_row, to_col):
            if self.get_piece(current_row, current_col) is not None:
                return False
            current_row += row_dir
            current_col += col_dir
        
        return True
    
    def is_valid_move(self, from_row, from_col, to_row, to_col, ignore_check=False):
        """Check if a move is valid"""
        if not self.is_valid_position(from_row, from_col) or not self.is_valid_position(to_row, to_col):
            return False
        
        piece = self.get_piece(from_row, from_col)
        if piece is None:
            return False
        
        target = self.get_piece(to_row, to_col)
        if target and target.color == piece.color:
            return False
        
        if piece.type == PieceType.PAWN:
            return self._is_valid_pawn_move(piece, from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.KNIGHT:
            return self._is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.BISHOP:
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.ROOK:
            return self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.QUEEN:
            return self._is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.KING:
            return self._is_valid_king_move(from_row, from_col, to_row, to_col)
        
        return False
    
    def _is_valid_pawn_move(self, piece, from_row, from_col, to_row, to_col):
        """Validate pawn move"""
        direction = -1 if piece.color == Color.WHITE else 1
        target = self.get_piece(to_row, to_col)
        
        # Forward move
        if from_col == to_col:
            if to_row == from_row + direction and target is None:
                return True
            # Two squares from starting position
            start_row = 6 if piece.color == Color.WHITE else 1
            if from_row == start_row and to_row == from_row + 2 * direction and target is None:
                if self.get_piece(from_row + direction, from_col) is None:
                    return True
        # Capture
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction and target is not None:
            return True
        
        return False
    
    def _is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        """Validate knight move"""
        return (abs(from_row - to_row), abs(from_col - to_col)) in [(1, 2), (2, 1)]
    
    def _is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        """Validate bishop move"""
        if abs(from_row - to_row) == abs(from_col - to_col) and from_row != to_row:
            return self._is_path_clear(from_row, from_col, to_row, to_col)
        return False
    
    def _is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        """Validate rook move"""
        if (from_row == to_row or from_col == to_col) and (from_row != to_row or from_col != to_col):
            return self._is_path_clear(from_row, from_col, to_row, to_col)
        return False
    
    def _is_valid_queen_move(self, from_row, from_col, to_row, to_col):
        """Validate queen move"""
        if from_row == to_row or from_col == to_col or abs(from_row - to_row) == abs(from_col - to_col):
            if from_row != to_row or from_col != to_col:
                return self._is_path_clear(from_row, from_col, to_row, to_col)
        return False
    
    def _is_valid_king_move(self, from_row, from_col, to_row, to_col):
        """Validate king move"""
        return abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1 and (from_row != to_row or from_col != to_col)
    
    def make_move(self, from_row, from_col, to_row, to_col):
        """Make a move on the board"""
        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            return False
        
        piece = self.get_piece(from_row, from_col)
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
        
        # Update king position
        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_king_pos = (to_row, to_col)
            else:
                self.black_king_pos = (to_row, to_col)
        
        self.move_history.append(((from_row, from_col), (to_row, to_col)))
        return True
    
    def is_in_check(self, color):
        """Check if king of given color is in check"""
        king_pos = self.white_king_pos if color == Color.WHITE else self.black_king_pos
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(king_pos[0], king_pos[1], enemy_color)
    
    def get_all_valid_moves(self, color):
        """Get all valid moves for a color"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    for target_row in range(8):
                        for target_col in range(8):
                            if self.is_valid_move(row, col, target_row, target_col):
                                # Make move and check if still in check
                                board_copy = self.copy()
                                board_copy.make_move(row, col, target_row, target_col)
                                if not board_copy.is_in_check(color):
                                    moves.append(((row, col), (target_row, target_col)))
        return moves
    
    def is_checkmate(self, color):
        """Check if king of given color is in checkmate"""
        if not self.is_in_check(color):
            return False
        return len(self.get_all_valid_moves(color)) == 0
    
    def is_stalemate(self, color):
        """Check if game is stalemate"""
        if self.is_in_check(color):
            return False
        return len(self.get_all_valid_moves(color)) == 0
    
    def copy(self):
        """Create a deep copy of the board"""
        new_board = Board.__new__(Board)
        new_board.grid = [row[:] for row in self.grid]
        new_board.move_history = self.move_history.copy()
        new_board.white_king_pos = self.white_king_pos
        new_board.black_king_pos = self.black_king_pos
        return new_board
    
    def display(self):
        """Display the board in text format"""
        print("  a b c d e f g h")
        for row in range(8):
            print(f"{8-row} ", end="")
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece is None:
                    print(". ", end="")
                else:
                    print(f"{piece} ", end="")
            print(f"{8-row}")
        print("  a b c d e f g h")

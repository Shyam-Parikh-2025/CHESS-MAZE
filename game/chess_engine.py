# Documentation:
# The pieces are stored as integers in the following binary method.
# The 4th bit determines color: so, 0 for white, 1 for black
# First 3 bits show type to (val 1-7) the piece types are title below.
# (piece & 7) is used to find type and (piece & 8) to find color (Bitwise operations)
# Example: 1110 (14 - shows black king = black(8) + king(6)=14)
#          0110 (6 - shows white king = white(0) + king(6)=6)
# Some of the complicated functions have docstring explaining their use.
# A pseudo valid move is a move that a piece can do, but it is not checked that it would
# cause check on the same color, so a black pawn moving can allow a check to the black king if
# we just looked at pseudo valid moves, but valid moves are checked moves
#  
import pygame as pg
import numpy as np
import os
from numba import njit
from constants import ROWS, COLS, SQSIZE, WIDTH, HEIGHT, color
from piece_points import piece_square_mid_game, piece_square_end_game, PHASE_WEIGHTS
 
# ============ PIECE TYPES =================
w_p, w_k, w_b, w_r, w_q, w_K = 1, 2, 3, 4, 5, 6
b_p, b_k, b_b, b_r, b_q, b_K = 9, 10, 11, 12, 13, 14
empty = 0
# black 1000 binary + piece value
 
# ============ OFFSETS =================
knight_offsets = np.array([-17, -15, -10, -6, 6, 10, 15, 17], dtype=np.int32)
diag_offsets = np.array([-9, -7, 7, 9], dtype=np.int32)
straight_offsets = np.array([-8, -1, 1, 8], dtype=np.int32)
king_offsets = np.array([-9, -8, -7, -1, 1, 7, 8, 9], dtype=np.int32)
 
# ZOBRIST HASHING TRIAL
#np.random.seed(9)
#ZOBRIST_PIECES = np.random.randint(0,2**63 -1, size=(15, 64), dtype=np.uint64)
#ZOBRIST_TURN = np.random.randint(0, 2**63 - 1, dtype=np.uint64)
 
class Chess:
    def __init__(self, super_mode: int=0, load_graphic: bool=True):
 
        pawn_row = np.array([w_p] * COLS)
        # To add exta queens if more dragons beaten
        if super_mode > 0:
            cnt = min(super_mode, COLS)
            idxs = np.random.choice(len(pawn_row), cnt, replace=False)
            pawn_row[idxs] = w_q
        
        self.board = np.zeros(64, dtype=np.int8)
        self.board[0: 8]  = [b_r, b_k, b_b, b_q, b_K, b_b, b_k, b_r]
        self.board[8: 16] = [b_p, b_p, b_p, b_p, b_p, b_p, b_p, b_p]
        self.board[48: 56]= pawn_row
        self.board[56: 64] = [w_r, w_k, w_b, w_q, w_K, w_b, w_k, w_r]
 
        self.white_turn = True
        self.move_log = []
        self.images = {}
        if load_graphic:
            self.load_images()
        
        # FOR PIECE SQUARE POINTS
        self.phase = 0
        self.mid_game_score = 0
        self.end_game_score = 0
        self.calc_board_score()
        self.max_phase = max(24, self.phase) # SO IT DOESN'T DROP BELOW 24
        self.white_king_sq, self.black_king_sq = 60, 4
 
    
    def calc_board_score(self):
        for sq in range(64):
                piece = self.board[sq]
                if piece != 0:
                    self.mid_game_score += piece_square_mid_game[piece][sq]
                    self.end_game_score += piece_square_end_game[piece][sq]
                    self.phase += PHASE_WEIGHTS[piece]
    
    def eval_board(self):
        phase = min(max(self.phase, 0), self.max_phase)
        return (self.mid_game_score * phase + self.end_game_score * (self.max_phase - phase)) // self.max_phase # https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
 
    def load_images(self):
        """This just loads the image with a library called os"""
        try:
            base_path = os.path.dirname(__file__)
            image_folder = os.path.join(base_path, "images")
            
            pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
            colors = ['white', 'black']
            for c in colors:
                for p in pieces:
                    key = f"{c}_{p}"
                    full_path = os.path.join(image_folder, f"{key}.png")
                    img = pg.image.load(full_path).convert_alpha()
                    img = pg.transform.smoothscale(img, (SQSIZE, SQSIZE))
                    self.images[key] = img
        except Exception as e:
            print(f"ERROR: {e}")
            print("Piece files not found, shifting to text if possible. Please double check images.")
 
    def make_move(self, move):
        """ This makes the move and stores it in the move_log"""
        start, end, flag = decode_move(move)
        piece = self.board[start]
        captured_piece = self.board[end]
 
        self.move_log.append((move, captured_piece, self.white_king_sq, self.black_king_sq,
                              self.white_turn, self.phase, self.mid_game_score, self.end_game_score))
        self.mid_game_score -= piece_square_mid_game[piece][start]
        self.end_game_score -= piece_square_end_game[piece][end]
        
        if (piece & 7) == 6:
            if piece & 8:
                self.black_king_sq = end
            else:
                self.white_king_sq = end
        
        if captured_piece != 0:
            self.mid_game_score -= piece_square_mid_game[captured_piece][end]
            self.end_game_score -= piece_square_end_game[captured_piece][end]
            self.phase -= PHASE_WEIGHTS[captured_piece]
        
        if flag == 1: # PAWN PROMOTION
            promote_queen_val = 13 if (piece & 8) else 5
            self.board[end] = promote_queen_val
            self.mid_game_score += piece_square_mid_game[promote_queen_val][end]
            self.end_game_score += piece_square_end_game[promote_queen_val][end]
            self.phase += PHASE_WEIGHTS[promote_queen_val]
        else:
            self.board[end] = piece
            self.mid_game_score += piece_square_mid_game[piece][end]
            self.end_game_score += piece_square_end_game[piece][end]
        
        self.board[start] = 0
        self.white_turn = not self.white_turn
 
        # move_log syntax [(move, captured piece, whose turn, maybe special move if exist)...]
 
    def undo_move(self):
        """ This undos the last move and removes it from the move_log"""
        if not self.move_log:
            return
        last_move = self.move_log.pop()
        move, captured_piece,  prev_w_K, prev_b_K, prev_turn, prev_phase, prev_mid_game, prev_end_game= last_move
        self.mid_game_score, self.end_game_score = prev_mid_game, prev_end_game
        self.phase = prev_phase
        self.white_turn = prev_turn
        self.white_king_sq = prev_w_K
        self.black_king_sq = prev_b_K
        
        start, end, flag = decode_move(move)
        curr_piece = self.board[end]
 
        if flag == 1:
            pawn_val = 9 if (curr_piece & 8) else 1
            self.board[start] = pawn_val
        else:
            self.board[start] = curr_piece
        
        self.board[end] = captured_piece
        
    
    def get_valid_moves(self):
        """This function gets all pseudo valid moves and validates each one."""
        pseuodo_valid_moves = self.get_all_pos_moves()
        return self.validate_moves(pseuodo_valid_moves)
 
    def get_all_pos_moves(self):
        """This is a method in the chess class that calls on a numba function with all
        parameters added (numba can not accept self)"""
        board = self.board
        return get_pos_moves(self.white_turn, board)
 
    
 
    def validate_moves(self, pseudo_moves):
        """The validation function that calls on the helper function is_check to
        validate pseudo moves"""
        valid_moves=[]
 
        for move in pseudo_moves:
            self.make_move(move)
 
            if not self.is_in_check(not self.white_turn):
                valid_moves.append(move)
 
            self.undo_move()
 
        return valid_moves
 
    def is_in_check(self, is_white_king):
        """Finds where the king is of the color and uses the is_square_attacked function
        to find if the king is attacked"""
        king_sq= self.white_king_sq if is_white_king else self.black_king_sq
        attacker_is_white = not is_white_king
        return is_square_attacked(self.board, king_sq, attacker_is_white)
    
    def is_checkmate(self):
        """is_checkmate function returns true if a color is checked and no other moves."""
        if self.is_in_check(self.white_turn):
            valid_moves = self.get_valid_moves()
            if len(valid_moves) == 0:
                return True
        return False
    
    def is_stalemate(self):
        """is_stalemate function return true if a color is not checked and no other moves."""
        if not self.is_in_check(self.white_turn):
            if len(self.get_valid_moves()) == 0:
                return True
        return False
 
@njit
def get_pos_moves(white_turn, board):
    """This function uses numba and a helper function for each piece to find all pos moves"""
    moves = np.zeros(256, dtype=np.int32)
    cnt = 0
    for sq in range(64):
            piece = board[sq]
            if piece == 0: continue
 
            piece_is_black = bool(piece & 8)
            if white_turn and piece_is_black: continue
            if not white_turn and not piece_is_black: continue
 
            color = -1 if not piece_is_black else 1
            piece_type = piece & 7
 
            if piece_type == 1:
                cnt = pawn_moves(board, sq, color, moves, cnt)
            elif piece_type == 2:
                cnt = knight_moves(board, sq, moves, cnt)
            elif piece_type == 3:
                cnt = bishop_moves(board, sq, moves, cnt)
            elif piece_type == 4:
                cnt = rook_moves(board, sq, moves, cnt)
            elif piece_type == 5:
                cnt = queen_moves(board, sq, moves, cnt)
            elif piece_type == 6:
                cnt = king_moves(board, sq, moves, cnt)
 
    return moves[:cnt]
 
#============== HELPER FUNCTIONS FOR MOVE FINDING  =================
@njit
def pawn_moves(board, sq, color, moves, cnt):
    is_black = (color == 1)
    dir_offset = 8 if is_black else -8
    start_row = 1 if is_black else 6
    promote_row = 7 if is_black else 0
    
    target = sq + dir_offset
    if 0 <= target < 64 and board[target] == 0:
        if target // 8 == promote_row:
            moves[cnt] = sq | (target << 6) | (1 << 12)
        else:
            moves[cnt] = sq | (target << 6)
        cnt  +=1
 
        if sq // 8 == start_row:
            target_2_ahead = sq + (2 * dir_offset)
            if board[target_2_ahead] == 0:
                moves[cnt] = sq | (target_2_ahead << 6)
                cnt += 1
        
        for diag_offset in (dir_offset - 1, dir_offset + 1):
            target = sq + diag_offset
            if 0 <= target < 64:
                if abs((sq % 8) - (target % 8)) == 1:
                    target_piece = board[target]
                    if target_piece != 0:
                        if ((board[sq] & 8) != (target_piece & 8)): # if not team
                            if target // 8 == promote_row:
                                moves[cnt] = sq | (target << 6) | (1 << 12)
                            else:
                                moves[cnt] = sq | (target << 6)
                            cnt += 1
    return cnt # optional en passant
 
@njit
def knight_moves(board, sq, moves, cnt):
    for jump in knight_offsets:
        target_sq = sq + jump
        if 0 <= target_sq < 64:
            if abs((sq % 8) - (target_sq % 8)) <= 2: # difference of rows to ensure no teleporting btw row 8 -> row1
                target_piece = board[target_sq]
                if target_piece == 0 or ((board[sq] & 8) != (target_piece & 8)):
                    moves[cnt] = sq | (target_sq << 6)
                    cnt += 1
    return cnt
 
@njit
def bishop_moves(board, sq, moves, cnt):
    return sliding_piece_move_finder(board, sq, diag_offsets, moves, cnt)
@njit
def rook_moves(board, sq, moves, cnt):
    return sliding_piece_move_finder(board, sq, straight_offsets, moves, cnt)
@njit
def queen_moves(board, sq, moves, cnt):
    cnt = sliding_piece_move_finder(board, sq, diag_offsets, moves, cnt)
    cnt = sliding_piece_move_finder(board, sq, straight_offsets, moves, cnt)
    return cnt
@njit
def king_moves(board, sq, moves, cnt):
    for jump in king_offsets: # will handle castling and all later if possible
        target = sq + jump
        if 0 <= target < 64:
            if abs((sq % 8) - (target % 8)) <= 1:
                target_piece = board[target]
                if target_piece == 0 or (board[sq] & 8) != (target_piece & 8):
                    moves[cnt] = sq | (target << 6)
                    cnt += 1
    return cnt
 
@njit
def sliding_piece_move_finder(board, sq, offsets, moves, cnt):
    """ This function is a helper function for the bishop, rook, king and queen and adds on each direction
    until the board ends and/or a piece is found"""
    for jump in offsets:
        target = sq
        for _ in range(1, 8):
            col = target % 8
            target += jump
 
            if target < 0 or target >= 64: break
 
            if abs(col - (target % 8)) > 1: break
 
            target_piece = board[target]
            if target_piece == 0:
                moves[cnt] = sq | (target << 6)
                cnt += 1
            else:
                if (board[sq] & 8) != (target_piece & 8):
                    moves[cnt] = sq | (target << 6)
                    cnt += 1
                break
    return cnt
 
@njit
def is_square_attacked(board, sq, attacker_is_white):
    """Helper func of is_check and finds all moves that would have an end destination
    at the square asked for."""
    attacker_color_bit = 0 if attacker_is_white else 8
 
    pawn_dir = 8 if attacker_is_white else -8
    for shift in (pawn_dir -1, pawn_dir+1):
        target = sq + shift
        if 0 <= target < 64 and abs((sq % 8) - (target % 8)) == 1:
            if board[target] == (1 | attacker_color_bit):
                return True
    
    knight_val = 2 | attacker_color_bit
    for jump in knight_offsets:
        target = sq + jump
        if 0 <= target < 64 and abs((sq % 8) - (target % 8)) <= 2:
            if board[target] == knight_val: return True
    
    king_val = 6 | attacker_color_bit
    for jump in king_offsets:
        target = sq + jump
        if 0 <= target < 64 and abs((sq % 8) - (target % 8)) <= 1:
            if board[target] == king_val: return True
    
    bishop_val = 3 | attacker_color_bit
    rook_val = 4 | attacker_color_bit
    queen_val = 5 | attacker_color_bit
 
    for jump in diag_offsets:
        target = sq
        for _ in range(1, 8):
            col = target % 8
            target += jump
            if target < 0 or target >= 64 or abs(col - (target % 8)) > 1: break
            target_val = board[target]
            if target_val != 0:
                if target_val == bishop_val or target_val == queen_val:
                    return True
                break
    
    for jump in straight_offsets:
        target = sq
        for _ in range(1, 8):
            col = target % 8
            target += jump
            if target < 0 or target >= 64 or abs(col - (target % 8)) > 1: break
            target_val = board[target]
            if target_val != 0:
                if target_val == rook_val or target_val == queen_val:
                    return True
                break
    return False
            
    
 
    
# move = ((start row, start col),(end row, end col))
 
@njit
def score_move(move, board):
    start = move & 63
    end = (move >> 6) & 63
    flag = move >> 12
    score = 0
    captured_piece = board[end]
    if captured_piece != 0:
        val = captured_piece & 7
        score += 10 * val
        piece = board[start] & 7
        score -= piece * 3 # MAY CHANGE LATER
    if flag == 1:
        score += 90
    return score
 
@njit
def sort_moves(moves, board):
    scores = []
    for i in range(len(moves)):
        scores.append(score_move(moves[i], board))
    
    n = len(moves)
    for i in range(n):
        for j in range(0, n-i-1):
            if scores[j] < scores[j+1]:
                score_temporary = scores[j]
                scores[j] = scores[j + 1]
                scores[j+1] = score_temporary
 
                move_temporary = moves[j]
                moves[j] = moves[j + 1]
                moves[j+1] = move_temporary
    return moves
 
 
# SHIFTING TO INT MOVES INSTEAD OF TUPLES
 
# RETIRED FUNCTIONS - USEFUL UNTIL THEY WERE USED ...
@njit
def encode_move(start, end, flag):
    return start | (end << 6) | (flag << 12)
 
@njit
def decode_move(move):
    start = move & 63
    end = (move >> 6) & 63
    flag = move >> 12
    return start, end, flag
 
@njit
def in_range(num, st=0, en=8):
    return st<=num<en
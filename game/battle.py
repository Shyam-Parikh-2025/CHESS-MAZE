from chess_engine import Chess, decode_move
from constants import SQSIZE
from dragon import Dragon
from player import Player
import pygame as pg
import threading

class Battle:
    def __init__(self, surface, dragon_level, dragon_name, player=Player((2,2)), super_mode=0):
        self.surface = surface
        self.super_mode = super_mode
        self.chess_engine = Chess(super_mode=self.super_mode) 
        self.is_active = True

        self.selected_sq = None
        self.hover_sq = None
        self.hover_moves = []

        self.player = player
        self.time_limit_bonus = max(self.player.dragons_beaten, 0) + player.time_limit_of_AI
        #print(self.time_limit_bonus)
        self.player.can_move = False
        self.dragon = Dragon(dragon_name, dragon_level)
        self.dragon_level = dragon_level
        self.game_over_processed = False
        self.ai_thinking = False
        self.ai_thread = None
        self.calculated_move = None
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            col = mouse_x // SQSIZE
            row = mouse_y // SQSIZE
            if 0<= row < 8 and 0 <= col < 8:
                sq = row * 8 + col
                self.click_process(sq)
        
        if event.type == pg.MOUSEMOTION:
            mouse_x, mouse_y = pg.mouse.get_pos()
            col = mouse_x // SQSIZE
            row = mouse_y // SQSIZE

            if 0 <= row < 8 and 0 <= col < 8:
                sq = row * 8 + col
                if self.hover_sq != sq:
                    self.hover_sq = sq
                    self.update_hover_moves()
            else:
                if self.hover_sq is not None:
                    self.hover_sq = None
                    self.hover_moves = []
        
    def update_hover_moves(self):
        self.hover_moves = []
        target_sq = self.selected_sq if self.selected_sq is not None else self.hover_sq
        if target_sq is not None:
            piece = self.chess_engine.board[target_sq]
            if piece != 0 and not (piece & 8) and self.chess_engine.white_turn:
                for move in self.chess_engine.get_valid_moves():
                    start, end, flag = decode_move(move)
                    if start == target_sq:
                        self.hover_moves.append(end)

    
    def click_process(self, sq):
        if self.selected_sq is None:
            piece = self.chess_engine.board[sq]
            if piece != 0:
                is_black = bool(piece  & 8)
                if self.chess_engine.white_turn and not is_black:
                    self.selected_sq = sq
                    #print(f"Selected: {self.selected_sq}")
    
        else:
            if self.selected_sq == sq:
                self.selected_sq = None
                return
            move_to_make = None
            for move in  self.chess_engine.get_valid_moves():
                start, end, flag = decode_move(move)
                if start == self.selected_sq and end == sq:
                    move_to_make = move
                    break
            if move_to_make is not None:
                self.chess_engine.make_move(move_to_make)
                self.selected_sq = None
                self.check_game_over(self.player)
            else:
                n_piece = self.chess_engine.board[sq]
                if self.chess_engine.white_turn and n_piece != 0 and not (n_piece & 8):
                    self.selected_sq = sq
                else:
                    self.selected_sq = None
        self.update_hover_moves()
    def update(self):
        if not self.chess_engine.white_turn and not self.game_over_processed:
            if not self.ai_thinking:
                self.trigger_dragon_move()
            elif self.calculated_move is not None:
                self.chess_engine.make_move(self.calculated_move)
                self.check_game_over(self.player)

                self.ai_thinking = False
                self.calculated_move = None
                self.ai_thread = None

    def trigger_dragon_move(self):
        self.ai_thinking = True
        self.calculated_move = None

        chess_engine_clone = Chess(super_mode=self.super_mode, load_graphic=False)
        chess_engine_clone.board = self.chess_engine.board.copy()
        chess_engine_clone.white_turn = self.chess_engine.white_turn
        chess_engine_clone.white_king_sq = self.chess_engine.white_king_sq
        chess_engine_clone.black_king_sq = self.chess_engine.black_king_sq
        chess_engine_clone.mid_game_score = self.chess_engine.mid_game_score
        chess_engine_clone.end_game_score = self.chess_engine.end_game_score
        chess_engine_clone.phase = self.chess_engine.phase
        chess_engine_clone.max_phase = self.chess_engine.max_phase

        self.ai_thread = threading.Thread(target=self._calculate_move_thread,
                                          args=(chess_engine_clone,))
        self.ai_thread.start()

    def _calculate_move_thread(self, chess_engine_clone):
        self.calculated_move = self.dragon.get_move(chess_engine_clone, self.dragon_level)

    def player_won(self):
        if self.game_over_processed: return
        self.game_over_processed = True
        self.player.dragons_beaten += 1
        self.player.playing_chess = False
        self.player.can_move = True
        self.update_score(self.dragon_level)
    
    def player_lost(self):
        if self.game_over_processed: return
        self.game_over_processed = True
        self.player.lives -= 1
        self.player.playing_chess = False
        self.player.can_move = True
        print("Lost a Life! You can do it!")


    def update_score(self, difficulty):
        self.player.score += (difficulty + 1)*100
    
    def check_game_over(self, player):
        if self.chess_engine.is_checkmate():
            if self.chess_engine.white_turn:
                self.player_lost()
            else:
                self.player_won()
            return True
        elif self.chess_engine.is_stalemate():
            print("Good Progress! Try again!")
            player.playing_chess = False
            return True
        return False
                
import pygame as pg
from scene import Scene
from ui import UI_MANAGER, Button, Slider
from constants import WIDTH, HEIGHT

class StartScreen(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.manager = UI_MANAGER(game.graphic2d_surf)
        self.font = pg.font.Font(None, 60)
        self.small_font = pg.font.Font(None, 36)
        self.edit_mode = 0

        self.button_wall = self.manager.add_element(
            Button, "Edit Walls", on_click=lambda: self.set_mode(0),
            alignment='TOP CENTER_X', x_offset=-300, y_offset=160, width=150, toggle=False
        )
        self.button_portal = self.manager.add_element(
            Button, "Edit Portals", on_click=lambda: self.set_mode(1),
            alignment='TOP CENTER_X', x_offset=-140, y_offset=160, width=150, toggle=False
        )
        
        self.slider_r = self.manager.add_element(Slider, "Wall Red", alignment='TOP CENTER_X', 
                                                 x_offset=-220, y_offset=240, height=20, width=250, 
                                                 initial_val=0.3)
        self.slider_g = self.manager.add_element(Slider, "Wall Green", alignment='TOP CENTER_X',
                                                 x_offset=-220, y_offset=320, height=20, width=250,
                                                 initial_val=0.3)
        self.slider_b = self.manager.add_element(Slider, "Wall Blue", alignment='TOP CENTER_X', 
                                                 x_offset=-220, y_offset=400, height=20, width=250,
                                                 initial_val=0.3)

        self.slider_mode = self.manager.add_element(Slider, "CHESS PROBABILITY", alignment='TOP CENTER_X',
                                                     x_offset=220, y_offset=240, height=20, width=280,
                                                     initial_val=0.5)
        
        self.button_start = self.manager.add_element(Button, "Begin Game", on_click=self.start_game, 
                                                    alignment='BOTTOM CENTER_X', y_offset=-40, width=300,
                                                    height=60, ACTIVE_COLOR=(100, 255, 100))
        
        # DIFFICULTY SETTINGS
        self.slider_difficulty_chess = self.manager.add_element(
            Slider, "CHESS DIFFICULTY", alignment='TOP CENTER_X', x_offset=220, y_offset=320, height=20, width=280)
        self.slider_difficulty_fps = self.manager.add_element(
            Slider, "FPS DIFFICULTY", alignment='TOP CENTER_X', x_offset=220, y_offset=400, height=20, width=280)
        
        self.button_wall.is_active = True
    
    def set_mode(self, mode):
        self.edit_mode = mode
        self.button_wall.is_active = (mode == 0)
        self.button_portal.is_active  = (mode == 1)
        current_color = self.game.wall_color if mode == 0 else self.game.portal_color

        self.slider_r.value = current_color[0]
        self.slider_g.value = current_color[1]
        self.slider_b.value = current_color[2]
        self.slider_r.update_knob_pos()
        self.slider_g.update_knob_pos()
        self.slider_b.update_knob_pos()
        
        self.slider_mode.update_knob_pos() # HAVE TO CHECK IF THIS WILL WORK - DEBUG
    
    def start_game(self):
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        self.game.change_scene(self.game.maze_scene)
    
    def handle_event(self, event):
        self.manager.handle_event(event)
    
    def update(self):
        self.manager.update()
        r = self.slider_r.get_val(0, 1)
        g = self.slider_g.get_val(0, 1)
        b = self.slider_b.get_val(0, 1)

        # SET DIFFICULTY AND TIME LIMITS BASED ON SLIDERS
        self.game.player.chance_of_chess = round(self.slider_mode.get_val(0, 1), 3)
        self.game.player.time_limit_of_AI = round(self.slider_difficulty_chess.get_val(0.5,15.0), 2)
        self.game.player.time_limit_of_fps = round(self.slider_difficulty_fps.get_val(30.0,5.0), 2)
        self.game.player.fps_block_speed_multiplier = round(self.slider_difficulty_fps.get_val(0.1, 0.5), 2)    
        self.game.player.fps_block_size_multiplier = round(self.slider_difficulty_fps.get_val(1.5, 0.5), 2)
        
        #print(self.game.player.time_limit_of_AI)
        n_color = (r, g, b)
        if self.edit_mode == 0:
            self.game.wall_color = n_color
        else:
            self.game.portal_color = n_color
    
    def render(self):
        self.game.graphic2d_surf.fill((30, 30, 40))
        title = self.font.render("Dragon Chess Maze", True, (255, 215, 0))
        rect = title.get_rect(center=(WIDTH//2, 100))
        self.game.graphic2d_surf.blit(title, rect)

        looks_subtitle = self.small_font.render("LOOKS:", True, (255, 255, 255))
        looks_rect = looks_subtitle.get_rect(center=(WIDTH//2 - 220, 150))
        self.game.graphic2d_surf.blit(looks_subtitle, looks_rect)

        preview_color_box = (int(self.slider_r.get_val(0, 255)),
                             int(self.slider_g.get_val(0, 255)),
                             int(self.slider_b.get_val(0, 255)))
        
        preview_box_rect = pg.Rect(0, 0, 120, 100)
        preview_box_rect.center = (WIDTH//2 - 220, 552)
        pg.draw.rect(self.game.graphic2d_surf, preview_color_box, preview_box_rect, border_radius=10)
        pg.draw.rect(self.game.graphic2d_surf, (255, 255, 255), preview_box_rect, 3, border_radius=10)

        diff_txt = self.small_font.render("DIFFICULTY SETTINGS:", True, (255,255,255))
        diff_rect = diff_txt.get_rect(center=(WIDTH//2 + 220, 150))
        self.game.graphic2d_surf.blit(diff_txt, diff_rect)

        self.manager.draw()
        self.game.graphic3d.render_2d_surf(self.game.graphic2d_surf)

class EndScreen(Scene):
    def __init__(self, game, victory=True):
        super().__init__(game)
        self.manager = UI_MANAGER(game.graphic2d_surf)
        self.victory = victory
        self.font = pg.font.Font(None, 50)

        self.button_quit = self.manager.add_element(
            Button, "QUIT GAME!", on_click=self.quit_game, 
            alignment='CENTER_BOTH', y_offset=90, height=60
        )
        self.button_restart = self.manager.add_element(
            Button, "RETRY GAME!", on_click=self.retry_game, 
            alignment='CENTER_BOTH', y_offset=125, height=60
        )
    
    def quit_game(self):
        self.game.running = False

    def retry_game(self):
        self.game.retry = True
        self.game.running = False

    def handle_event(self, event):
        self.manager.handle_event(event)
    
    def update(self):
        self.manager.update()
    
    def render(self):
        self.game.graphic2d_surf.fill((0, 0, 0))
        msg = "VICTORY!" if self.victory else "GAME OVER! BETTER LUCK NEXT TIME!"
        color = (215, 215, 0) if self.victory else (200, 50, 50)

        text = self.font.render(msg, True, color)
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.game.graphic2d_surf.blit(text, rect)
        score_font = pg.font.Font(None, 50)
        score_text = score_font.render(f"Final Score: {self.game.player.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2+50))
        self.game.graphic2d_surf.blit(score_text, score_rect)

        self.manager.draw()
        self.game.graphic3d.render_2d_surf(self.game.graphic2d_surf)

import pygame as pg
import sys
from pathlib import Path
from constants import WIDTH, HEIGHT
from player import Player
from graphics import Graphics2d, Graphics3d
from map_gen import MapGen

base_path = Path(__file__).resolve().parent

class Game:
    def __init__(self):
        pg.init()
        self.is_fullscreen = False
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL | pg.DOUBLEBUF)

        self.clock = pg.time.Clock()
        icon_path = base_path / 'images' / 'white_queen.png'
        try:
            game_icon = pg.image.load(icon_path) 
            pg.display.set_icon(game_icon)
        except FileNotFoundError:
            print("Icon file not found.")
        pg.display.set_caption("Dragon Chess Maze")

        self.player = Player(start_pos=(2, 2))
        self.graphic3d = Graphics3d(self.screen)
        self.graphic2d_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA).convert_alpha()
        self.graphic2d = Graphics2d(self.graphic2d_surf, self.player)

        self.map_gen = MapGen(numBattles=25) # increase numBattles to make it easier to find a portal
        self.grid, self.portals = self.map_gen.generate_full()

        self.current_battle_pos = (0,0)
        self.current_scene = None
        self.running = True
        # custom color time!!! - one of my fav part after chess
        self.wall_color = (0.3, 0.3, 0.3)
        self.portal_color = (0.6, 0.6, 0.6)
        self.maze_scene = None
        self.player.time_limit_of_AI = 0
        self.retry = False

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pg.display.set_mode((0,0), pg.OPENGL | pg.DOUBLEBUF | pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
    
    def update_screen(self):
        import constants
        n_width, n_height = self.screen.get_size()
        constants.WIDTH, constants.HEIGHT = n_width, n_height
        self.graphic2d_surf = pg.Surface((n_width, n_height), pg.SRCALPHA).convert_alpha()
    def change_scene(self, new_scene):
        self.current_scene = new_scene
    
    def run(self):
        # MUTATION 11 HERE
        self.running = True
        while self.running:
            self.delta_time = self.clock.tick(60) / 1000.0

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                
                if self.current_scene:
                    self.current_scene.handle_event(event)
            
            if self.current_scene:
                self.current_scene.update()
                self.current_scene.render()
            
            pg.display.flip()
            if self.retry:
                return True
        return False
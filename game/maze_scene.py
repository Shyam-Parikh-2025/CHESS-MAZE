import pygame as pg
import random

from scene import Scene
from battle_scene import BattleScene
from taming_scene2 import TamingScene

class MazeScene(Scene):
    def handle_event(self, event):

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.event.set_grab(not pg.event.get_grab())
                pg.mouse.set_visible(not pg.mouse.get_visible())


    def update(self):
        game = self.game
        keys = pg.key.get_pressed()
        game.player.update(keys, game.grid, game.delta_time)

        r, c = int(game.player.pos[1]), int(game.player.pos[0])
        tile_val = game.grid[r, c]

        if tile_val == 3:
            game.current_battle_pos = (r, c)
            game.player.playing_chess = True
            if random.random() < game.player.chance_of_chess:
                game.change_scene(BattleScene(game))
            else:
                game.change_scene(TamingScene(game))
        
        elif tile_val == 4:
            if game.player.dragons_beaten >= 2:
                print("Time to fight the boss! You can do it!")
                game.current_battle_pos = (r, c)
                game.player.playing_chess = True

                total_dragons = game.map_gen.numBattles
                power_up = 0
                if game.player.dragons_beaten > 2:
                    power_up = min(game.player.dragons_beaten, 8)

                if random.random() <= game.player.chance_of_chess:
                    game.change_scene(BattleScene(game, is_boss=True, super_mode=power_up))
                else:
                    game.change_scene(TamingScene(game, is_boss=True))
            else:
                game.player.pos[0] -= 0.3
                game.player.pos[1] -= 0.3
                print("You have to defeat more dragons to be able to fight the boss!")

    
    def render(self):
        game = self.game

        game.graphic3d.update_view(game.player)
        game.graphic3d.render_maze(game.grid, game.wall_color, game.portal_color)

        game.graphic2d_surf.fill((0,0,0,0))
        game.graphic2d.draw_fps()
        game.graphic3d.render_2d_surf(game.graphic2d_surf)
    

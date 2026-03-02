from requirments import requirments
print("All the libraries needed are about to be installed: ")
requirments()

from game import Game
from maze_scene import MazeScene
from menu_scenes import StartScreen
import pygame as pg
import sys

def main():
    playing = True
    while playing:    
        game = Game()
        maze_scene = MazeScene(game)
        # print(game.map_gen) # FOR DEBUGGING AND DEVELOPER EASE ONLY (AKA WHEN WE HAD TO FIND A GAME TO PLAY EACH TIME)
        game.maze_scene = maze_scene
        start_screen = StartScreen(game)
        game.change_scene(start_screen)

        pg.event.set_grab(True)
        pg.mouse.set_visible(True)
        playing = game.run()
        if playing:
            pg.quit()
            pg.init()
    sys.exit()
if __name__ == "__main__":
    main()
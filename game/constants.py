import pygame as pg, moderngl as mgl, numpy as np

HEIGHT, WIDTH = 800, 1000
ROWS, COLS = 8, 8
SQSIZE = 100
color = {
    'light': '#EAFBC8',
    'dark': '#779A58'
}
colors = {

    'light_tile': '#EAFBC8', 
    'dark_tile':  '#779A58',  

    'wall':        '#1E1E1E',  
    'room':        '#FFFFFF', 
    'start':       '#4CAF50', 
    'battle':      '#E53935',  
    'boss_start':  '#6A1B9A',  
}
game_mode = {
    "Chess": 1,
    "Taming_Scene": 2
    # ... can always add more
}
BOSS_DRAG_LEVEL = 2
MINION_DRAG_LEVEL = 1
MAX_BOSS_DEPTH = 20
MAX_MINION_DEPTH = 1
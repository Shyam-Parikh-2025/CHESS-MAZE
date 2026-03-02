import pygame as pg
import numpy as np
from constants import game_mode

class Player:
    def __init__(self, start_pos, surface=None, radius=0.3):
        self.pos = np.array(start_pos, dtype=np.float32)
        self.playing_chess = False
        self.speed = 0.1
        self.radius = radius
        self.dragons_beaten = 0

        self.lives = 3
        self.score = 0
        
        self.can_move = True
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.mouse_sensitivity = 0.002
        
        # USED FOR SETTING DIFFICULTY BASED ON SLIDERS
        self.chance_of_chess = 0.5
        self.time_limit_of_AI = 0 # THIS IS FOR CHESS
        self.time_limit_of_fps = 0 # THIS IS FOR FPS
        self.fps_block_speed_multiplier = 1.0
        self.fps_block_size_multiplier = 1.0
        
    def angle_mouse(self):
        x, y = pg.mouse.get_rel()
        self.angle_x += x * self.mouse_sensitivity
        self.angle_y -= y * self.mouse_sensitivity
        self.angle_y = np.clip(self.angle_y, -np.pi / 2, np.pi / 2)

    def update(self, keys, grid, delta_time = 0.016):
        """
        Calculates movement based on the keyboard input and camera angle controlled
        by the mouse.
        
        Math (Trig):
        - Forward/Backward (W/S):  x += cos(angle), z += sin(angle), or x -= cos(angle), z -= sin(angle)
        - Strafing (A/D): Uses sin/cos offset by 90 degrees.
        
        Physics:
        - Movement is calculated tentatively (delta_x, delta_z).
        - Then passed to collision_checker to see if it hits a wall.
        """
        self.angle_mouse()
        sin_a = np.sin(self.angle_x)
        cos_a = np.cos(self.angle_x)
        actual_speed = (self.speed * 60.0) * delta_time

        delta_x = 0.0
        delta_z = 0.0
        if self.can_move:
            if keys[pg.K_w] or keys[pg.K_UP]:
                delta_x += actual_speed * cos_a
                delta_z += actual_speed * sin_a
            if keys[pg.K_s] or keys[pg.K_DOWN]:
                delta_x -= actual_speed * cos_a
                delta_z -= actual_speed * sin_a
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                delta_x += actual_speed * sin_a
                delta_z -= actual_speed * cos_a
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                delta_x -= actual_speed * sin_a
                delta_z += actual_speed * cos_a

            if delta_x != 0.0 and delta_z != 0.0:
                length = np.hypot(delta_x, delta_z)
                delta_x = delta_x / length
                delta_z = delta_z / length
                delta_x *= actual_speed
                delta_z *= actual_speed

        self.collision_checker(delta_x, delta_z, grid)

    def collision_checker(self, dx, dz, grid):
        """
        Collision Detection for player-grid interactions.
        
        Instead of checking the exact player mesh (which we did not do yet),
        we check if the player's center point + radius is in a grid cell with the
        value '1' (Wall). We update X and Z separately - allows sliding.
        """
        rows, cols = grid.shape

        to_be_x = self.pos[0] + dx
        n_x = int(np.clip(to_be_x + np.sign(dx) * self.radius, 0, cols - 1))
        n_y = int(np.clip(self.pos[1], 0, rows - 1))

        if grid[n_y, n_x] != 1:
            self.pos[0] = to_be_x

        to_be_z = self.pos[1] + dz
        n_x = int(np.clip(self.pos[0], 0, cols - 1))
        n_y = int(np.clip(to_be_z + np.sign(dz) * self.radius, 0, rows - 1))

        if grid[n_y, n_x] != 1:
            self.pos[1] = to_be_z

    def check_teleports(self, grid, portal_dict):
        rows, cols = grid.shape
        r = int(np.clip(self.pos[1], 0, rows - 1))
        c = int(np.clip(self.pos[0], 0, cols - 1))

        if grid[r, c] == 3:
            self.speed = 0
            self.playing_chess = True
            pg.mouse.get_rel()

import pygame as pg
import numpy as np
import math
import time
import random
from pyrr import matrix44
from scene import Scene
from battle_scene import BattleScene
from constants import WIDTH, HEIGHT
from menu_scenes import EndScreen
from queen_vbo import QUEEN_VBO
from king_vbo import KING_VBO
from rook_vbo import ROOK_VBO
# MAYBE ADD SLIDER AS TIME INDICATOR NXT

class Net:
    def __init__(self, start_pos, dir):
        self.start_pos = start_pos
        self.pos = np.array(self.start_pos, dtype=np.float32)
        self.dir = np.array(dir, dtype=np.float32)
        self.speed = 1.0
        self.radius = 1.0
        self.life_time = 60
        self.expanding = False
        self.max_expansion = 3.0
        self.active = True
    
    def update(self):
        if not self.expanding:
            self.pos += self.dir * self.speed
            distance = abs(np.linalg.norm(self.pos - self.start_pos))
            if distance > 200: self.active=False # MAYBE KEEP OR DISCARD
        else:
            self.radius = min(self.radius+0.3, self.max_expansion)
            if self.radius >= (self.max_expansion-0.2):
                self.active  = False
        self.life_time -= 1
    
    def check_collision(self, target_poss, target_hitbox:float=0.3):
        distances = np.linalg.norm(np.array(target_poss) - np.array(self.pos), axis=1)
        captures = np.where(distances < (self.radius + target_hitbox + 2.0))[0]
        if captures.size > 0:
            return True, np.array(target_poss)[captures], captures
        return False, None, None


class Target:
    def __init__(self, ctx, program, name, pos, hitbox, color, fmt='3f', size=1.0, attribute_names=['in_pos'],  vbo=None):
        self.name = name
        self.pos = np.array(pos, dtype='float32')
        self.hitbox = hitbox
        self.color = color
        self.captured = False
        self.program = program
        self.size = size
        self.vbo = vbo
        if self.vbo is None:
            vertices = np.array([
            # x, y, z
            -self.size, -self.size,  self.size,  self.size, -self.size,  self.size,  self.size,  self.size,  self.size, # Front
            -self.size, -self.size,  self.size,  self.size,  self.size,  self.size, -self.size,  self.size,  self.size,
            self.size, -self.size,  self.size,  self.size, -self.size, -self.size,  self.size,  self.size, -self.size, # Right
            self.size, -self.size,  self.size,  self.size,  self.size, -self.size,  self.size,  self.size,  self.size,
            self.size, -self.size, -self.size, -self.size, -self.size, -self.size, -self.size,  self.size, -self.size, # Back
            self.size, -self.size, -self.size, -self.size,  self.size, -self.size,  self.size,  self.size, -self.size,
            -self.size, -self.size, -self.size, -self.size, -self.size,  self.size, -self.size,  self.size,  self.size, # Left
            -self.size, -self.size, -self.size, -self.size,  self.size,  self.size, -self.size,  self.size, -self.size,
            -self.size,  self.size,  self.size,  self.size,  self.size,  self.size,  self.size,  self.size, -self.size, # Top
            -self.size,  self.size,  self.size,  self.size,  self.size, -self.size, -self.size,  self.size, -self.size,
            -self.size, -self.size, -self.size,  self.size, -self.size, -self.size,  self.size, -self.size,  self.size, # Bottom
            -self.size, -self.size, -self.size,  self.size, -self.size,  self.size, -self.size, -self.size,  self.size,
            ], dtype='float32')
        else:
            vertices = vbo.astype('float32')
        self.vbo = ctx.buffer(vertices)
        self.vao = ctx.vertex_array(program, [(self.vbo, fmt, *attribute_names)])
    
    def render(self):
        if not self.captured:
            model = matrix44.create_from_translation(self.pos)
            self.program["m_model"].write(model.astype("float32"))
            self.program["u_color"].value = self.color
            self.vao.render()

class TamingScene(Scene):
    def __init__(self, game, is_boss=False):
        super().__init__(game)
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        self.is_boss = is_boss
        # SETTING DIFFICULTY
        self.time_limit = float(self.game.player.time_limit_of_fps)
        if not (self.time_limit > 0): self.time_limit = 20.0
        self.size = 2.0 * self.game.player.fps_block_size_multiplier
        self.speed_mul = self.game.player.fps_block_speed_multiplier
        self.dragon_level = 1 if not is_boss else 1.5
        
        self.start_time = time.time()
        self.nets = []
        self.yaw = math.pi / 2.0
        self.pitch = 0.0
        self.camera_front = np.array([0.0, 0.0, 1.0], dtype='float32')
        self.crosshair_pos = [WIDTH // 2, HEIGHT // 2]
        self.mouse_sensitivity = 0.002
        self.targets = {}
        self.over_processed = False
        self.targets["Rook"]=Target(ctx=self.game.graphic3d.ctx,
                            program=self.game.graphic3d.prog,
                            name="Rook",
                            pos=[-5.0, 0.0, 15.0],
                            hitbox=self.size*2,
                            color=(0.0, 0.5, 1.0),
                            fmt='3f',
                            size=self.size,
                            attribute_names=['in_pos'],
                            vbo=ROOK_VBO
                            )

        self.targets["Queen"] = Target(
                                ctx=self.game.graphic3d.ctx,
                                program=self.game.graphic3d.prog,
                                name="Queen",
                                pos=[5.0, 2.0, 20.0],
                                hitbox=self.size*2,
                                color=(1.0, 0.0, 1.0),
                                fmt='3f',
                                size=self.size,
                                attribute_names=['in_pos'],
                                vbo=QUEEN_VBO
                            )

        self.targets["King"] = Target(
                                ctx=self.game.graphic3d.ctx,
                                program=self.game.graphic3d.prog,
                                name="King",
                                pos=[0.0, 0.0, 25.0],
                                hitbox=self.size*2,
                                color=(1.0, 0.8, 0.0),
                                fmt='3f',
                                size=self.size,
                                attribute_names=['in_pos'],
                                vbo=KING_VBO
                            )
        
        self.update_cam()
        self.dir_target = 1

    def update_cam(self):
        x = math.cos(self.yaw) * math.cos(self.pitch)
        y = math.sin(self.pitch)
        z = math.sin(self.yaw) * math.cos(self.pitch)
        self.camera_front = np.array([x, y, z], dtype='float32')
        self.camera_front /= np.linalg.norm(self.camera_front)
        eye = np.array([0.0, 0.0, 0.0], dtype='float32')
        up = np.array([0.0, 1.0, 0.0], dtype='float32')
        self.view = matrix44.create_look_at(eye, eye + self.camera_front, up)
                                            
    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            dx, dy = event.rel
            self.yaw += dx * self.mouse_sensitivity
            self.pitch -= dy * self.mouse_sensitivity

            self.pitch = max(-math.pi/2 + 0.1, min(math.pi/2 - 0.1, self.pitch))

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.shoot_net()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.event.set_grab(not pg.event.get_grab())
                pg.mouse.set_visible(not pg.mouse.get_visible())
    
    def shoot_net(self):
        net = Net([0.0, 0.0, 0.0], self.camera_front.copy())
        self.nets.append(net)
    
    def update(self):
        self.update_cam()
        time_left = max(0, self.time_limit - (time.time() - self.start_time))
        theta = time.time() * (1 + self.dragon_level*self.speed_mul)
        if abs(time_left % 10.0) < 0.1:
            self.dir_target = random.choice([1,-1])*self.dir_target
        rook, queen, king = self.targets["Rook"], self.targets["Queen"], self.targets["King"]
        if not rook.captured:
            rook.pos = np.array([-5.0 + 10.0 * math.sin(theta), 0.0, 15.0])
        if not queen.captured:
            queen.pos = np.array([8.0 * math.sin(theta * 1.5), 5.0 * math.cos(theta * 2.0), 15.0])
        if not king.captured:
            king.pos = np.array([4.0 * math.sin(theta * 3.0), 4.0 * math.cos(theta * 4.0), 15.0])
        
        for net in self.nets[:]:
            net.update()
            
            target_list = list(self.targets.values())
            positions = [t.pos for t in target_list]
            hit_bool, hit_pos, hit_indices = net.check_collision(positions)

            if hit_bool and not net.expanding:
                net.expanding = True
                for idx in hit_indices:
                    target_obj = target_list[idx]
                    if not target_obj.captured:
                        target_obj.captured = True
                        print(f"Captured the {target_obj.name}")
            if not net.active or net.life_time <= 0:
                if net in self.nets:
                    self.nets.remove(net)

            all_captured = all(target.captured for target in self.targets.values())
            if all_captured:
                self.finish_taming(victory=True)
            elif time_left <= 0:
                self.finish_taming(victory=False)

    def finish_taming(self, victory):
        if self.over_processed: return
        for target in self.targets.values():
            target.vbo.release()
            target.vao.release()
            
        if victory:
            print("One Dragon Tamed!")
            self.game.player.dragons_beaten += 1
            self.game.player.score += 200
            if self.is_boss:
                    pg.event.set_grab(False)
                    pg.mouse.set_visible(True)
                    self.game.change_scene(EndScreen(self.game, victory=True))
                    return
            r, c = self.game.current_battle_pos                
            self.game.grid[r, c] = 0
        else:
            print("Time ran out! You lost a life.")
            self.game.player.lives -= 1
            if self.game.player.lives <= 0:
                pg.event.set_grab(False)
                pg.mouse.set_visible(True)
                self.game.change_scene(EndScreen(self.game, victory=False))
                return
            self.game.player.pos[0] = 2.0
            self.game.player.pos[1] = 2.0
        self.over_processed = True
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        self.game.player.playing_chess = False
        if self.game.maze_scene is not None:
            self.game.change_scene(self.game.maze_scene)

    def render(self):
        game = self.game
        game.graphic3d.ctx.clear(0.05, 0.05, 0.1) 
        game.graphic3d.ctx.enable(game.graphic3d.ctx.DEPTH_TEST)
        aspect_ratio = game.screen.get_width() / game.screen.get_height()
        projection = matrix44.create_perspective_projection_matrix(45.0, aspect_ratio, 0.1, 100.0)
        game.graphic3d.prog["m_proj"].write(projection.astype("float32"))
        game.graphic3d.prog["m_view"].write(self.view.astype("float32"))
        for name, target in self.targets.items():
            target.render()
        
        for net in self.nets[:]:
            model = matrix44.create_from_translation(net.pos)
            scale = matrix44.create_from_scale(np.array([net.radius, net.radius, net.radius], dtype=np.float32))
            final_model = matrix44.multiply(scale, model)
            game.graphic3d.prog["m_model"].write(final_model.astype("float32"))
            game.graphic3d.prog["u_color"].value = (0.0, 1.0, 1.0)
            game.graphic3d.vao.render()
        
        surf = game.graphic2d_surf
        surf.fill((0, 0, 0, 0))
        cx = game.screen.get_width() // 2
        cy = game.screen.get_height() // 2
        pg.draw.line(surf, (255, 50, 50), (cx - 15, cy), (cx + 15, cy), 2)
        pg.draw.line(surf, (255, 50, 50), (cx, cy - 15), (cx, cy + 15), 2)
        
        elapsed = time.time() - self.start_time
        time_left = max(0, self.time_limit - elapsed)
        font = pg.font.Font(None, 40)
        timer_txt = font.render(f"Time: {time_left:.1f}s", True, (255, 255, 255))
        surf.blit(timer_txt, (20, 20))
        y_offset = 70

        for name, target_obj in self.targets.items():
            color = (0, 255, 0) if target_obj.captured else (100, 100, 100)
            status_txt = font.render(name, True, color)
            surf.blit(status_txt, (20, y_offset))
            y_offset += 40
        game.graphic3d.render_2d_surf(surf)

def get_ray_direction(mouse_x, mouse_y, width, height, view_matrix, projection_matrix):
    """Honestly, this is some math that I had to research on how to get, but it works by:
    - making the coords from the pg way to the moderngl way (btw -1 and 1)
    - uses the inverse matrix and matrix multiplication to undo what the rendering does.
    - returns direction"""
    x = (2.0 * mouse_x) / width - 1.0
    y = 1.0 - (2.0 * mouse_y) / height
    ray_clip = np.array([x, y, -1.0, 1.0])
    inv_view_proj = np.linalg.inv(projection_matrix @ view_matrix)
    ray_world = inv_view_proj @ ray_clip
    ray_world = ray_world[:3] / ray_world[3]
    direction = ray_world / np.linalg.norm(ray_world)
    return direction
import pygame
import src.config as config
from .ball import Ball

class Paladin(Ball):
    def __init__(self, x, y, space, name="Paladin", radius=config.BALL_RADIUS):
        self.tangential_scale = 1.0
        self.original_sprite = None
        super().__init__(x, y, space, name, color=config.COLOR_PALADIN, radius=radius)
        self.max_hp = config.PALADIN_HP
        self.hp = self.max_hp
        self.attack = config.PALADIN_ATTACK
        self.rotation_speed = config.PALADIN_ROTATION_SPEED

    def _setup_weapon(self, space):
        try:
            self.original_sprite = pygame.image.load("assets/shield.png").convert_alpha()
            self._rebuild_weapon()
        except Exception as e:
            print(f"Paladin failed to load sprite: {e}")
        
        if not self.weapon.shapes:
            # Hammer: Thick and heavy
            w, l = config.PALADIN_WEAPON_DIMS
            r = self.radius
            self.weapon.base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]
            self.weapon.create_shapes()

    def _rebuild_weapon(self):
        if not self.original_sprite: return
        
        target_size = self.radius * 2.5
        w, h = self.original_sprite.get_size()
        base_scale = target_size / max(w, h)
        
        new_w = max(1, int(w * base_scale))
        new_h = max(1, int(h * base_scale * self.tangential_scale))
        
        scaled = pygame.transform.scale(self.original_sprite, (new_w, new_h))
        self.weapon.build_composite([(scaled, (self.radius, 0))])

    def _rebuild_callback(self, space, key):
        self._rebuild_weapon()

    def on_hit(self, target):
        pass

    def on_clash(self, target):
        # Paladin Mechanic: Increase shield size and damage on clash
        self.attack *= 1.01
        self.tangential_scale += 0.05
        self.weapon.space.add_post_step_callback(self._rebuild_callback, self)

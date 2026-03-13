import pygame
import pymunk
import src.config as config
from .ball import Ball

class Rogue(Ball):
    def __init__(self, x, y, space, name="Rogue", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=config.COLOR_ROGUE, radius=radius)
        self.attack = config.ROGUE_ATTACK
        self.attack_speed = config.ROGUE_ATTACK_SPEED
        self.speed = config.ROGUE_SPEED
        self.rotation_speed = config.ROGUE_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Load Dagger
        try:
            surf = pygame.image.load("assets/dagger.png").convert_alpha()
        except Exception as e:
            print(f"Rogue failed to load dagger: {e}")
            super()._setup_weapon(space)
            return

        # Scale down (Rogue daggers are small)
        scale = (self.radius * 1.5) / max(surf.get_width(), surf.get_height())
        new_size = (int(surf.get_width() * scale), int(surf.get_height() * scale))
        dagger = pygame.transform.scale(surf, new_size)
        
        # Rotate 135 degrees to point outwards (Right)
        dagger = pygame.transform.rotate(dagger, 135)
        
        w, h = dagger.get_size()
        gap = -20
        
        # Positions relative to ball center
        x_offset = self.radius + w/2
        
        self.weapon.build_composite([
            (dagger, (x_offset, -h/2 - gap/2)), # Top
            (dagger, (x_offset, h/2 + gap/2))   # Bottom
        ])

    def on_hit(self, target):
        # Rogue Mechanic: Reset angle slightly to allow "double taps" or rapid stabs
        self.weapon_angle -= 0.5
        # Speed boost
        self.rotation_speed *= 1.05
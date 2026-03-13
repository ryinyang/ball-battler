import pygame
import pymunk
import src.config as config
from .ball import Ball

class Monk(Ball):
    def __init__(self, x, y, space, name="Monk", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=config.COLOR_MONK, radius=radius)
        self.max_hp = config.MONK_HP
        self.hp = self.max_hp
        self.attack = config.MONK_ATTACK
        self.attack_speed = config.MONK_ATTACK_SPEED
        self.speed = config.MONK_SPEED
        self.rotation_speed = config.MONK_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Load sprites
        try:
            fist_surf = pygame.image.load("assets/fist.png").convert_alpha()
            hand_surf = pygame.image.load("assets/hand.png").convert_alpha()
        except Exception as e:
            print(f"Monk failed to load sprites: {e}")
            super()._setup_weapon(space)
            return

        def prepare_surf(surf):
             size = self.radius
             s = size / max(surf.get_width(), surf.get_height())
             new_size = (int(surf.get_width() * s), int(surf.get_height() * s))
             return pygame.transform.scale(surf, new_size)

        fist = prepare_surf(fist_surf)
        hand = prepare_surf(hand_surf)
        
        offset_dist = self.radius
        
        # Right hand (Fist)
        fist_offset = (offset_dist + fist.get_width()/2, 0)
        # Left hand (Palm)
        hand_offset = (-offset_dist - hand.get_width()/2, 0)
        
        self.weapon.build_composite([
            (fist, fist_offset),
            (hand, hand_offset)
        ])

    def on_hit(self, target):
        # Monk Mechanic: Combo momentum (increase rotation speed temporarily)
        self.rotation_speed *= 1.1

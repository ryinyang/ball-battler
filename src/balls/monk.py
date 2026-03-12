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

        # Helper to scale
        def scale_surf(surf, size):
             s = size / max(surf.get_width(), surf.get_height())
             weapon_scale = 0.7
             s *= weapon_scale
             new_size = (int(surf.get_width() * s), int(surf.get_height() * s))
             return pygame.transform.scale(surf, new_size)

        # Scale to match radius roughly
        target_size = self.radius * 1.5
        fist = scale_surf(fist_surf, target_size)
        hand = scale_surf(hand_surf, target_size)
        
        # Create Composite
        w_fist, h_fist = fist.get_size()
        w_hand, h_hand = hand.get_size()
        offset_dist = self.radius
        
        total_w = int(w_hand + offset_dist * 2 + w_fist + 20)
        total_h = int(max(h_fist, h_hand) + 20)
        
        composite = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        cx, cy = total_w / 2, total_h / 2
        
        # Position Fist (Right)
        fist_pos = (cx + offset_dist, cy - h_fist/2)
        composite.blit(fist, fist_pos)
        
        # Position Hand (Left)
        hand_pos = (cx - offset_dist - w_hand, cy - h_hand/2)
        composite.blit(hand, hand_pos)
        
        self.weapon_image = composite
        self.weapon_image_offset = pymunk.Vec2d(0, 0)
        
        # Generate Geometry
        def get_shifted_outline(surf, pos):
            mask = pygame.mask.from_surface(surf)
            outline = mask.outline(every=2)
            return [(p[0] + pos[0] - cx, p[1] + pos[1] - cy) for p in outline]

        outline_f = get_shifted_outline(fist, fist_pos)
        outline_h = get_shifted_outline(hand, hand_pos)
        
        self.weapon_outline_vertices = [outline_f, outline_h]
        self.weapon_base_vertices = [self._get_convex_hull(outline_f), self._get_convex_hull(outline_h)]
        
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Monk Mechanic: Combo momentum (increase rotation speed temporarily)
        self.rotation_speed *= 1.1

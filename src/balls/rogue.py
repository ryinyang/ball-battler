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
        
        # Create Composite Surface for 2 Parallel Daggers
        w, h = dagger.get_size()
        gap = -20
        total_w, total_h = w, h * 2 + gap
        
        composite = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        composite.blit(dagger, (0, 0))          # Top Dagger
        composite.blit(dagger, (0, h + gap))    # Bottom Dagger
        
        self.weapon_image = composite
        
        # Offset calculation to position daggers at the edge of the ball
        cx, cy = total_w / 2, total_h / 2
        self.weapon_image_offset = pymunk.Vec2d(self.radius + cx, 0)
        
        # Generate Manual Physics Shapes and Outlines
        mask = pygame.mask.from_surface(dagger)
        outline = mask.outline(every=2)
        
        # Create shifted outlines for each dagger relative to the final composite center
        # Offset = (Relative Pos on Composite) - (Composite Center) + (Global Offset)
        offset_1 = pymunk.Vec2d(0, 0) - pymunk.Vec2d(cx, cy) + self.weapon_image_offset
        offset_2 = pymunk.Vec2d(0, h + gap) - pymunk.Vec2d(cx, cy) + self.weapon_image_offset
        
        outline1 = [(p[0] + offset_1.x, p[1] + offset_1.y) for p in outline]
        outline2 = [(p[0] + offset_2.x, p[1] + offset_2.y) for p in outline]
        
        self.weapon_outline_vertices = [outline1, outline2]
        self.weapon_base_vertices = [self._get_convex_hull(outline1), self._get_convex_hull(outline2)]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Rogue Mechanic: Reset angle slightly to allow "double taps" or rapid stabs
        self.weapon_angle -= 0.5
        # Speed boost
        self.rotation_speed *= 1.05
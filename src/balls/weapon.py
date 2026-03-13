import math
import pygame
import pymunk
import src.config as config

def get_convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1: return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

class Weapon:
    def __init__(self, ball, space):
        self.ball = ball
        self.space = space
        self.shapes = []
        self.base_vertices = []   # Physics vertices (local to weapon center/offset)
        self.outline_vertices = [] # Visual outlines
        
        # Render properties
        self.image = None
        self.image_offset = pymunk.Vec2d(0, 0)
        self.angle = 0.0

    def cleanup(self):
        if self.shapes:
            self.space.remove(*self.shapes)
            self.shapes = []

    def update(self, dt):
        self.angle += self.ball.rotation_speed * dt
        
        # Decouple weapon rotation from body rotation
        relative_angle = self.angle - self.ball.body.angle
        cos_a = math.cos(relative_angle)
        sin_a = math.sin(relative_angle)
        
        for i, shape in enumerate(self.shapes):
            if i >= len(self.base_vertices): break
            base_verts = self.base_vertices[i]
            # Rotate vertices around (0,0) which is the ball center in local space
            new_verts = [(x*cos_a - y*sin_a, x*sin_a + y*cos_a) for x, y in base_verts]
            shape.unsafe_set_vertices(new_verts)

    def create_default(self):
        w, l = config.WEAPON_WIDTH, config.WEAPON_LENGTH
        r = self.ball.radius
        # Define relative to ball center
        verts = [(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]
        self.base_vertices = [verts]
        self.image = None
        self.create_shapes()

    def load_sprite(self, path, max_size=None, offset=(0,0), rotation=0):
        try:
            surf = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Weapon failed to load sprite {path}: {e}")
            self.create_default()
            return

        if rotation != 0:
            surf = pygame.transform.rotate(surf, rotation)
        
        if max_size:
            scale = max_size / max(surf.get_width(), surf.get_height())
            new_size = (int(surf.get_width() * scale), int(surf.get_height() * scale))
            surf = pygame.transform.scale(surf, new_size)
        
        self.build_composite([(surf, offset)])

    def build_composite(self, parts):
        """
        parts: List of (surface, offset_from_center_vec)
        """
        if not parts: return

        # Calculate bounding box
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        for surf, off in parts:
            w, h = surf.get_size()
            x1 = off[0] - w/2
            y1 = off[1] - h/2
            min_x = min(min_x, x1)
            min_y = min(min_y, y1)
            max_x = max(max_x, x1 + w)
            max_y = max(max_y, y1 + h)

        total_w = int(max_x - min_x)
        total_h = int(max_y - min_y)
        
        composite = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        
        self.base_vertices = []
        self.outline_vertices = []

        for surf, off in parts:
            w, h = surf.get_size()
            # Pos in ball space (top-left of sprite)
            bx = off[0] - w/2
            by = off[1] - h/2
            
            # Blit onto composite (shift by min_x/min_y to align with surface origin)
            composite.blit(surf, (int(bx - min_x), int(by - min_y)))
            
            # Physics Shapes (Relative to Ball Center)
            mask = pygame.mask.from_surface(surf)
            outline = mask.outline(every=2)
            shifted_outline = [(p[0] + bx, p[1] + by) for p in outline]
            
            self.outline_vertices.append(shifted_outline)
            self.base_vertices.append(get_convex_hull(shifted_outline))

        self.image = composite
        # Image offset is vector from Ball Center to Surface Center
        self.image_offset = pymunk.Vec2d(min_x + total_w/2, min_y + total_h/2)
        self.create_shapes()

    def create_shapes(self):
        self.cleanup()
        for vertices in self.base_vertices:
            shape = pymunk.Poly(self.ball.body, vertices)
            shape.sensor = False
            shape.collision_type = config.COLLISION_TYPE_WEAPON
            shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_WEAPON, mask=config.MASK_WEAPON)
            shape.ball = self.ball
            self.space.add(shape)
            self.shapes.append(shape)

import math
import pygame
import pymunk
import src.config as config
from src.utilities import print_damage

class Ball:
    def __init__(self, x, y, space, name="Ball", color=config.COLOR_BALL_DEFAULT, radius=config.BALL_RADIUS):
        self.radius = radius
        moment = pymunk.moment_for_circle(config.BALL_MASS, 0, self.radius) # Calculate moment of inertia
        self.body = pymunk.Body(config.BALL_MASS, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = config.BALL_ELASTICITY
        self.shape.friction = config.BALL_FRICTION
        self.shape.collision_type = 1
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_BALL, mask=config.MASK_BALL)
        self.shape.ball = self
        space.add(self.body, self.shape)
        self.name = name
        self.color = color

        # Stats (Default / Base)
        self.max_hp = config.BALL_BASE_HP
        self.hp = self.max_hp
        self.attack = 10
        self.attack_speed = 1.0
        self.speed = 500
        self.flash_timer = 0.0
        self.weapon_flash_timer = 0.0
        self.stun_timer = 0.0

        # Weapon Setup
        self.weapon_angle = 0.0
        self.rotation_speed = 5.0 
        self.weapon_shapes = []
        self.weapon_image = None
        self.weapon_outline_vertices = []
        self.weapon_base_vertices = []
        self._setup_weapon(space)

    def _setup_weapon(self, space):
        """Override this in subclasses to define weapon shape and stats."""
        # Default: A simple stick
        w, l = config.WEAPON_WIDTH, config.WEAPON_LENGTH
        r = self.radius
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]
        self._create_weapon_shapes(space)

    def _create_weapon_shapes(self, space):
        if self.weapon_shapes:
            space.remove(*self.weapon_shapes)
            self.weapon_shapes = []
        
        for vertices in self.weapon_base_vertices:
            shape = pymunk.Poly(self.body, vertices)
            shape.sensor = False
            shape.collision_type = config.COLLISION_TYPE_WEAPON
            shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_WEAPON, mask=config.MASK_WEAPON)
            shape.ball = self
            space.add(shape)
            self.weapon_shapes.append(shape)

    def create_weapon_from_image(self, space, image_path, max_size=None, offset=None, rotation=0):
        """Loads an image, generates a hitbox from non-transparent pixels, and sets up the weapon."""
        try:
            surface = pygame.image.load(image_path).convert_alpha()
            if rotation != 0:
                surface = pygame.transform.rotate(surface, rotation)
            if max_size:
                scale = max_size / max(surface.get_width(), surface.get_height())
                new_size = (int(surface.get_width() * scale), int(surface.get_height() * scale))
                surface = pygame.transform.scale(surface, new_size)
        except Exception as e:
            print(f"Failed to load weapon image {image_path}: {e}")
            return

        self.weapon_image = surface
        self.weapon_image_offset = pymunk.Vec2d(*offset) if offset else pymunk.Vec2d(0, 0)
        
        # Generate mask and outline from non-transparent pixels
        mask = pygame.mask.from_surface(surface)
        outline = mask.outline(every=2) # Get outline points, skipping every 2nd for performance
        
        if not outline:
            return

        # Center the outline vertices relative to the image and apply offset
        w, h = surface.get_size()
        cx, cy = w / 2, h / 2
        off = self.weapon_image_offset
        centered_outline = [(p[0] - cx + off.x, p[1] - cy + off.y) for p in outline]
        
        # Store the raw outline for the visual highlight effect
        self.weapon_outline_vertices = centered_outline
        
        # Generate Convex Hull for Physics (Pymunk requires convex shapes)
        hull = self._get_convex_hull(centered_outline)
        self.weapon_base_vertices = [hull]
        
        self._create_weapon_shapes(space)

    def _get_convex_hull(self, points):
        """Computes the convex hull of a set of points using Monotone Chain algorithm."""
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

    def update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.weapon_flash_timer > 0:
            self.weapon_flash_timer -= dt

        if self.stun_timer > 0:
            self.stun_timer -= dt
            self.body.velocity = pymunk.Vec2d(0, 0)
            return

        # Clamp velocity to prevent tunneling
        if self.body.velocity.length > config.BALL_MAX_SPEED:
            self.body.velocity = self.body.velocity.normalized() * config.BALL_MAX_SPEED

        # Update weapon angle
        self.weapon_angle += self.rotation_speed * dt
        
        # Decouple weapon rotation from body rotation
        relative_angle = self.weapon_angle - self.body.angle
        cos_a = math.cos(relative_angle)
        sin_a = math.sin(relative_angle)
        
        # Rotate vertices in local space
        for i, shape in enumerate(self.weapon_shapes):
            base_verts = self.weapon_base_vertices[i]
            new_verts = [(x*cos_a - y*sin_a, x*sin_a + y*cos_a) for x, y in base_verts]
            shape.unsafe_set_vertices(new_verts)

    def on_hit(self, target):
        """Override for class-specific on-hit logic."""
        pass

    def on_clash(self, target):
        """Override for class-specific clash logic."""
        pass

    def take_damage(self, amount):
        self.hp -= amount

    def deal_hit(self, target, weapon_shape):
        # Trap Handling
        if hasattr(weapon_shape, 'trap'):
            weapon_shape.trap.trigger(target)
            return True

        # Damage Calculation
        damage = self.attack
        print_damage(self, target, damage)
        target.take_damage(damage)
        self.on_hit(target)
        target.flash_timer = config.BALL_FLASH_DURATION
        self.weapon_flash_timer = config.BALL_FLASH_DURATION

        is_projectile = hasattr(weapon_shape, 'projectile')

        # Physics Responses (Knockback / Recoil)
        if is_projectile:
            direction = weapon_shape.body.velocity.normalized()
            weapon_shape.projectile.destroy()
            if hasattr(self, 'projectiles') and weapon_shape.projectile in self.projectiles:
                self.projectiles.remove(weapon_shape.projectile)
        else:
            direction = (target.body.position - self.body.position).normalized()
            self.body.apply_impulse_at_local_point(-direction * config.RECOIL_IMPULSE)
            self.rotation_speed *= -1

        target.body.apply_impulse_at_local_point(direction * config.KNOCKBACK_IMPULSE)
        return True

import math
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
        self.stun_timer = 0.0

        # Weapon Setup
        self.weapon_angle = 0.0
        self.rotation_speed = 5.0 
        self.weapon_shapes = []
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

    def update(self, dt):
        if self.stun_timer > 0:
            self.stun_timer -= dt
            self.body.velocity = pymunk.Vec2d(0, 0)
            return

        # Clamp velocity to prevent tunneling
        if self.body.velocity.length > config.BALL_MAX_SPEED:
            self.body.velocity = self.body.velocity.normalized() * config.BALL_MAX_SPEED

        if self.flash_timer > 0:
            self.flash_timer -= dt

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
        self.flash_timer = config.BALL_FLASH_DURATION

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

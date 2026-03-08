import math
import pymunk

class Ball:
    def __init__(self, x, y, space, name="Ball"):
        mass = 10
        radius = 15
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.999999999999
        self.shape.friction = 0.5
        self.shape.collision_type = 1
        self.shape.ball = self
        space.add(self.body, self.shape)
        self.name = name

        # Phase 3.2: Weapon Setup (Decoupled Rotation)
        self.weapon_angle = 0.0
        self.rotation_speed = 5.0  # Radians/sec
        
        # Define base vertices for the weapon (offset from center)
        # A rectangle 10x40, offset by radius (15)
        w, l, r = 10, 40, 15
        self.weapon_base_vertices = [(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]
        
        self.weapon_shape = pymunk.Poly(self.body, self.weapon_base_vertices)
        self.weapon_shape.sensor = True
        self.weapon_shape.collision_type = 2
        self.weapon_shape.ball = self
        space.add(self.weapon_shape)

        # Stats
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 5
        self.attack_speed = 1.0  # Cooldown duration in seconds
        self.speed = 500         # Movement impulse
        self.cooldown = 0.0      # Current cooldown timer
        self.flash_timer = 0.0   # Visual flash on hit

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Update weapon angle
        self.weapon_angle += self.rotation_speed * dt
        
        # Decouple weapon rotation from body rotation
        relative_angle = self.weapon_angle - self.body.angle
        cos_a = math.cos(relative_angle)
        sin_a = math.sin(relative_angle)
        
        # Rotate vertices in local space
        new_verts = [(x*cos_a - y*sin_a, x*sin_a + y*cos_a) for x, y in self.weapon_base_vertices]
        self.weapon_shape.unsafe_set_vertices(new_verts)

    def on_hit(self, target):
        pass

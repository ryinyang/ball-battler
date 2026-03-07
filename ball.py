import pymunk

class Ball:
    def __init__(self, x, y, space):
        mass = 10
        radius = 15
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.9
        self.shape.friction = 0.5
        self.shape.collision_type = 1
        self.shape.ball = self
        space.add(self.body, self.shape)

        # Stats
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 5
        self.attack_speed = 1.0  # Cooldown duration in seconds
        self.speed = 500         # Movement impulse
        self.cooldown = 0.0      # Current cooldown timer

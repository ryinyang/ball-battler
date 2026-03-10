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
        # Dagger: Short and thin
        w, l = config.ROGUE_WEAPON_DIMS
        r = self.radius
        self.weapon_base_vertices = [[(r, -w/2), (r+l, 0), (r, w/2)]] # Triangle tip
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Rogue Mechanic: Reset angle slightly to allow "double taps" or rapid stabs
        self.weapon_angle -= 0.5
        # Speed boost
        self.rotation_speed *= 1.05
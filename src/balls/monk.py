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
        # Fist: A simple square/box
        w, l = config.MONK_WEAPON_DIMS
        r = self.radius
        fist1 = [(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]
        fist2 = [(-r, -w/2), (-(r+l), -w/2), (-(r+l), w/2), (-r, w/2)]
        self.weapon_base_vertices = [fist1, fist2]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Monk Mechanic: Combo momentum (increase rotation speed temporarily)
        self.rotation_speed *= 1.1

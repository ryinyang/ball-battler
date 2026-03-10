import src.config as config
from .ball import Ball

class Paladin(Ball):
    def __init__(self, x, y, space, name="Paladin", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=config.COLOR_PALADIN, radius=radius)
        self.max_hp = config.PALADIN_HP
        self.hp = self.max_hp
        self.attack = config.PALADIN_ATTACK
        self.rotation_speed = config.PALADIN_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Hammer: Thick and heavy
        w, l = config.PALADIN_WEAPON_DIMS
        r = self.radius
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Paladin Mechanic: Fortify Health on hit
        self.max_hp += 5
        self.hp += 5

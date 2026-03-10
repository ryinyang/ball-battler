import src.config as config
from .ball import Ball

class Berserker(Ball):
    def __init__(self, x, y, space, name="Berserker", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=config.COLOR_BERSERKER, radius=radius)
        self.max_hp = config.BERSERKER_HP
        self.hp = self.max_hp
        self.attack = config.BERSERKER_ATTACK
        self.rotation_speed = config.BERSERKER_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Axe: Wide and long
        w, l = config.BERSERKER_WEAPON_DIMS
        r = self.radius
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w), (r+l, w), (r, w/2)]]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Berserker Mechanic: Heal slightly on hit
        self.hp = min(self.max_hp, self.hp + 5)

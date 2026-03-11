import src.config as config
from .ball import Ball

class Paladin(Ball):
    def __init__(self, x, y, space, name="Paladin", radius=config.BALL_RADIUS):
        self.weapon_width, self.weapon_length = config.PALADIN_WEAPON_DIMS
        super().__init__(x, y, space, name, color=config.COLOR_PALADIN, radius=radius)
        self.max_hp = config.PALADIN_HP
        self.hp = self.max_hp
        self.attack = config.PALADIN_ATTACK
        self.rotation_speed = config.PALADIN_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Hammer: Thick and heavy
        w, l = self.weapon_width, self.weapon_length
        r = self.radius
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        pass

    def on_clash(self, target):
        # Paladin Mechanic: Increase shield size on clash
        self.weapon_width *= 1.1
        if self.weapon_width > config.PALADIN_MAX_SHIELD_WIDTH:
            self.weapon_width = config.PALADIN_MAX_SHIELD_WIDTH
        w, l = self.weapon_width, self.weapon_length
        r = self.radius
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]

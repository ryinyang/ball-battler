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
        # Attempt to load sprite
        self.weapon.load_sprite("assets/shield.png", max_size=self.radius * 2.5, offset=(self.radius, 0))
        
        if not self.weapon.shapes:
            # Hammer: Thick and heavy
            w, l = config.PALADIN_WEAPON_DIMS
            r = self.radius
            self.weapon.base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]
            self.weapon.create_shapes()

    def on_hit(self, target):
        pass

    def on_clash(self, target):
        # Paladin Mechanic: Increase shield size on clash (Disabled for sprite)
        pass

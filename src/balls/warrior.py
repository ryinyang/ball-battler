import src.config as config
from .ball import Ball

class Warrior(Ball):
    def __init__(self, x, y, space, name="Warrior", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=config.COLOR_WARRIOR, radius=radius)
        self.max_hp = config.WARRIOR_HP
        self.hp = self.max_hp
        self.attack = config.WARRIOR_ATTACK
        self.rotation_speed = config.WARRIOR_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Sword: Blade + Crossguard
        w, l = config.WARRIOR_WEAPON_DIMS
        r = self.radius
        
        # Blade
        blade = [(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]
        
        # Crossguard
        guard_w = w * 3
        guard_l = 10
        guard = [(r, -guard_w/2), (r+guard_l, -guard_w/2), (r+guard_l, guard_w/2), (r, guard_w/2)]
        
        self.weapon_base_vertices = [blade, guard]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Warrior Mechanic: Battle Hardened - Increase attack on hit
        self.attack += 1
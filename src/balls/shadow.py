import src.config as config
from src.utilities import print_damage
from .ball import Ball

class Shadow(Ball):
    def __init__(self, x, y, space, name="Shadow", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=config.COLOR_SHADOW, radius=radius)
        self.max_hp = config.SHADOW_HP
        self.hp = self.max_hp
        self.aoe_radius = config.SHADOW_AOE_RADIUS
        self.current_dps = config.SHADOW_BASE_DPS
        self.rotation_speed = 0 # Hands don't spin independently
        self.space = space
        self.aoe_timer = 0.0

    def _setup_weapon(self, space):
        # Clasped hands: A Square held in front
        size = 24
        r = self.radius
        offset = r + size / 2
        
        # Square vertices centered at (offset, 0)
        half = size / 2
        self.weapon_base_vertices = [[
            (offset - half, -half),
            (offset + half, -half),
            (offset + half, half),
            (offset - half, half)
        ]]
        self._create_weapon_shapes(space)

    def deal_hit(self, target, weapon_shape):
        # Shadow does not deal damage via weapon hits (hands are for blocking/pushing)
        return False

    def update(self, dt):
        # Lock weapon angle to body angle so hands rotate with the character (shield-like)
        self.weapon_angle = self.body.angle
        
        super().update(dt)
        
        # Scale DPS
        self.current_dps += config.SHADOW_DPS_SCALING * dt
        
        # Apply AOE Damage every second
        self.aoe_timer += dt
        if self.aoe_timer >= 1.0:
            self.aoe_timer = 0.0
            # Efficiently query for shapes near the Shadow
            for shape in self.space.shapes:
                # Check if shape is a ball (and not self)
                if hasattr(shape, 'ball') and shape.ball != self and not hasattr(shape, 'weapon'):
                    # Check distance
                    dist = (shape.body.position - self.body.position).length
                    if dist < self.aoe_radius + shape.radius:
                        damage = self.current_dps
                        print_damage(self, shape.ball, damage)
                        shape.ball.take_damage(damage)

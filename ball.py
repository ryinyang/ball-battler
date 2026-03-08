import math
import pymunk
import config

class Ball:
    def __init__(self, x, y, space, name="Ball", color=(255, 0, 0)):
        mass = 10
        radius = 15
        moment = pymunk.moment_for_circle(mass, 0, radius) # Calculate moment of inertia
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.999999999999
        self.shape.friction = 0.5
        self.shape.collision_type = 1
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_BALL, mask=config.MASK_BALL)
        self.shape.ball = self
        space.add(self.body, self.shape)
        self.name = name
        self.color = color

        # Stats (Default / Base)
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack = 10
        self.defense = 5
        self.attack_speed = 1.0
        self.speed = 500
        self.flash_timer = 0.0

        # Weapon Setup
        self.weapon_angle = 0.0
        self.rotation_speed = 5.0 
        self.weapon_shapes = []
        self.weapon_base_vertices = []
        self._setup_weapon(space)

    def _setup_weapon(self, space):
        """Override this in subclasses to define weapon shape and stats."""
        # Default: A simple stick
        w, l, r = 10, 40, 15
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]
        self._create_weapon_shapes(space)

    def _create_weapon_shapes(self, space):
        if self.weapon_shapes:
            space.remove(*self.weapon_shapes)
            self.weapon_shapes = []
        
        for vertices in self.weapon_base_vertices:
            shape = pymunk.Poly(self.body, vertices)
            shape.sensor = False
            shape.collision_type = config.COLLISION_TYPE_WEAPON
            shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_WEAPON, mask=config.MASK_WEAPON)
            shape.ball = self
            space.add(shape)
            self.weapon_shapes.append(shape)

    def update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Update weapon angle
        self.weapon_angle += self.rotation_speed * dt
        
        # Decouple weapon rotation from body rotation
        relative_angle = self.weapon_angle - self.body.angle
        cos_a = math.cos(relative_angle)
        sin_a = math.sin(relative_angle)
        
        # Rotate vertices in local space
        for i, shape in enumerate(self.weapon_shapes):
            base_verts = self.weapon_base_vertices[i]
            new_verts = [(x*cos_a - y*sin_a, x*sin_a + y*cos_a) for x, y in base_verts]
            shape.unsafe_set_vertices(new_verts)

    def on_hit(self, target):
        """Override for class-specific on-hit logic."""
        pass

class Rogue(Ball):
    def __init__(self, x, y, space, name="Rogue"):
        super().__init__(x, y, space, name, color=config.COLOR_ROGUE)
        self.attack = config.ROGUE_ATTACK
        self.defense = config.ROGUE_DEFENSE
        self.attack_speed = config.ROGUE_ATTACK_SPEED
        self.speed = config.ROGUE_SPEED
        self.rotation_speed = config.ROGUE_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Dagger: Short and thin
        w, l, r = config.ROGUE_WEAPON_DIMS
        self.weapon_base_vertices = [[(r, -w/2), (r+l, 0), (r, w/2)]] # Triangle tip
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Rogue Mechanic: Reset angle slightly to allow "double taps" or rapid stabs
        self.weapon_angle -= 0.5
        # Speed boost
        self.rotation_speed *= 1.05

class Berserker(Ball):
    def __init__(self, x, y, space, name="Berserker"):
        super().__init__(x, y, space, name, color=config.COLOR_BERSERKER)
        self.max_hp = config.BERSERKER_HP
        self.hp = self.max_hp
        self.attack = config.BERSERKER_ATTACK
        self.defense = config.BERSERKER_DEFENSE
        self.rotation_speed = config.BERSERKER_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Axe: Wide and long
        w, l, r = config.BERSERKER_WEAPON_DIMS
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w), (r+l, w), (r, w/2)]]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Berserker Mechanic: Heal slightly on hit
        self.hp = min(self.max_hp, self.hp + 5)

class Paladin(Ball):
    def __init__(self, x, y, space, name="Paladin"):
        super().__init__(x, y, space, name, color=config.COLOR_PALADIN)
        self.max_hp = config.PALADIN_HP
        self.hp = self.max_hp
        self.attack = config.PALADIN_ATTACK
        self.defense = config.PALADIN_DEFENSE
        self.rotation_speed = config.PALADIN_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Hammer: Thick and heavy
        w, l, r = config.PALADIN_WEAPON_DIMS
        self.weapon_base_vertices = [[(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Paladin Mechanic: Fortify Defense on hit
        self.defense += 1

class Monk(Ball):
    def __init__(self, x, y, space, name="Monk"):
        super().__init__(x, y, space, name, color=config.COLOR_MONK)
        self.hp = config.MONK_HP
        self.attack = config.MONK_ATTACK
        self.defense = config.MONK_DEFENSE
        self.attack_speed = config.MONK_ATTACK_SPEED
        self.speed = config.MONK_SPEED
        self.rotation_speed = config.MONK_ROTATION_SPEED

    def _setup_weapon(self, space):
        # Fist: A simple square/box
        w, l, r = config.MONK_WEAPON_DIMS
        fist1 = [(r, -w/2), (r+l, -w/2), (r+l, w/2), (r, w/2)]
        fist2 = [(-r, -w/2), (-(r+l), -w/2), (-(r+l), w/2), (-r, w/2)]
        self.weapon_base_vertices = [fist1, fist2]
        self._create_weapon_shapes(space)

    def on_hit(self, target):
        # Monk Mechanic: Combo momentum (increase rotation speed temporarily)
        self.rotation_speed *= 1.1

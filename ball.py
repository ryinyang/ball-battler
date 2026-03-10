import math
import pymunk
import config

class Ball:
    def __init__(self, x, y, space, name="Ball", color=config.COLOR_BALL_DEFAULT, radius=config.BALL_RADIUS):
        self.radius = radius
        moment = pymunk.moment_for_circle(config.BALL_MASS, 0, self.radius) # Calculate moment of inertia
        self.body = pymunk.Body(config.BALL_MASS, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = config.BALL_ELASTICITY
        self.shape.friction = config.BALL_FRICTION
        self.shape.collision_type = 1
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_BALL, mask=config.MASK_BALL)
        self.shape.ball = self
        space.add(self.body, self.shape)
        self.name = name
        self.color = color

        # Stats (Default / Base)
        self.max_hp = config.BALL_BASE_HP
        self.hp = self.max_hp
        self.attack = 10
        self.attack_speed = 1.0
        self.speed = 500
        self.flash_timer = 0.0
        self.stun_timer = 0.0

        # Weapon Setup
        self.weapon_angle = 0.0
        self.rotation_speed = 5.0 
        self.weapon_shapes = []
        self.weapon_base_vertices = []
        self._setup_weapon(space)

    def _setup_weapon(self, space):
        """Override this in subclasses to define weapon shape and stats."""
        # Default: A simple stick
        w, l = config.WEAPON_WIDTH, config.WEAPON_LENGTH
        r = self.radius
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
        if self.stun_timer > 0:
            self.stun_timer -= dt
            self.body.velocity = pymunk.Vec2d(0, 0)
            return

        # Clamp velocity to prevent tunneling
        if self.body.velocity.length > config.BALL_MAX_SPEED:
            self.body.velocity = self.body.velocity.normalized() * config.BALL_MAX_SPEED

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

class Arrow:
    def __init__(self, x, y, angle, space, owner):
        self.owner = owner
        self.space = space
        self.lifetime = 1.5

        mass = 0.05
        size = (30, 5)
        moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.body.angle = angle
        speed = 800
        self.body.velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

        self.shape = pymunk.Poly.create_box(self.body, size)
        self.shape.sensor = True
        self.shape.collision_type = config.COLLISION_TYPE_WEAPON
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_WEAPON, mask=config.MASK_WEAPON)
        self.shape.ball = owner
        self.shape.projectile = self

        space.add(self.body, self.shape)

    def update(self, dt):
        self.lifetime -= dt

    def destroy(self):
        if self.body in self.space.bodies:
            self.space.remove(self.body, self.shape)

class Trap:
    def __init__(self, x, y, space, owner):
        self.owner = owner
        self.space = space
        
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x, y)
        
        size = 20
        self.shape = pymunk.Poly.create_box(self.body, (size, size))
        self.shape.sensor = True
        self.shape.collision_type = config.COLLISION_TYPE_WEAPON
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_WEAPON, mask=config.MASK_WEAPON)
        self.shape.ball = owner
        self.shape.trap = self
        
        space.add(self.body, self.shape)

    def destroy(self):
        if self.body in self.space.bodies:
            self.space.remove(self.body, self.shape)

class Ranger(Ball):
    def __init__(self, x, y, space, name="Ranger", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=(34, 139, 34), radius=radius)
        self.projectiles = []
        self.traps = []
        self.fire_rate = 0.1
        self.fire_timer = 0.0
        self.trap_cooldown = 3.0
        self.trap_timer = 0.0
        self.attack = 12
        self.speed = 400
        self.rotation_speed = 3.0
        self.space = space

    def _setup_weapon(self, space):
        w, l = 5, 40
        r = self.radius
        self.weapon_base_vertices = [[(r, -l/2), (r+w, -l/2), (r+w, l/2), (r, l/2)]]
        self._create_weapon_shapes(space)

    def update(self, dt):
        super().update(dt)
        if self.stun_timer > 0:
            return

        self.trap_timer -= dt
        if self.trap_timer <= 0:
            self.trap_timer = self.trap_cooldown
            self.lay_trap()

        self.fire_timer -= dt
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            self.shoot()

        for p in self.projectiles[:]:
            p.update(dt)
            if p.lifetime <= 0:
                p.destroy()
                if p in self.projectiles:
                    self.projectiles.remove(p)

    def lay_trap(self):
        if len(self.traps) >= 2:
            oldest = self.traps.pop(0)
            oldest.destroy()
        
        t = Trap(self.body.position.x, self.body.position.y, self.space, self)
        self.traps.append(t)

    def shoot(self):
        angle = self.weapon_angle
        spawn_dist = self.radius + 15
        x = self.body.position.x + math.cos(angle) * spawn_dist
        y = self.body.position.y + math.sin(angle) * spawn_dist
        arrow = Arrow(x, y, angle, self.body.space, self)
        self.projectiles.append(arrow)

    def on_hit(self, target):
        # Ranger Mechanic: Kiting - Speed boost on hit
        self.speed *= 1.05

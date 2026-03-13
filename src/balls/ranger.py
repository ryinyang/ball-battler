import math
import pymunk
import src.config as config
from .ball import Ball

class Arrow:
    def __init__(self, x, y, angle, space, owner):
        self.owner = owner
        self.space = space
        self.lifetime = config.RANGER_ARROW_LIFETIME

        mass = config.RANGER_ARROW_MASS
        size = config.RANGER_ARROW_SIZE
        moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.body.angle = angle
        speed = config.RANGER_ARROW_SPEED
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
        
        size = config.RANGER_TRAP_SIZE
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

    def trigger(self, target):
        print(f"{self.owner.name}'s Trap hit {target.name}!")
        target.take_damage(config.RANGER_TRAP_DAMAGE)
        target.flash_timer = config.BALL_FLASH_DURATION
        target.stun_timer = config.RANGER_TRAP_STUN_DURATION
        self.destroy()
        if self in self.owner.traps:
            self.owner.traps.remove(self)

class Ranger(Ball):
    def __init__(self, x, y, space, name="Ranger", radius=config.BALL_RADIUS):
        super().__init__(x, y, space, name, color=config.COLOR_RANGER, radius=radius)
        self.projectiles = []
        self.traps = []
        self.fire_rate = config.RANGER_FIRE_RATE
        self.fire_timer = 0.0
        self.trap_cooldown = config.RANGER_TRAP_COOLDOWN
        self.trap_timer = 0.0
        self.attack = config.RANGER_ATTACK
        self.speed = config.RANGER_SPEED
        self.rotation_speed = config.RANGER_ROTATION_SPEED
        self.space = space

    def _setup_weapon(self, space):
        # Attempt to load sprite
        self.weapon.load_sprite("assets/bow.png", max_size=self.radius * 2.5, offset=(self.radius, 0), rotation=-45)
        
        if not self.weapon.shapes:
            w, l = 5, 40
            r = self.radius
            self.weapon.base_vertices = [[(r, -l/2), (r+w, -l/2), (r+w, l/2), (r, l/2)]]
            self.weapon.create_shapes()

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
        self.fire_rate *= 0.99
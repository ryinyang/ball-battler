import math
import pymunk
import src.config as config
from .ball import Ball

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

    def trigger(self, target):
        print(f"{self.owner.name}'s Trap hit {target.name}!")
        target.take_damage(5)
        target.stun_timer = 1.0
        self.destroy()
        if self in self.owner.traps:
            self.owner.traps.remove(self)

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
        self.fire_rate *= 0.99
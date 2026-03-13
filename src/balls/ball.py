import math
import pygame
import pymunk
import src.config as config
from src.utilities import print_damage
from .weapon import Weapon

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
        self.weapon_flash_timer = 0.0
        self.stun_timer = 0.0

        self.rotation_speed = 5.0
        self.weapon = Weapon(self, space)
        self._setup_weapon(space)

    @property
    def weapon_shapes(self):
        return self.weapon.shapes

    @property
    def weapon_image(self):
        return self.weapon.image

    @property
    def weapon_image_offset(self):
        return self.weapon.image_offset
    
    @property
    def weapon_angle(self):
        return self.weapon.angle

    @weapon_angle.setter
    def weapon_angle(self, value):
        self.weapon.angle = value

    @property
    def weapon_outline_vertices(self):
        return self.weapon.outline_vertices

    def _setup_weapon(self, space):
        """Override this in subclasses to define weapon shape and stats."""
        self.weapon.create_default()

    def create_weapon_from_image(self, space, image_path, max_size=None, offset=None, rotation=0):
        self.weapon.load_sprite(image_path, max_size, offset if offset else (0,0), rotation)

    def update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.weapon_flash_timer > 0:
            self.weapon_flash_timer -= dt

        if self.stun_timer > 0:
            self.stun_timer -= dt
            self.body.velocity = pymunk.Vec2d(0, 0)
            return

        # Clamp velocity to prevent tunneling
        if self.body.velocity.length > config.BALL_MAX_SPEED:
            self.body.velocity = self.body.velocity.normalized() * config.BALL_MAX_SPEED

        self.weapon.update(dt)

    def on_hit(self, target):
        """Override for class-specific on-hit logic."""
        pass

    def on_clash(self, target):
        """Override for class-specific clash logic."""
        pass

    def take_damage(self, amount):
        self.hp -= amount

    def deal_hit(self, target, weapon_shape):
        # Trap Handling
        if hasattr(weapon_shape, 'trap'):
            weapon_shape.trap.trigger(target)
            return True

        # Damage Calculation
        damage = self.attack
        print_damage(self, target, damage)
        target.take_damage(damage)
        self.on_hit(target)
        target.flash_timer = config.BALL_FLASH_DURATION
        self.weapon_flash_timer = config.BALL_FLASH_DURATION

        is_projectile = hasattr(weapon_shape, 'projectile')

        # Physics Responses (Knockback / Recoil)
        if is_projectile:
            direction = weapon_shape.body.velocity.normalized()
            weapon_shape.projectile.destroy()
            if hasattr(self, 'projectiles') and weapon_shape.projectile in self.projectiles:
                self.projectiles.remove(weapon_shape.projectile)
        else:
            direction = (target.body.position - self.body.position).normalized()
            self.body.apply_impulse_at_local_point(-direction * config.RECOIL_IMPULSE)
            self.rotation_speed *= -1

        target.body.apply_impulse_at_local_point(direction * config.KNOCKBACK_IMPULSE)
        return True

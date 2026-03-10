import math
import pygame
import pymunk
import config

class Anomaly:
    def __init__(self, space, x, y, duration=0):
        self.space = space
        self.x = x
        self.y = y
        self.duration = duration
        self.timer = 0.0
        self.finished = False

    def update(self, dt, balls):
        self.timer += dt
        if self.duration > 0 and self.timer >= self.duration:
            self.finished = True

    def draw(self, screen):
        pass

class BlackHole(Anomaly):
    def __init__(self, space, center_x, center_y):
        super().__init__(space, center_x, center_y, duration=config.BLACK_HOLE_DURATION)
        self.center_x = center_x
        self.center_y = center_y
        self.current_x = center_x
        self.current_y = center_y
        self.angle = 0.0
        self.color = config.COLOR_BLACK_HOLE
        self.start_delay = config.BLACK_HOLE_START_DELAY
        self.is_active = False

    def update(self, dt, balls):
        if not self.is_active:
            self.start_delay -= dt
            if self.start_delay <= 0:
                self.is_active = True
            return

        super().update(dt, balls)

        # Move in a circle around the center
        self.angle += config.BLACK_HOLE_SPEED * dt
        self.current_x = self.center_x + math.cos(self.angle) * config.BLACK_HOLE_PATH_RADIUS
        self.current_y = self.center_y + math.sin(self.angle) * config.BLACK_HOLE_PATH_RADIUS

        bh_pos = pymunk.Vec2d(self.current_x, self.current_y)

        # Apply strong attraction force to all balls
        for ball in balls:
            dist_vec = bh_pos - ball.body.position
            dist_sq = dist_vec.length_squared
            if dist_sq < 100: dist_sq = 100 # Prevent division by zero/infinity

            force_mag = config.BLACK_HOLE_FORCE / dist_sq
            force = dist_vec.normalized() * force_mag
            ball.body.apply_force_at_world_point(force, ball.body.position)

    def draw(self, screen):
        if not self.is_active:
            return

        pos = (int(self.current_x), int(self.current_y))
        pygame.draw.circle(screen, self.color, pos, config.BLACK_HOLE_RADIUS)
        pygame.draw.circle(screen, (150, 50, 150), pos, config.BLACK_HOLE_RADIUS + 2, 2)
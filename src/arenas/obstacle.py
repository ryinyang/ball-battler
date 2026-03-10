import pygame
import pymunk
import src.config as config

class Obstacle:
    def __init__(self, space, x, y):
        self.space = space
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (x, y)
        self.shape = None
        self.color = config.COLOR_OBSTACLE

    def draw(self, screen):
        pass

    def on_collide(self, ball):
        pass

class Bumper(Obstacle):
    def __init__(self, space, x, y):
        super().__init__(space, x, y)
        self.radius = config.BUMPER_RADIUS
        self.color = config.COLOR_BUMPER
        
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = config.BUMPER_ELASTICITY
        self.shape.friction = 0.5
        self.shape.collision_type = config.COLLISION_TYPE_OBSTACLE
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_OBSTACLE)
        self.shape.obstacle = self
        self.space.add(self.body, self.shape)

    def draw(self, screen):
        pos = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(screen, self.color, pos, self.radius)
        pygame.draw.circle(screen, (255, 255, 255), pos, self.radius - 8, 3)

    def on_collide(self, ball):
        ball.body.velocity = ball.body.velocity * config.BUMPER_SPEED_BOOST
import pygame
import pygame.gfxdraw
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
        r = int(self.radius)
        c = pygame.Color(self.color)
        
        # Main Body
        pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], r, c)
        pygame.gfxdraw.aacircle(screen, pos[0], pos[1], r, c)
        
        # White Ring details
        pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], r - 7, (255, 255, 255))
        pygame.gfxdraw.aacircle(screen, pos[0], pos[1], r - 7, (255, 255, 255))
        
        pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], r - 10, c)
        pygame.gfxdraw.aacircle(screen, pos[0], pos[1], r - 10, c)

    def on_collide(self, ball):
        ball.body.velocity = ball.body.velocity * config.BUMPER_SPEED_BOOST
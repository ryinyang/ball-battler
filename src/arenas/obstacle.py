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

    def update(self, dt):
        pass

class Bumper(Obstacle):
    def __init__(self, space, x, y):
        super().__init__(space, x, y)
        self.radius = config.BUMPER_RADIUS
        self.color = config.COLOR_BUMPER
        self.highlight_color = config.COLOR_BUMPER_HIGHLIGHT
        
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.elasticity = config.BUMPER_ELASTICITY
        self.shape.friction = 0.5
        self.shape.collision_type = config.COLLISION_TYPE_OBSTACLE
        self.shape.filter = pymunk.ShapeFilter(categories=config.CATEGORY_OBSTACLE)
        self.shape.obstacle = self
        self.space.add(self.body, self.shape)
        
        self.scale = 1.0
        self.anim_timer = 0.0
        self.anim_duration = 0.2

    def draw(self, screen):
        pos = int(self.body.position.x), int(self.body.position.y)
        r = int(self.radius * self.scale)
        c = pygame.Color(self.color)
        highlight_color = pygame.Color(self.highlight_color)
        
        # Main Body
        pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], r, c)
        pygame.gfxdraw.aacircle(screen, pos[0], pos[1], r, c)
        
        # White Ring details
        pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], r - 7, highlight_color)
        pygame.gfxdraw.aacircle(screen, pos[0], pos[1], r - 7, highlight_color)
        
        pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], r - 10, c)
        pygame.gfxdraw.aacircle(screen, pos[0], pos[1], r - 10, c)

    def on_collide(self, ball):
        ball.body.velocity = ball.body.velocity * config.BUMPER_SPEED_BOOST
        self.anim_timer = self.anim_duration

    def update(self, dt):
        if self.anim_timer > 0:
            self.anim_timer -= dt
            
            # Normalize time 0.0 -> 1.0
            t = 1.0 - (max(0, self.anim_timer) / self.anim_duration)
            
            # Expand then shrink
            # 0.0 to 0.5: Expand from 1.0 to 1.3
            # 0.5 to 1.0: Shrink from 1.3 to 1.0
            if t < 0.3:
                progress = t / 0.3
                self.scale = 1.0 + (0.3 * progress)
            else:
                progress = (t - 0.3) / 0.7
                self.scale = 1.3 - (0.3 * progress)
        else:
            self.scale = 1.0
            self.anim_timer = 0
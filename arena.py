import pygame
import pymunk
import config
from anomaly import BlackHole

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

class Arena:
    def __init__(self, space, vertices=None):
        self.space = space
        self.walls = []
        self.obstacles = []
        self.anomalies = []
        
        if vertices:
            self.vertices = vertices
        else:
            raise ValueError("Arena requires vertices")

        self._build_walls()

    def _build_walls(self):
        for i in range(len(self.vertices)):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % len(self.vertices)]
            
            wall = pymunk.Segment(self.space.static_body, p1, p2, config.WALL_THICKNESS)
            wall.elasticity = config.WALL_ELASTICITY
            wall.friction = config.WALL_FRICTION
            wall.filter = pymunk.ShapeFilter(categories=config.CATEGORY_WALL)
            self.space.add(wall)
            self.walls.append(wall)

class BasicArena(Arena):
    def __init__(self, space, width, height):
        vertices = [
            (0, 0),
            (width, 0),
            (width, height),
            (0, height)
        ]
        super().__init__(space, vertices=vertices)

class OctagonArena(Arena):
    def __init__(self, space, width, height, corner_cut=150):
        vertices = [
            (0, corner_cut),              # Left-Top
            (corner_cut, 0),              # Top-Left
            (width - corner_cut, 0),      # Top-Right
            (width, corner_cut),          # Right-Top
            (width, height - corner_cut), # Right-Bottom
            (width - corner_cut, height), # Bottom-Right
            (corner_cut, height),         # Bottom-Left
            (0, height - corner_cut)      # Left-Bottom
        ]
        super().__init__(space, vertices=vertices)
        
        # Bumpers in a + shape
        # self.obstacles.append(Bumper(space, width / 2 - 150, height / 2))
        # self.obstacles.append(Bumper(space, width / 2 + 150, height / 2))
        # self.obstacles.append(Bumper(space, width / 2, height / 2 - 150))
        # self.obstacles.append(Bumper(space, width / 2, height / 2 + 150))
        self.anomalies.append(BlackHole(space, width / 2, height / 2))

    def _build_walls(self):
        max_y = max(v[1] for v in self.vertices)

        for i in range(len(self.vertices)):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % len(self.vertices)]
            
            wall = pymunk.Segment(self.space.static_body, p1, p2, config.WALL_THICKNESS)
            
            # Make the bottom wall extra bouncy
            # if p1[1] == max_y and p2[1] == max_y:
            #     wall.elasticity = config.WALL_BOUNCY_ELASTICITY
            # else:
            wall.elasticity = config.WALL_ELASTICITY
            
            wall.friction = config.WALL_FRICTION
            wall.filter = pymunk.ShapeFilter(categories=config.CATEGORY_WALL)
            self.space.add(wall)
            self.walls.append(wall)
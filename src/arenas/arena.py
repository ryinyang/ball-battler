import pymunk
import src.config as config

class Arena:
    def __init__(self, space, vertices=None):
        self.space = space
        self.walls = []
        self.obstacles = []
        self.anomalies = []
        self.items = []
        
        if vertices:
            self.vertices = vertices
        else:
            raise ValueError("Arena requires vertices")

        self._build_walls()

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def add_anomaly(self, anomaly):
        self.anomalies.append(anomaly)

    def add_item(self, item):
        self.items.append(item)

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
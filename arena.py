import pymunk
import config

class Arena:
    def __init__(self, space, width, height):
        self.space = space
        self.width = width
        self.height = height
        self.walls = []
        self._build_walls()

    def _build_walls(self):
        # 4 segments: Top, Bottom, Left, Right
        segments = [
            ((0, 0), (self.width, 0)),
            ((0, self.height), (self.width, self.height)),
            ((0, 0), (0, self.height)),
            ((self.width, 0), (self.width, self.height))
        ]

        for p1, p2 in segments:
            wall = pymunk.Segment(self.space.static_body, p1, p2, config.WALL_THICKNESS)
            wall.elasticity = config.WALL_ELASTICITY
            wall.friction = config.WALL_FRICTION
            self.space.add(wall)
            self.walls.append(wall)
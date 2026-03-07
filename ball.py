import pymunk

class Ball:
    def __init__(self, x, y, space):
        mass = 10
        radius = 15
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = (x, y)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.9
        self.shape.friction = 0.5
        space.add(self.body, self.shape)

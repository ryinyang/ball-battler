import pygame
import pymunk
from ball import Ball

def main():
    # Initialize Pygame
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Battler - Phase 0")
    clock = pygame.time.Clock()

    # Initialize Pymunk Space
    space = pymunk.Space()
    space.gravity = (0, 900)  # Gravity pointing down

    # Create Arena Walls
    # 4 segments: Top, Bottom, Left, Right
    walls = [
        pymunk.Segment(space.static_body, (0, 0), (WIDTH, 0), 5),
        pymunk.Segment(space.static_body, (0, HEIGHT), (WIDTH, HEIGHT), 5),
        pymunk.Segment(space.static_body, (0, 0), (0, HEIGHT), 5),
        pymunk.Segment(space.static_body, (WIDTH, 0), (WIDTH, HEIGHT), 5)
    ]
    
    for wall in walls:
        wall.elasticity = 1.0
        wall.friction = 0.5
        space.add(wall)

    # Create Balls
    ball1 = Ball(WIDTH // 4, HEIGHT // 2, space)
    ball1.body.velocity = (400, -200)
    ball2 = Ball(3 * WIDTH // 4, HEIGHT // 2, space)
    ball2.body.velocity = (-400, -200)
    balls = [ball1, ball2]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Physics step
        dt = 1.0 / 60.0
        space.step(dt)

        # Drawing
        screen.fill((0, 0, 0))
        
        # Draw walls
        for shape in space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1 = shape.a
                p2 = shape.b
                pygame.draw.line(screen, (200, 200, 200), p1, p2, int(shape.radius * 2))

        # Draw balls
        for ball in balls:
            pos = int(ball.body.position.x), int(ball.body.position.y)
            pygame.draw.circle(screen, (255, 0, 0), pos, int(ball.shape.radius))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

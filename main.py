import pygame
import pymunk
from ball import Ball

def handle_collision(arbiter, space, data):
    shape_a, shape_b = arbiter.shapes
    ball_a = shape_a.ball
    ball_b = shape_b.ball
    
    # Damage Logic: max(1, Attack - Defense)
    dmg_a = max(1, ball_b.attack - ball_a.defense)
    dmg_b = max(1, ball_a.attack - ball_b.defense)
    
    ball_a.hp -= dmg_a
    ball_b.hp -= dmg_b
    
    print(f"Collision Detected! A: {ball_a.hp} (-{dmg_a}) | B: {ball_b.hp} (-{dmg_b})")

def main():
    # Initialize Pygame
    pygame.init()
    
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Battler - Phase 1")
    clock = pygame.time.Clock()

    # Initialize Pymunk Space
    space = pymunk.Space()
    space.gravity = (0, 900)  # Gravity pointing down

    # Collision Handler
    space.on_collision(1, 1, begin=handle_collision)

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

        # Death Loop
        for ball in balls[:]:
            if ball.hp <= 0:
                space.remove(ball.body, ball.shape)
                balls.remove(ball)
                print("Ball eliminated!")

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

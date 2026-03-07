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

    # Physics Tweak: Add a small velocity boost on collision
    ball_a.body.velocity *= 1.01
    ball_b.body.velocity *= 1.01

def main():
    # Initialize Pygame
    pygame.init()
    
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Battler - Phase 2")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Initialize Pymunk Space
    space = pymunk.Space()
    space.gravity = (0, 400)  # Gravity pointing down

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
        # Physics Tweak: Remove wall friction for more energetic bounces
        wall.friction = 0.0
        space.add(wall)

    # Create Balls
    ball1 = Ball(WIDTH // 4, HEIGHT // 2, space, "Player 1")
    ball1.body.velocity = (400, -200)
    ball2 = Ball(3 * WIDTH // 4, HEIGHT // 2, space, "Player 2")
    ball2.body.velocity = (-400, -200)
    balls = [ball1, ball2]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Physics Tweak: Attraction force between balls
        if len(balls) > 1:
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    ball_a = balls[i]
                    ball_b = balls[j]

                    p1 = ball_a.body.position
                    p2 = ball_b.body.position
                    direction = p2 - p1
                    distance_sq = direction.length_squared

                    # Avoid instability at very close distances
                    if distance_sq < (ball_a.shape.radius + ball_b.shape.radius)**2:
                        continue

                    force_magnitude = 2000000.0 / distance_sq
                    force_vector = direction.normalized() * force_magnitude
                    ball_a.body.apply_force_at_world_point(force_vector, p1)
                    ball_b.body.apply_force_at_world_point(-force_vector, p2)

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

        # Draw UI
        for i, ball in enumerate(balls):
            velocity_magnitude = int(ball.body.velocity.length)
            text_surf = font.render(f"{ball.name}: HP {int(ball.hp)} | Vel: {velocity_magnitude}", True, (255, 255, 255))
            if i % 2 == 0:
                screen.blit(text_surf, (20, 20 + (i // 2) * 30))
            else:
                rect = text_surf.get_rect()
                rect.topright = (WIDTH - 20, 20 + (i // 2) * 30)
                screen.blit(text_surf, rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

import pygame
import pymunk
from ball import Rogue, Berserker
from arena import Arena
import config

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(config.CAPTION)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.running = True

        # Physics Setup
        self.space = pymunk.Space()
        self.space.gravity = config.GRAVITY
        
        # Handlers
        h_weapon = self.space.on_collision(config.COLLISION_TYPE_BALL, config.COLLISION_TYPE_WEAPON, begin=self.handle_weapon_hit)

        # Game Objects
        self.arena = Arena(self.space, self.WIDTH, self.HEIGHT)
        self.balls = []
        self._spawn_balls()

    def _spawn_balls(self):
        # Using the new subclasses
        b1 = Rogue(self.WIDTH // 4, self.HEIGHT // 2, self.space, "Rogue")
        b1.body.velocity = (400, -200)
        
        b2 = Berserker(3 * self.WIDTH // 4, self.HEIGHT // 2, self.space, "Berserker")
        b2.body.velocity = (-400, -200)
        
        self.balls = [b1, b2]

    def handle_weapon_hit(self, arbiter, space, data):
        victim_shape, weapon_shape = arbiter.shapes
        victim = victim_shape.ball
        attacker = weapon_shape.ball

        if victim == attacker:
            return False

        if attacker.cooldown <= 0:
            attacker.cooldown = attacker.attack_speed
            
            dmg = max(1, attacker.attack - victim.defense)
            victim.hp -= dmg
            print(f"{attacker.name} hit {victim.name} for {dmg}!")
            
            attacker.on_hit(victim)
            attacker.flash_timer = config.BALL_FLASH_DURATION

            # Visual Knockback
            impulse_vec = (victim.body.position - attacker.body.position).normalized() * config.KNOCKBACK_IMPULSE
            victim.body.apply_impulse_at_local_point(impulse_vec)

        return False

    def apply_attraction(self):
        if len(self.balls) < 2: return
        
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball_a = self.balls[i]
                ball_b = self.balls[j]
                
                p1, p2 = ball_a.body.position, ball_b.body.position
                direction = p2 - p1
                dist_sq = direction.length_squared
                
                if dist_sq < (ball_a.shape.radius + ball_b.shape.radius)**2:
                    continue

                force = direction.normalized() * (config.ATTRACTION_FORCE / dist_sq)
                ball_a.body.apply_force_at_world_point(force, p1)
                ball_b.body.apply_force_at_world_point(-force, p2)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(config.FPS)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.apply_attraction()
        dt = config.DT
        for ball in self.balls: ball.update(dt)
        self.space.step(dt)
        self._check_deaths()

    def _check_deaths(self):
        for ball in self.balls[:]:
            if ball.hp <= 0:
                self.space.remove(ball.body, ball.shape, ball.weapon_shape)
                self.balls.remove(ball)
                print(f"{ball.name} eliminated!")

    def draw(self):
        self.screen.fill(config.COLOR_BG)
        # Draw Walls
        for shape in self.space.shapes:
            if isinstance(shape, pymunk.Segment):
                pygame.draw.line(self.screen, config.COLOR_WALL, shape.a, shape.b, int(shape.radius * 2))
        
        # Draw Balls
        for ball in self.balls:
            pos = int(ball.body.position.x), int(ball.body.position.y)
            pygame.draw.circle(self.screen, ball.color, pos, int(ball.shape.radius))

            # Draw Weapon (World Space)
            local_verts = ball.weapon_shape.get_vertices()
            world_verts = []
            for v in local_verts:
                p = ball.body.position + v.rotated(ball.body.angle)
                world_verts.append((int(p.x), int(p.y)))
            
            weapon_color = config.COLOR_WEAPON_FLASH if ball.flash_timer > 0 else config.COLOR_WEAPON_DEFAULT
            pygame.draw.polygon(self.screen, weapon_color, world_verts)

        # Draw UI
        for i, ball in enumerate(self.balls):
            velocity_magnitude = int(ball.body.velocity.length)
            text_surf = self.font.render(f"{ball.name}: HP {int(ball.hp)} | Vel: {velocity_magnitude}", True, config.COLOR_TEXT)
            if i % 2 == 0:
                self.screen.blit(text_surf, (20, 20 + (i // 2) * 30))
            else:
                rect = text_surf.get_rect()
                rect.topright = (self.WIDTH - 20, 20 + (i // 2) * 30)
                self.screen.blit(text_surf, rect)

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()

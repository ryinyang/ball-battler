import pygame
import pymunk
from ball import Rogue, Berserker, Paladin, Monk
from arena import OctagonArena
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
        self.bullet_time_timer = 0.0
        self.bullet_time_balls = []

        # Physics Setup
        self.space = pymunk.Space()
        self.space.gravity = config.GRAVITY
        
        # Handlers
        h_weapon = self.space.on_collision(config.COLLISION_TYPE_BALL, config.COLLISION_TYPE_WEAPON, begin=self.handle_weapon_hit)
        h_clash = self.space.on_collision(config.COLLISION_TYPE_WEAPON, config.COLLISION_TYPE_WEAPON, begin=self.handle_weapon_clash)
        h_obstacle = self.space.on_collision(config.COLLISION_TYPE_BALL, config.COLLISION_TYPE_OBSTACLE, begin=self.handle_obstacle_hit)

        # Game Objects
        self.arena = OctagonArena(self.space, self.WIDTH, self.HEIGHT)
        self.balls = []
        self._spawn_balls()

    def _spawn_balls(self):
        # Spawn 4 classes in corners
        offset = 150
        
        b1 = Rogue(offset, offset, self.space, "Rogue")
        b1.body.velocity = (200, 200)
        
        b2 = Berserker(self.WIDTH - offset, offset, self.space, "Berserker")
        b2.body.velocity = (-200, 200)

        b3 = Paladin(offset, self.HEIGHT - offset, self.space, "Paladin")
        b3.body.velocity = (200, -200)

        b4 = Monk(self.WIDTH - offset, self.HEIGHT - offset, self.space, "Monk")
        b4.body.velocity = (-200, -200)
        
        self.balls = [b1, b2, b3, b4]

    def handle_weapon_hit(self, arbiter, space, data):
        victim_shape, weapon_shape = arbiter.shapes
        victim = victim_shape.ball
        attacker = weapon_shape.ball

        if victim == attacker:
            return False

        dmg = max(1, attacker.attack - victim.defense)
        victim.hp -= dmg
        print(f"{attacker.name} hit {victim.name} for {dmg}!")
        
        attacker.on_hit(victim)
        attacker.flash_timer = config.BALL_FLASH_DURATION

        # Visual Knockback
        direction = (victim.body.position - attacker.body.position).normalized()
        victim.body.apply_impulse_at_local_point(direction * config.KNOCKBACK_IMPULSE)
        attacker.body.apply_impulse_at_local_point(-direction * config.RECOIL_IMPULSE)
        self.bullet_time_timer = config.BULLET_TIME_DURATION
        self.bullet_time_balls = [attacker, victim]
        attacker.rotation_speed *= -1

        return True

    def handle_weapon_clash(self, arbiter, space, data):
        shape_a, shape_b = arbiter.shapes
        ball_a = shape_a.ball
        ball_b = shape_b.ball

        if ball_a == ball_b:
            return False

        # Reverse rotation
        ball_a.rotation_speed *= -1
        ball_b.rotation_speed *= -1

        # Knockback
        diff = ball_b.body.position - ball_a.body.position
        if diff.length_squared > 0:
            direction = diff.normalized()
            ball_a.body.apply_impulse_at_local_point(-direction * config.WEAPON_CLASH_IMPULSE)
            ball_b.body.apply_impulse_at_local_point(direction * config.WEAPON_CLASH_IMPULSE)

        return True

    def handle_obstacle_hit(self, arbiter, space, data):
        ball_shape, obstacle_shape = arbiter.shapes
        ball = ball_shape.ball
        obstacle = obstacle_shape.obstacle
        obstacle.on_collide(ball)
        return True

    def check_proximity_bullet_time(self):
        # If a hit event is currently active (long timer), don't interfere
        if self.bullet_time_timer > config.DT * 3:
            return

        triggered = False
        close_balls = set()
        threshold_sq = config.BULLET_TIME_TRIGGER_DISTANCE ** 2

        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball_a = self.balls[i]
                ball_b = self.balls[j]
                
                dist_sq = (ball_a.body.position - ball_b.body.position).length_squared
                
                if dist_sq < threshold_sq:
                    triggered = True
                    close_balls.add(ball_a)
                    close_balls.add(ball_b)
        
        if triggered:
            self.bullet_time_timer = config.DT * 2
            self.bullet_time_balls = list(close_balls)

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
        self.check_proximity_bullet_time()
        
        dt = config.DT
        if self.bullet_time_timer > 0:
            dt *= config.BULLET_TIME_SCALE
            self.bullet_time_timer -= config.DT
            
        for ball in self.balls: ball.update(dt)
        self.space.step(dt)
        self._check_deaths()

    def _check_deaths(self):
        for ball in self.balls[:]:
            if ball.hp <= 0:
                self.space.remove(ball.body, ball.shape, *ball.weapon_shapes)
                self.balls.remove(ball)
                print(f"{ball.name} eliminated!")

    def draw(self):
        self.screen.fill(config.COLOR_BG)
        
        # Draw Obstacles
        for obstacle in self.arena.obstacles:
            obstacle.draw(self.screen)

        # Draw Bullet Time Highlights
        if self.bullet_time_timer > 0:
            for ball in self.bullet_time_balls:
                if ball in self.balls:
                    pos = int(ball.body.position.x), int(ball.body.position.y)
                    
                    halo_radius = int(ball.shape.radius) + 40
                    halo_surf = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
                    for r in range(halo_radius, int(ball.shape.radius), -2):
                        
                        pygame.draw.circle(halo_surf, (*config.COLOR_HIGHLIGHT, config.HALO_OPACITY), (halo_radius, halo_radius), r)
                    self.screen.blit(halo_surf, (pos[0] - halo_radius, pos[1] - halo_radius))

        # Draw Walls
        for shape in self.space.shapes:
            if isinstance(shape, pymunk.Segment):
                pygame.draw.line(self.screen, config.COLOR_WALL, shape.a, shape.b, int(shape.radius * 2))
        
        # Draw Balls
        for ball in self.balls:
            pos = int(ball.body.position.x), int(ball.body.position.y)
            pygame.draw.circle(self.screen, ball.color, pos, int(ball.shape.radius))

            # Draw Weapon (World Space)
            for shape in ball.weapon_shapes:
                local_verts = shape.get_vertices()
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

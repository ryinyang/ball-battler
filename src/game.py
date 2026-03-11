import random
import pygame
import pygame.gfxdraw
import pymunk
from src.balls.rogue import Rogue
from src.balls.berserker import Berserker
from src.balls.paladin import Paladin
from src.balls.monk import Monk
from src.balls.warrior import Warrior
from src.balls.ranger import Ranger
from src.balls.shadow import Shadow
from src.arenas.arena import OctagonArena
from src.arenas.anomaly import BlackHole
from src.arenas.obstacle import Bumper
from src.arenas.item import Potion
import src.config as config

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(config.CAPTION)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.Font("assets/impact.ttf", 24)
        self.running = True
        self.bullet_time_timer = 0.0
        self.bullet_time_balls = []
        self.item_spawn_timer = config.ITEM_SPAWN_INTERVAL

        # Physics Setup
        self.space = pymunk.Space()
        self.space.gravity = config.GRAVITY
        
        # Handlers
        h_weapon = self.space.on_collision(config.COLLISION_TYPE_BALL, config.COLLISION_TYPE_WEAPON, begin=self.handle_weapon_hit)
        h_clash = self.space.on_collision(config.COLLISION_TYPE_WEAPON, config.COLLISION_TYPE_WEAPON, begin=self.handle_weapon_clash)
        h_obstacle = self.space.on_collision(config.COLLISION_TYPE_BALL, config.COLLISION_TYPE_OBSTACLE, begin=self.handle_obstacle_hit)
        h_item = self.space.on_collision(config.COLLISION_TYPE_BALL, config.COLLISION_TYPE_ITEM, begin=self.handle_item_pickup)

        # Game Objects
        self.arena = OctagonArena(self.space, self.WIDTH, self.HEIGHT)
        self.balls = []
        self._populate_arena()
        self._spawn_balls()

    def _populate_arena(self):
        # Bumpers in a + shape
        w, h = self.WIDTH, self.HEIGHT
        # self.arena.add_obstacle(Bumper(self.space, w / 2 - 150, h / 2))
        # self.arena.add_obstacle(Bumper(self.space, w / 2 + 150, h / 2))
        self.arena.add_obstacle(Bumper(self.space, w / 2, h / 2 - 150))
        self.arena.add_obstacle(Bumper(self.space, w / 2, h / 2 + 150))
        
        # Black Hole
        self.arena.add_anomaly(BlackHole(self.space, w / 2, h / 2))

    def _spawn_balls(self):
        offset = 150
        
        b1 = Rogue(offset, offset, self.space, "Rogue")
        b1.body.velocity = (200, 200)
        
        b2 = Berserker(self.WIDTH - offset, offset, self.space, "Berserker")
        b2.body.velocity = (-200, 200)

        b3 = Paladin(offset, self.HEIGHT - offset, self.space, "Paladin")
        b3.body.velocity = (200, -200)

        b4 = Monk(self.WIDTH - offset, self.HEIGHT - offset, self.space, "Monk")
        b4.body.velocity = (-200, -200)
        
        b5 = Warrior(self.WIDTH / 2, self.HEIGHT / 2, self.space, "Warrior")
        b5.body.velocity = (100, 100)
        
        b6 = Ranger(self.WIDTH / 2, offset, self.space, "Ranger")
        b6.body.velocity = (0, 200)
        
        b7 = Shadow(self.WIDTH / 2, self.HEIGHT / 2 + 100, self.space, "Shadow")
        b7.body.velocity = (100, -100)
        
        self.balls = [b1, b2, b3, b4, b5, b6, b7]

    def _spawn_item(self):
        # Don't spawn items if there are too many
        if len(self.arena.items) >= 5:
            return

        # Find a valid spawn position (not too close to walls or obstacles)
        padding = 50
        x = random.uniform(padding, self.WIDTH - padding)
        y = random.uniform(padding, self.HEIGHT - padding)
        
        new_item = Potion(self.space, x, y)
        self.arena.add_item(new_item)

    def handle_weapon_hit(self, arbiter, space, data):
        target_shape, weapon_shape = arbiter.shapes
        target = target_shape.ball
        attacker = weapon_shape.ball

        if target == attacker:
            return False

        # Delegate combat logic to the attacker Ball
        attacker.deal_hit(target, weapon_shape)
        
        self.bullet_time_timer = config.BULLET_TIME_DURATION
        self.bullet_time_balls = [attacker, target]

        return True

    def handle_weapon_clash(self, arbiter, space, data):
        shape_a, shape_b = arbiter.shapes
        ball_a = shape_a.ball
        ball_b = shape_b.ball

        if ball_a == ball_b:
            return False

        # Handle projectile clash
        is_proj_a = hasattr(shape_a, 'projectile')
        is_proj_b = hasattr(shape_b, 'projectile')
        is_trap_a = hasattr(shape_a, 'trap')
        is_trap_b = hasattr(shape_b, 'trap')

        if is_proj_a or is_proj_b or is_trap_a or is_trap_b:
            for s in [shape_a, shape_b]:
                if hasattr(s, 'projectile'):
                    s.projectile.destroy()
                    if hasattr(s.ball, 'projectiles') and s.projectile in s.ball.projectiles:
                        s.ball.projectiles.remove(s.projectile)
                elif hasattr(s, 'trap'):
                    s.trap.destroy()
                    if hasattr(s.ball, 'traps') and s.trap in s.ball.traps:
                        s.ball.traps.remove(s.trap)
            return False

        # Reverse rotation
        ball_a.rotation_speed *= -1
        ball_b.rotation_speed *= -1

        # Trigger on_clash
        ball_a.on_clash(ball_b)
        ball_b.on_clash(ball_a)

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

    def handle_item_pickup(self, arbiter, space, data):
        ball_shape, item_shape = arbiter.shapes
        ball = ball_shape.ball
        item = item_shape.item

        item.apply_effect(ball)
        
        def remove_item_callback(space, item_to_remove, items_list):
            if item_to_remove in items_list:
                items_list.remove(item_to_remove)
                item_to_remove.remove()

        space.add_post_step_callback(remove_item_callback, item, self.arena.items)
        return False # It's a sensor, no physical response needed

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

    def _update_item_spawner(self, dt):
        self.item_spawn_timer -= dt
        if self.item_spawn_timer <= 0:
            self._spawn_item()
            self.item_spawn_timer = config.ITEM_SPAWN_INTERVAL

    def update(self):
        # self.apply_attraction()
        self.check_proximity_bullet_time()
        self._update_item_spawner(config.DT)
        
        dt = config.DT
        if self.bullet_time_timer > 0:
            dt *= config.BULLET_TIME_SCALE
            self.bullet_time_timer -= config.DT
            
        for anomaly in self.arena.anomalies[:]:
            anomaly.update(dt, self.balls)
            if anomaly.finished:
                self.arena.anomalies.remove(anomaly)

        for ball in self.balls: ball.update(dt)
        self.space.step(dt)
        self._check_deaths()

    def _check_deaths(self):
        for ball in self.balls[:]:
            if ball.hp <= 0:
                if hasattr(ball, 'projectiles'):
                    for p in ball.projectiles:
                        p.destroy()
                    ball.projectiles.clear()

                if hasattr(ball, 'traps'):
                    for t in ball.traps:
                        t.destroy()
                    ball.traps.clear()

                self.space.remove(ball.body, ball.shape, *ball.weapon_shapes)
                self.balls.remove(ball)
                print(f"{ball.name} eliminated!")

    def draw(self):
        self.screen.fill(config.COLOR_BG)
        
        # Draw Obstacles
        for obstacle in self.arena.obstacles:
            obstacle.draw(self.screen)

        # Draw Effects
        for anomaly in self.arena.anomalies:
            anomaly.draw(self.screen)

        # Draw Items
        for item in self.arena.items:
            item.draw(self.screen)

        # Draw Bullet Time Highlights
        if self.bullet_time_timer > 0:
            for ball in self.bullet_time_balls:
                if ball in self.balls:
                    pos = int(ball.body.position.x), int(ball.body.position.y)
                    
                    halo_radius = int(ball.shape.radius) + 40
                    halo_surf = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
                    for r in range(halo_radius, int(ball.shape.radius), -2):
                        
                        c = pygame.Color(config.COLOR_HIGHLIGHT)
                        c.a = config.HALO_OPACITY
                        pygame.gfxdraw.filled_circle(halo_surf, halo_radius, halo_radius, r, c)
                    self.screen.blit(halo_surf, (pos[0] - halo_radius, pos[1] - halo_radius))

        # Draw Walls
        for shape in self.space.shapes:
            if isinstance(shape, pymunk.Segment):
                pygame.draw.line(self.screen, config.COLOR_WALL, shape.a, shape.b, int(shape.radius * 2))
        
        # Draw Balls
        for ball in self.balls:
            pos = int(ball.body.position.x), int(ball.body.position.y)
            c = pygame.Color(ball.color)
            pygame.gfxdraw.filled_circle(self.screen, pos[0], pos[1], int(ball.shape.radius), c)
            pygame.gfxdraw.aacircle(self.screen, pos[0], pos[1], int(ball.shape.radius), c)
            
            # Draw HP inside ball
            hp_surf = self.small_font.render(str(int(ball.hp)), True, config.COLOR_TEXT)
            hp_rect = hp_surf.get_rect(center=pos)
            self.screen.blit(hp_surf, hp_rect)

            # Draw Shadow AOE Halo
            if hasattr(ball, 'aoe_radius'):
                r = int(ball.aoe_radius)
                halo_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                c = pygame.Color(ball.color)
                c.a = config.HALO_OPACITY
                pygame.gfxdraw.filled_circle(halo_surf, r, r, r, c)
                self.screen.blit(halo_surf, (pos[0] - r, pos[1] - r))

            # Draw Weapon (World Space)
            for shape in ball.weapon_shapes:
                local_verts = shape.get_vertices()
                world_verts = []
                for v in local_verts:
                    p = ball.body.position + v.rotated(ball.body.angle)
                    world_verts.append((int(p.x), int(p.y)))
                
                weapon_color = config.COLOR_WEAPON_FLASH if ball.flash_timer > 0 else config.COLOR_WEAPON_DEFAULT
                c = pygame.Color(weapon_color)
                pygame.gfxdraw.filled_polygon(self.screen, world_verts, c)
                pygame.gfxdraw.aapolygon(self.screen, world_verts, c)

            # Draw Projectiles
            if hasattr(ball, 'projectiles'):
                for p in ball.projectiles:
                    p_verts = []
                    for v in p.shape.get_vertices():
                        # World transform
                        wv = p.body.position + v.rotated(p.body.angle)
                        p_verts.append((int(wv.x), int(wv.y)))
                    c = pygame.Color(ball.color)
                    pygame.gfxdraw.filled_polygon(self.screen, p_verts, c)
                    pygame.gfxdraw.aapolygon(self.screen, p_verts, c)

            # Draw Traps
            if hasattr(ball, 'traps'):
                for t in ball.traps:
                    t_verts = []
                    for v in t.shape.get_vertices():
                        # World transform
                        wv = t.body.position + v.rotated(t.body.angle)
                        t_verts.append((int(wv.x), int(wv.y)))
                    c = pygame.Color(200, 50, 50)
                    pygame.gfxdraw.filled_polygon(self.screen, t_verts, c)
                    pygame.gfxdraw.aapolygon(self.screen, t_verts, c)

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
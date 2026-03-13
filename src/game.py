import random
import pygame
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
from src.drawing_manager import DrawingManager

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(config.CAPTION)
        self.clock = pygame.time.Clock()
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
        
        self.drawing_manager = DrawingManager(self.screen, self.WIDTH, self.HEIGHT)
        self.drawing_manager.cache_arena_floor(self.space)

    def _populate_arena(self):
        # Bumpers in a + shape
        w, h = self.WIDTH, self.HEIGHT
        # self.arena.add_obstacle(Bumper(self.space, w / 2 - 150, h / 2))
        # self.arena.add_obstacle(Bumper(self.space, w / 2 + 150, h / 2))
        self.arena.add_obstacle(Bumper(self.space, w / 2, h / 2 - 150))
        self.arena.add_obstacle(Bumper(self.space, w / 2, h / 2 + 150))
        
        # Black Hole
        # self.arena.add_anomaly(BlackHole(self.space, w / 2, h / 2))

    def _spawn_balls(self):
        offset = 150
        
        b1 = Rogue(offset, offset, self.space, "Rogue")
        b1.body.velocity = (200, 200)
        
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
        
        self.balls = [b1, b3, b4, b5, b6, b7]

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

        for obstacle in self.arena.obstacles:
            if hasattr(obstacle, 'update'):
                obstacle.update(dt)

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
        self.drawing_manager.draw(self.space, self.arena, self.balls, self.bullet_time_timer, self.bullet_time_balls)
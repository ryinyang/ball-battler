import math
import pygame
import pygame.gfxdraw
import pymunk
import src.config as config

class DrawingManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 36)
        try:
            self.small_font = pygame.font.Font("assets/impact.ttf", 24)
        except FileNotFoundError:
            self.small_font = pygame.font.SysFont(None, 24)
            
        self.arena_polygon = []

    def cache_arena_floor(self, space):
        vertices = set()
        for shape in space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1 = (int(shape.a.x), int(shape.a.y))
                p2 = (int(shape.b.x), int(shape.b.y))
                vertices.add(p1)
                vertices.add(p2)
        
        if not vertices:
            self.arena_polygon = []
            return
            
        cx, cy = self.width / 2, self.height / 2
        # Sort vertices by angle from center to form a proper polygon
        self.arena_polygon = sorted(list(vertices), key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    def draw(self, space, arena, balls, bullet_time_timer, bullet_time_balls):
        self.screen.fill(config.COLOR_BG)
        
        # Draw Arena Floor
        if self.arena_polygon:
            c = pygame.Color(config.COLOR_ARENA_FLOOR)
            pygame.gfxdraw.filled_polygon(self.screen, self.arena_polygon, c)
            pygame.gfxdraw.aapolygon(self.screen, self.arena_polygon, c)

        # Draw Objects
        for obstacle in arena.obstacles:
            obstacle.draw(self.screen)
        for anomaly in arena.anomalies:
            anomaly.draw(self.screen)
        for item in arena.items:
            item.draw(self.screen)

        # Draw Bullet Time Highlights
        if bullet_time_timer > 0:
            for ball in bullet_time_balls:
                if ball in balls:
                    self._draw_halo(ball)

        # Draw Walls
        self._draw_walls(space)

        # Draw Balls & UI
        for ball in balls:
            self._draw_ball(ball)
        
        self._draw_ui(balls)
        
        pygame.display.flip()

    def _draw_halo(self, ball):
        pos = int(ball.body.position.x), int(ball.body.position.y)
        halo_radius = int(ball.shape.radius) + 40
        halo_surf = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
        for r in range(halo_radius, int(ball.shape.radius), -2):
            c = pygame.Color(config.COLOR_HIGHLIGHT)
            c.a = config.HALO_OPACITY
            pygame.gfxdraw.filled_circle(halo_surf, halo_radius, halo_radius, r, c)
        self.screen.blit(halo_surf, (pos[0] - halo_radius, pos[1] - halo_radius))

    def _draw_walls(self, space):
        for shape in space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1, p2 = shape.a, shape.b
                radius = int(shape.radius)
                color = pygame.Color(config.COLOR_WALL)
                for p in (p1, p2):
                    pygame.gfxdraw.filled_circle(self.screen, int(p.x), int(p.y), radius, color)
                    pygame.gfxdraw.aacircle(self.screen, int(p.x), int(p.y), radius, color)
                v = p2 - p1
                if v.length_squared > 0:
                    nv = v.perpendicular().normalized() * radius
                    poly_verts = [p1 + nv, p2 + nv, p2 - nv, p1 - nv]
                    poly_points = [(int(p.x), int(p.y)) for p in poly_verts]
                    pygame.gfxdraw.filled_polygon(self.screen, poly_points, color)
                    pygame.gfxdraw.aapolygon(self.screen, poly_points, color)

    def _draw_ball(self, ball):
        pos = int(ball.body.position.x), int(ball.body.position.y)
        
        # Body (Flash White on Hit)
        color = config.COLOR_FLASH if ball.flash_timer > 0 else ball.color
        c = pygame.Color(color)
        pygame.gfxdraw.filled_circle(self.screen, pos[0], pos[1], int(ball.shape.radius), c)
        pygame.gfxdraw.aacircle(self.screen, pos[0], pos[1], int(ball.shape.radius), c)
        
        # HP Text
        hp = max(1, int(ball.hp))
        # Invert color when flashing for better visibility
        text_color = config.COLOR_BG if ball.flash_timer > 0 else config.COLOR_TEXT
        hp_surf = self.small_font.render(str(hp), True, text_color)
        hp_rect = hp_surf.get_rect(center=pos)
        self.screen.blit(hp_surf, hp_rect)

        # Shadow AOE
        if hasattr(ball, 'aoe_radius'):
            r = int(ball.aoe_radius)
            halo_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            c = pygame.Color(ball.color)
            c.a = config.HALO_OPACITY
            pygame.gfxdraw.filled_circle(halo_surf, r, r, r, c)
            self.screen.blit(halo_surf, (pos[0] - r, pos[1] - r))

        # Weapons
        for shape in ball.weapon_shapes:
            local_verts = shape.get_vertices()
            world_verts = [(int((ball.body.position + v.rotated(ball.body.angle)).x), int((ball.body.position + v.rotated(ball.body.angle)).y)) for v in local_verts]
            
            c = pygame.Color(config.COLOR_WEAPON_DEFAULT)
            pygame.gfxdraw.filled_polygon(self.screen, world_verts, c)
            pygame.gfxdraw.aapolygon(self.screen, world_verts, c)
            
            # White Outline Flash
            if ball.weapon_flash_timer > 0:
                pygame.draw.lines(self.screen, config.COLOR_FLASH, True, world_verts, 3)

        # Projectiles
        if hasattr(ball, 'projectiles'):
            for p in ball.projectiles:
                p_verts = [(int((p.body.position + v.rotated(p.body.angle)).x), int((p.body.position + v.rotated(p.body.angle)).y)) for v in p.shape.get_vertices()]
                c = pygame.Color(ball.color)
                pygame.gfxdraw.filled_polygon(self.screen, p_verts, c)
                pygame.gfxdraw.aapolygon(self.screen, p_verts, c)

        # Traps
        if hasattr(ball, 'traps'):
            for t in ball.traps:
                t_verts = [(int((t.body.position + v.rotated(t.body.angle)).x), int((t.body.position + v.rotated(t.body.angle)).y)) for v in t.shape.get_vertices()]
                c = pygame.Color(200, 50, 50)
                pygame.gfxdraw.filled_polygon(self.screen, t_verts, c)
                pygame.gfxdraw.aapolygon(self.screen, t_verts, c)

    def _draw_ui(self, balls):
        for i, ball in enumerate(balls):
            velocity_magnitude = int(ball.body.velocity.length)
            text_surf = self.font.render(f"{ball.name}: HP {int(ball.hp)} | Vel: {velocity_magnitude}", True, config.COLOR_TEXT)
            if i % 2 == 0:
                self.screen.blit(text_surf, (20, 20 + (i // 2) * 30))
            else:
                rect = text_surf.get_rect()
                rect.topright = (self.width - 20, 20 + (i // 2) * 30)
                self.screen.blit(text_surf, rect)
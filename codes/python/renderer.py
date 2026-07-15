import math
import threading
import pygame

BG_COLOR = (18, 18, 24)
WALL_COLOR = (90, 200, 255)
PLAYER_COLOR = (255, 120, 90)
RAY_COLOR = (120, 255, 150)
TEXT_COLOR = (230, 230, 230)
GRID_COLOR = (40, 40, 50)


class RoomView:
    def __init__(self, tracker, room, width=800, height=650):
        self.tracker = tracker
        self.room = room
        self.width = width
        self.height = height
        self.running = False
        self.thread = None
        self.sim_mode = False
        self.screen = None
        self.margin = 60

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _to_screen(self, x, y):
        x0, x1, y0, y1 = self.room.bounds()
        avail_w = self.width - self.margin * 2
        avail_h = self.height - self.margin * 2
        scale = min(avail_w / self.room.width, avail_h / self.room.height)
        sx = self.width / 2 + x * scale
        sy = self.height / 2 - y * scale
        return sx, sy, scale

    def _run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Room Tracking View")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("consolas", 16)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if self.sim_mode:
                self._handle_sim_keys(keys)

            self._draw(font)
            clock.tick(30)

        pygame.quit()

    def _handle_sim_keys(self, keys):
        snap = self.tracker.snapshot()
        x, y, angle = snap["player_x"], snap["player_y"], snap["player_angle"]
        step = 3
        rot_step = 3
        angle_rad = math.radians(angle)

        if keys[pygame.K_w]:
            x += math.sin(angle_rad) * step
            y += math.cos(angle_rad) * step
        if keys[pygame.K_s]:
            x -= math.sin(angle_rad) * step
            y -= math.cos(angle_rad) * step
        if keys[pygame.K_a]:
            x -= math.cos(angle_rad) * step
            y += math.sin(angle_rad) * step
        if keys[pygame.K_d]:
            x += math.cos(angle_rad) * step
            y -= math.sin(angle_rad) * step
        if keys[pygame.K_LEFT]:
            angle -= rot_step
        if keys[pygame.K_RIGHT]:
            angle += rot_step

        self.tracker.set_position_manual(x, y, angle)

    def _draw(self, font):
        self.screen.fill(BG_COLOR)

        x0, x1, y0, y1 = self.room.bounds()
        sx0, sy0, scale = self._to_screen(x0, y1)
        sx1, sy1, _ = self._to_screen(x1, y0)
        room_rect = pygame.Rect(sx0, sy0, sx1 - sx0, sy1 - sy0)
        pygame.draw.rect(self.screen, WALL_COLOR, room_rect, 3)

        for wall in self.room.walls:
            ax, ay, bx, by = wall
            pax, pay, _ = self._to_screen(ax, ay)
            pbx, pby, _ = self._to_screen(bx, by)
            pygame.draw.line(self.screen, WALL_COLOR, (pax, pay), (pbx, pby), 2)

        for obstacle in self.room.obstacles:
            ox, oy, ow, oh = obstacle
            psx, psy, _ = self._to_screen(ox - ow / 2, oy + oh / 2)
            pygame.draw.rect(self.screen, (150, 100, 200),
                              pygame.Rect(psx, psy, ow * scale, oh * scale))

        origin_x, origin_y, _ = self._to_screen(0, 0)
        pygame.draw.line(self.screen, GRID_COLOR, (origin_x, sy0), (origin_x, sy1), 1)
        pygame.draw.line(self.screen, GRID_COLOR, (sx0, origin_y), (sx1, origin_y), 1)

        snap = self.tracker.snapshot()
        px, py = snap["player_x"], snap["player_y"]
        angle = snap["player_angle"]
        angle_rad = math.radians(angle)
        psx, psy, _ = self._to_screen(px, py)

        front_end_x = px + math.sin(angle_rad) * snap["front_distance"]
        front_end_y = py + math.cos(angle_rad) * snap["front_distance"]
        fex, fey, _ = self._to_screen(front_end_x, front_end_y)
        pygame.draw.line(self.screen, RAY_COLOR, (psx, psy), (fex, fey), 1)

        right_angle = angle_rad
        right_end_x = px + math.cos(right_angle) * snap["right_distance"]
        right_end_y = py - math.sin(right_angle) * snap["right_distance"]
        rex, rey, _ = self._to_screen(right_end_x, right_end_y)
        pygame.draw.line(self.screen, RAY_COLOR, (psx, psy), (rex, rey), 1)

        pygame.draw.circle(self.screen, PLAYER_COLOR, (int(psx), int(psy)), 9)
        arrow_len = 22
        tip_x = psx + math.sin(angle_rad) * arrow_len
        tip_y = psy - math.cos(angle_rad) * arrow_len
        pygame.draw.line(self.screen, PLAYER_COLOR, (psx, psy), (tip_x, tip_y), 3)

        info_lines = [
            f"X: {px:.1f} cm   Y: {py:.1f} cm   Angle: {angle:.1f} deg",
            f"Front: {snap['front_distance']:.1f} cm   Right: {snap['right_distance']:.1f} cm",
            f"Tracking: {'ON' if snap['tracking_enabled'] else 'OFF'}   State: {snap['player_state']}",
            f"Sim mode: {'ON' if self.sim_mode else 'OFF'} (toggle in main window)"
        ]
        for i, line in enumerate(info_lines):
            surf = font.render(line, True, TEXT_COLOR)
            self.screen.blit(surf, (10, 10 + i * 20))

        pygame.display.flip()

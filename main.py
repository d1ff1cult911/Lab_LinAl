import pygame
import math
import sys

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((1000, 800))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

# Общие настройки
BG_COLOR = (30, 30, 30)
AXIS_COLORS = {'x': (255, 50, 50), 'y': (50, 255, 50), 'z': (50, 50, 255)}
SCALE = 40



class SurfaceVisualizer:
    def __init__(self):
        self.angle_x = 0.5
        self.angle_y = 0.5
        self.scale = SCALE
        self.dragging = False
        self.last_mouse = (0, 0)
        self.surface_type = 0  # 0-4 для выбора поверхности

    def generate_points(self, params):
        points = []
        u_min, u_max, v_min, v_max, u_step, v_step = params['ranges']
        u = u_min
        while u < u_max+u_step:
            row = []
            v = v_min
            while v < v_max+v_step:
                if self.surface_type == 0:
                    # Спиральная поверхность
                    x = (params['alpha'] + params['beta'] * math.cos(v)) * math.cos(u)
                    y = (params['alpha'] + params['beta'] * math.cos(v)) * math.sin(u)
                    z = params['beta'] * math.sin(v) + params['alpha'] * u
                elif self.surface_type == 1:
                    # Мёбиус
                    x = (params['alpha'] + v * math.cos(u / 2)) * math.cos(u)
                    y = (params['alpha'] + v * math.cos(u / 2)) * math.sin(u)
                    z = params['beta'] * v * math.sin(u / 2)
                elif self.surface_type == 2:
                    # Тор
                    x = (params['alpha'] + params['beta'] * math.cos(v)) * math.cos(u)
                    y = (params['alpha'] + params['beta'] * math.cos(v)) * math.sin(u)
                    z = params['beta'] * math.sin(v)
                elif self.surface_type == 3:
                    # Винтовая
                    x = params['alpha'] * u * math.cos(u)
                    y = params['beta'] * u * math.sin(u)
                    z = v
                elif self.surface_type == 4:
                    # Раковина
                    x = params['alpha'] * math.exp(params['beta'] * v) * math.cos(v) * (1 + math.cos(u))
                    y = params['alpha'] * math.exp(params['beta'] * v) * math.sin(v) * (1 + math.cos(u))
                    z = params['alpha'] * math.exp(params['beta'] * v) * math.sin(u)
                row.append((x, y, z))
                v += v_step
            points.append(row)
            u += u_step
        return points

    def project(self, point):
        x, y, z = point
        # Поворот
        y_rot = y * math.cos(self.angle_x) - z * math.sin(self.angle_x)
        z_rot = y * math.sin(self.angle_x) + z * math.cos(self.angle_x)
        x_rot = x * math.cos(self.angle_y) + z_rot * math.sin(self.angle_y)
        # Проекция
        return int(x_rot * self.scale + 500), int(y_rot * self.scale + 400)

    def draw_axes(self, screen):
        axes = [
            (50, 0, 0, 'X'),
            (0, 50, 0, 'Y'),
            (0, 0, 50, 'Z')
        ]
        for axis in axes:
            end = self.project(axis[:3])
            start = self.project((0, 0, 0))
            pygame.draw.line(screen, AXIS_COLORS[axis[3].lower()], start, end, 2)
            text = font.render(axis[3], True, AXIS_COLORS[axis[3].lower()])
            screen.blit(text, end)

    def draw_surface(self, screen, points, color):
        for i in range(len(points)-1):
            for j in range(len(points[i]) - 1):
                try:
                    p1 = self.project(points[i][j])
                    p2 = self.project(points[i][j + 1])
                    p3 = self.project(points[i + 1][j + 1])
                    p4 = self.project(points[i + 1][j])
                    pygame.draw.polygon(screen, color, [p1, p2, p3, p4])
                except:
                    continue

    def run(self):
        params = [
            {'alpha': 3, 'beta': 1, 'ranges': [0, 4 * math.pi, 0, 2 * math.pi, 0.2, 0.2]},
            {'alpha': 2, 'beta': 1, 'ranges': [0, 2 * math.pi, -0.5, 0.5, 0.2, 0.1]},
            {'alpha': 3, 'beta': 1, 'ranges': [0, 2 * math.pi, 0, 2 * math.pi, 0.2, 0.2]},
            {'alpha': 1, 'beta': 1, 'ranges': [0, 4 * math.pi, -2, 2, 0.3, 0.2]},
            {'alpha': 0.3, 'beta': 0.1, 'ranges': [0, 2 * math.pi, 0, 6 * math.pi, 0.2, 0.1]}
        ]
        colors = [
            (100, 200, 200), (200, 100, 200), (200, 200, 100),
            (100, 200, 100), (200, 100, 100)
        ]

        while True:
            screen.fill(BG_COLOR)
            current_params = params[self.surface_type]
            points = self.generate_points(current_params)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.dragging = True
                    self.last_mouse = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    mouse = pygame.mouse.get_pos()
                    dx = mouse[0] - self.last_mouse[0]
                    dy = mouse[1] - self.last_mouse[1]
                    self.angle_y += dx * 0.01
                    self.angle_x -= dy * 0.01
                    self.last_mouse = mouse
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.surface_type = (self.surface_type + 1) % 5
                    elif event.key == pygame.K_LEFT:
                        self.surface_type = (self.surface_type - 1) % 5

            self.draw_surface(screen, points, colors[self.surface_type])
            self.draw_axes(screen)
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    visualizer = SurfaceVisualizer()
    visualizer.run()
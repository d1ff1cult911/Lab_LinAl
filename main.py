import pygame
import math
import sys
from pygame.locals import *

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((1200, 900))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

# Настройки
BG_COLOR = (30, 30, 30)
GRADIENT_COLORS = {
    'base': (100, 200, 250),  # Базовый цвет (голубой)
    'dark': (20, 50, 80)  # Темный цвет для градиента
}
SCALE = 45
ROT_SPEED = 0.02
FPS = 60


class SurfaceVisualizer:
    def __init__(self):
        self.angle_x = 0.5
        self.angle_y = 0.5
        self.scale = SCALE
        self.dragging = False
        self.last_mouse = (0, 0)
        self.surface_type = 0
        self.z_min = 0
        self.z_max = 1
        self.params = [
            {  # 0: Спиральная поверхность
                'alpha': 3.0,
                'beta': 1.0,
                'ranges': [0, 4 * math.pi, 0, 2 * math.pi, 0.2, 0.2],
                'color': (100, 200, 200)
            },
            {  # 1: Поверхность Мёбиуса
                'alpha': 2.0,
                'beta': 1.0,
                'ranges': [0, 2 * math.pi, -0.5, 0.5, 0.2, 0.1],
                'color': (200, 100, 200)
            },
            {  # 2: Тор
                'alpha': 3.0,
                'beta': 1.0,
                'ranges': [0, 2 * math.pi, 0, 2 * math.pi, 0.2, 0.2],
                'color': (200, 200, 100)
            },
            {  # 3: Винтовая поверхность
                'alpha': 1.0,
                'beta': 1.0,
                'ranges': [0, 4 * math.pi, -2, 2, 0.3, 0.2],
                'color': (100, 200, 100)
            },
            {  # 4: Морская раковина
                'alpha': 0.3,
                'beta': 0.1,
                'ranges': [0, 2 * math.pi, 0, 6 * math.pi, 0.2, 0.1],
                'color': (200, 100, 100)
            }
        ]

    def calculate_gradient(self, z):
        """Рассчет цвета с градиентом и затемнением"""
        t = (z - self.z_min) / (self.z_max - self.z_min)
        base_color = self.params[self.surface_type]['color']
        r = int(base_color[0] * (1 - t) + GRADIENT_COLORS['dark'][0] * t)
        g = int(base_color[1] * (1 - t) + GRADIENT_COLORS['dark'][1] * t)
        b = int(base_color[2] * (1 - t) + GRADIENT_COLORS['dark'][2] * t)
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def generate_points(self):
        params = self.params[self.surface_type]
        u_min, u_max, v_min, v_max, u_step, v_step = params['ranges']
        points = []
        z_values = []

        u = u_min
        while u < u_max + u_step:
            row = []
            v = v_min
            while v < v_max + v_step:
                if self.surface_type == 0:
                    # Спиральная поверхность
                    x = (params['alpha'] + params['beta'] * math.cos(v)) * math.cos(u)
                    y = (params['alpha'] + params['beta'] * math.cos(v)) * math.sin(u)
                    z = params['beta'] * math.sin(v) + params['alpha'] * u
                elif self.surface_type == 1:
                    # Поверхность Мёбиуса
                    x = (params['alpha'] + v * math.cos(u / 2)) * math.cos(u)
                    y = (params['alpha'] + v * math.cos(u / 2)) * math.sin(u)
                    z = params['beta'] * v * math.sin(u / 2)
                elif self.surface_type == 2:
                    # Тор
                    x = (params['alpha'] + params['beta'] * math.cos(v)) * math.cos(u)
                    y = (params['alpha'] + params['beta'] * math.cos(v)) * math.sin(u)
                    z = params['beta'] * math.sin(v)
                elif self.surface_type == 3:
                    # Винтовая поверхность
                    x = params['alpha'] * u * math.cos(u)
                    y = params['beta'] * u * math.sin(u)
                    z = v
                elif self.surface_type == 4:
                    # Морская раковина
                    x = params['alpha'] * math.exp(params['beta'] * v) * math.cos(v) * (1 + math.cos(u))
                    y = params['alpha'] * math.exp(params['beta'] * v) * math.sin(v) * (1 + math.cos(u))
                    z = params['alpha'] * math.exp(params['beta'] * v) * math.sin(u)

                row.append((x, y, z))
                z_values.append(z)
                v += v_step
            points.append(row)
            u += u_step

        self.z_min = min(z_values)
        self.z_max = max(z_values)
        return points

    def project(self, point):
        x, y, z = point
        # Поворот вокруг оси X
        y_rot = y * math.cos(self.angle_x) - z * math.sin(self.angle_x)
        z_rot = y * math.sin(self.angle_x) + z * math.cos(self.angle_x)
        # Поворот вокруг оси Y
        x_rot = x * math.cos(self.angle_y) + z_rot * math.sin(self.angle_y)
        z_final = -x * math.sin(self.angle_y) + z_rot * math.cos(self.angle_y)
        # Проекция и центрирование
        return (int(x_rot * self.scale + 600), int(y_rot * self.scale + 450), z_final)

    def draw_axes(self, screen):
        axes = [
            (50, 0, 0, 'X'),
            (0, 50, 0, 'Y'),
            (0, 0, 50, 'Z')
        ]
        for axis in axes:
            start = self.project((0, 0, 0))
            end = self.project(axis[:3])
            color = (150, 150, 150)
            pygame.draw.line(screen, color, start[:2], end[:2], 2)
            text = font.render(axis[3], True, color)
            screen.blit(text, end[:2])

    def draw_surface(self, screen, points):
        polygons = []
        for i in range(len(points) - 1):
            for j in range(len(points[i]) - 1):
                p1 = self.project(points[i][j])
                p2 = self.project(points[i][j + 1])
                p3 = self.project(points[i + 1][j + 1])
                p4 = self.project(points[i + 1][j])

                # Средняя глубина для затемнения
                avg_z = (p1[2] + p2[2] + p3[2] + p4[2]) / 4
                color = self.calculate_gradient(avg_z)
                polygons.append((avg_z, [p1[:2], p2[:2], p3[:2], p4[:2]], color))

        # Сортировка и отрисовка
        for poly in sorted(polygons, key=lambda x: -x[0]):
            try:
                pygame.draw.polygon(screen, poly[2], poly[1])
            except:
                continue

    def run(self):
        while True:
            screen.fill(BG_COLOR)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    self.dragging = True
                    self.last_mouse = pygame.mouse.get_pos()
                elif event.type == MOUSEBUTTONUP:
                    self.dragging = False
                elif event.type == MOUSEMOTION and self.dragging:
                    mouse = pygame.mouse.get_pos()
                    dx = mouse[0] - self.last_mouse[0]
                    dy = mouse[1] - self.last_mouse[1]
                    self.angle_y += dx * 0.005
                    self.angle_x -= dy * 0.005
                    self.last_mouse = mouse
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        self.surface_type = (self.surface_type + 1) % 5
                    elif event.key == K_LEFT:
                        self.surface_type = (self.surface_type - 1) % 5

            points = self.generate_points()
            self.draw_surface(screen, points)
            self.draw_axes(screen)

            # Отображение текущей поверхности
            text = font.render(f'Surface {self.surface_type + 1}', True, (255, 255, 255))
            screen.blit(text, (20, 20))

            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    visualizer = SurfaceVisualizer()
    visualizer.run()
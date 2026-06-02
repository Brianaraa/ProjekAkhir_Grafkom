import pygame
import math
from core.base import BaseShape
from core.pattern import PatternGenerator, PatternStyle
from fitur.algoritma import ManualAlgorithms
from core.math_utils import rotate_3d, project_3d_to_2d

class Bintang(BaseShape):
    """
    Implementasi Objek 2D Bintang.
    Full pipeline: Mirroring → Skew → Rotasi Z → Proyeksi Perspektif → Fill Pattern → Bresenham Outline.
    """
    def __init__(self, x, y, z, color, outer_radius=50, inner_radius=20):
        super().__init__(x, y, z, color)
        self.base_outer_radius = max(outer_radius, 1)
        self.base_inner_radius = max(inner_radius, 1)
        self.angle_z = 0
        self.fill_type = PatternStyle.FILL_SOLID
        self.outline_color = (0, 0, 0)

    def _get_local_points(self):
        outer = self.base_outer_radius * self.scale
        inner = self.base_inner_radius * self.scale
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = outer if i % 2 == 0 else inner
            lx = r * math.cos(angle)
            ly = r * math.sin(angle)
            points.append((lx, ly, 0))
        return points

    def draw(self, surface):
        current_outer = self.base_outer_radius * self.scale
        if current_outer <= 0:
            return

        local_points = self._get_local_points()

        projected_points = []
        for px, py, pz in local_points:
            px, py, pz = self.apply_mirroring(px, py, pz)
            px, py, pz = self.apply_skew(px, py, pz)
            rx, ry, rz = rotate_3d(px, py, pz, 0, 0, self.angle_z)
            fx, fy = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
            projected_points.append((fx, fy))

        min_x = min(p[0] for p in projected_points)
        max_x = max(p[0] for p in projected_points)
        min_y = min(p[1] for p in projected_points)
        max_y = max(p[1] for p in projected_points)
        surf_w = max_x - min_x
        surf_h = max_y - min_y

        if self.fill_type == PatternStyle.FILL_SOLID:
            pygame.draw.polygon(surface, self.color, projected_points)
        elif surf_w > 0 and surf_h > 0:
            temp_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            tile = PatternGenerator.create_fill_pattern(self.fill_type, self.outline_color)
            PatternGenerator.fill_surface_with_pattern(temp_surface, tile)
            mask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            local_pts = [(p[0] - min_x, p[1] - min_y) for p in projected_points]
            pygame.draw.polygon(mask, (255, 255, 255, 255), local_pts)
            temp_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(temp_surface, (min_x, min_y))

        if self.show_outline:
            for i in range(len(projected_points)):
                p1 = projected_points[i]
                p2 = projected_points[(i + 1) % len(projected_points)]
                ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, p1, p2, self.outline_width)

        if self.is_selected:
            self._draw_selection_style(surface, min_x, min_y, surf_w, surf_h)

    def _draw_selection_style(self, surface, min_x, min_y, w, h):
        rect_x, rect_y = int(min_x), int(min_y)
        pygame.draw.rect(surface, (59, 130, 246), (rect_x - 2, rect_y - 2, int(w) + 4, int(h) + 4), 2)
        corners = [(rect_x, rect_y), (rect_x + w, rect_y),
                   (rect_x, rect_y + h), (rect_x + w, rect_y + h)]
        for c in corners:
            pygame.draw.rect(surface, (255, 255, 255), (int(c[0]) - 4, int(c[1]) - 4, 8, 8))
            pygame.draw.rect(surface, (59, 130, 246), (int(c[0]) - 4, int(c[1]) - 4, 8, 8), 2)

    def is_clicked(self, mouse_pos):
        mx, my = mouse_pos
        dx = mx - self.x
        dy = -(my - self.y)
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        dx /= factor
        dy /= factor
        cos_a = math.cos(-self.angle_z)
        sin_a = math.sin(-self.angle_z)
        local_x = dx * cos_a - dy * sin_a
        local_y = dx * sin_a + dy * cos_a
        if self.flip_x:
            local_x = -local_x
        if self.flip_y:
            local_y = -local_y
        c_outer = self.base_outer_radius * self.scale
        return math.hypot(local_x, local_y) <= c_outer

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "outer_radius": self.base_outer_radius,
            "inner_radius": self.base_inner_radius,
            "angle_z": self.angle_z,
            "fill_type": self.fill_type
        })
        return data

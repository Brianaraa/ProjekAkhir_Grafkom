import pygame
import math
from core.base import BaseShape
from core.pattern import PatternGenerator, PatternStyle
from fitur.algoritma import ManualAlgorithms
from core.math_utils import rotate_3d, project_3d_to_2d

class JajarGenjang(BaseShape):
    """
    Implementasi Objek 2D Jajar Genjang.
    Full pipeline: Mirroring → Rotasi Z → Proyeksi Perspektif → Fill Pattern → Bresenham Outline.
    """
    def __init__(self, x, y, z, color, width=100, height=60, offset=30):
        super().__init__(x, y, z, color)
        self.base_width = width
        self.base_height = height
        self.base_offset = offset

        # Rotasi Sumbu Z (Miring/Roll)
        self.angle_z = 0

        # Pengaturan tampilan
        self.fill_type = PatternStyle.FILL_SOLID
        self.outline_color = (0, 0, 0)

    def _get_local_points(self):
        """Hitung 4 titik jajar genjang di ruang lokal."""
        hw = (self.base_width * self.scale) / 2
        hh = (self.base_height * self.scale) / 2
        ho = (self.base_offset * self.scale) / 2
        return [
            (-hw + ho, -hh, 0),
            ( hw + ho, -hh, 0),
            ( hw - ho,  hh, 0),
            (-hw - ho,  hh, 0)
        ]

    def draw(self, surface):
        """Render jajar genjang dengan pipeline transformasi penuh."""
        current_w = self.base_width * self.scale
        current_h = self.base_height * self.scale
        if current_w <= 0 or current_h <= 0:
            return

        local_points = self._get_local_points()

        # Pipeline: Mirroring → Rotasi Z → Proyeksi Perspektif
        projected_points = []
        for px, py, pz in local_points:
            px, py, pz = self.apply_mirroring(px, py, pz)
            rx, ry, rz = rotate_3d(px, py, pz, 0, 0, self.angle_z)
            fx, fy = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
            projected_points.append((fx, fy))

        # Bounding Box Dinamis
        min_x = min(p[0] for p in projected_points)
        max_x = max(p[0] for p in projected_points)
        min_y = min(p[1] for p in projected_points)
        max_y = max(p[1] for p in projected_points)
        surf_w = max_x - min_x
        surf_h = max_y - min_y

        # PROSES FILLING
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

        # OUTLINE MANUAL BRESENHAM
        for i in range(len(projected_points)):
            p1 = projected_points[i]
            p2 = projected_points[(i + 1) % len(projected_points)]
            ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, p1, p2)

        # Indikator Seleksi
        if self.is_selected:
            self._draw_selection_style(surface, min_x, min_y, surf_w, surf_h)

    def _draw_selection_style(self, surface, min_x, min_y, w, h):
        """Visualisasi seleksi dinamis."""
        rect_x, rect_y = int(min_x), int(min_y)
        pygame.draw.rect(surface, (255, 0, 0), (rect_x, rect_y, int(w), int(h)), 1)
        corners = [(rect_x, rect_y), (rect_x + w, rect_y),
                   (rect_x, rect_y + h), (rect_x + w, rect_y + h)]
        for c in corners:
            pygame.draw.rect(surface, (0, 0, 255), (int(c[0]) - 3, int(c[1]) - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Deteksi klik dengan koreksi angle_z (inverse transform) + Ray Casting."""
        mx, my = mouse_pos
        dx = mx - self.x
        dy = -(my - self.y)
        # Inverse proyeksi perspektif
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        dx /= factor
        dy /= factor
        # Rotasi balik -angle_z
        cos_a = math.cos(-self.angle_z)
        sin_a = math.sin(-self.angle_z)
        local_x = dx * cos_a - dy * sin_a
        local_y = dx * sin_a + dy * cos_a
        # Inverse mirroring
        if self.flip_x:
            local_x = -local_x
        if self.flip_y:
            local_y = -local_y

        # Ray Casting pada poligon tanpa rotasi
        hw = (self.base_width * self.scale) / 2
        hh = (self.base_height * self.scale) / 2
        ho = (self.base_offset * self.scale) / 2
        # Titik lokal (Y tidak di-flip karena sudah inverse)
        points = [
            (-hw + ho, -hh),
            ( hw + ho, -hh),
            ( hw - ho,  hh),
            (-hw - ho,  hh)
        ]

        inside = False
        n = len(points)
        p1x, p1y = points[0]
        for i in range(1, n + 1):
            p2x, p2y = points[i % n]
            if local_y > min(p1y, p2y):
                if local_y <= max(p1y, p2y):
                    if local_x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (local_y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or local_x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "width": self.base_width,
            "height": self.base_height,
            "offset": self.base_offset,
            "angle_z": self.angle_z,
            "fill_type": self.fill_type
        })
        return data

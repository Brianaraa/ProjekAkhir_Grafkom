import pygame
import math
from core.base import BaseShape
from core.pattern import PatternGenerator, PatternStyle
from fitur.algoritma import ManualAlgorithms
from core.math_utils import rotate_3d, project_3d_to_2d

class Donut(BaseShape):
    """
    Implementasi Objek 2D Donut (Cincin).
    Berbasis poligon titik agar mendukung Mirroring, Rotasi Z, dan Fill Pattern.
    Full pipeline: Mirroring → Rotasi Z → Proyeksi Perspektif → Fill Masking → Bresenham Outline.
    """
    def __init__(self, x, y, z, color, outer_radius=60, inner_radius=30):
        super().__init__(x, y, z, color)
        self.base_outer_radius = max(outer_radius, 1)
        self.base_inner_radius = min(inner_radius, self.base_outer_radius - 1)

        # Rotasi Sumbu Z
        self.angle_z = 0

        # Pengaturan tampilan
        self.fill_type = PatternStyle.FILL_SOLID
        self.outline_color = (0, 0, 0)

        # Resolusi lingkaran (jumlah segmen)
        self._segments = 36

    def _generate_circle_points(self, radius):
        """Generate titik-titik lingkaran di ruang lokal (pusat 0,0)."""
        points = []
        for i in range(self._segments):
            theta = 2 * math.pi * i / self._segments
            lx = radius * math.cos(theta)
            ly = radius * math.sin(theta)
            points.append((lx, ly, 0))
        return points

    def _transform_points(self, local_points):
        """Pipeline Mirroring → Skew → Rotasi Z → Proyeksi Perspektif."""
        projected = []
        for px, py, pz in local_points:
            px, py, pz = self.apply_mirroring(px, py, pz)
            px, py, pz = self.apply_skew(px, py, pz)
            rx, ry, rz = rotate_3d(px, py, pz, 0, 0, self.angle_z)
            fx, fy = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
            projected.append((fx, fy))
        return projected

    def draw(self, surface):
        """Render donut sebagai cincin poligon dengan lubang di tengah."""
        outer_r = self.base_outer_radius * self.scale
        inner_r = self.base_inner_radius * self.scale
        if outer_r <= 0:
            return

        # 1. Generate titik lokal & transformasi
        outer_local = self._generate_circle_points(outer_r)
        inner_local = self._generate_circle_points(inner_r)
        outer_proj = self._transform_points(outer_local)
        inner_proj = self._transform_points(inner_local)

        # 2. Hitung Bounding Box dari semua titik
        all_pts = outer_proj + inner_proj
        min_x = min(p[0] for p in all_pts)
        max_x = max(p[0] for p in all_pts)
        min_y = min(p[1] for p in all_pts)
        max_y = max(p[1] for p in all_pts)
        surf_w = int(max_x - min_x) + 2
        surf_h = int(max_y - min_y) + 2
        if surf_w <= 0 or surf_h <= 0:
            return

        # Koordinat relatif ke bounding box
        outer_rel = [(p[0] - min_x + 1, p[1] - min_y + 1) for p in outer_proj]
        inner_rel = [(p[0] - min_x + 1, p[1] - min_y + 1) for p in inner_proj]

        # 3. PROSES FILLING (Ring = outer filled minus inner hole)
        if self.fill_type == PatternStyle.FILL_SOLID:
            # Buat surface ring dengan alpha
            ring_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            pygame.draw.polygon(ring_surf, (*self.color, 255), outer_rel)
            # Buat mask untuk lubang tengah
            hole_mask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            hole_mask.fill((255, 255, 255, 255))
            pygame.draw.polygon(hole_mask, (0, 0, 0, 0), inner_rel)
            ring_surf.blit(hole_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(ring_surf, (min_x - 1, min_y - 1))
        else:
            # Pattern fill untuk ring
            ring_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            tile = PatternGenerator.create_fill_pattern(self.fill_type, self.outline_color)
            PatternGenerator.fill_surface_with_pattern(ring_surf, tile)
            # Mask: outer polygon
            outer_mask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            pygame.draw.polygon(outer_mask, (255, 255, 255, 255), outer_rel)
            ring_surf.blit(outer_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            # Potong lubang inner
            hole_mask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            hole_mask.fill((255, 255, 255, 255))
            pygame.draw.polygon(hole_mask, (0, 0, 0, 0), inner_rel)
            ring_surf.blit(hole_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(ring_surf, (min_x - 1, min_y - 1))

        # 4. OUTLINE MANUAL BRESENHAM (lingkaran luar + lingkaran dalam)
        if self.show_outline:
            for i in range(self._segments):
                p1 = outer_proj[i]; p2 = outer_proj[(i + 1) % self._segments]
                ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, p1, p2, self.outline_width)
            for i in range(self._segments):
                p1 = inner_proj[i]; p2 = inner_proj[(i + 1) % self._segments]
                ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, p1, p2, self.outline_width)

        # 5. Indikator Seleksi
        if self.is_selected:
            self._draw_selection_style(surface, min_x, min_y, surf_w, surf_h)

    def _draw_selection_style(self, surface, min_x, min_y, w, h):
        rx, ry = int(min_x)-2, int(min_y)-2
        pygame.draw.rect(surface, (59,130,246), (rx, ry, int(w)+4, int(h)+4), 2)
        for c in [(rx,ry),(rx+int(w)+4,ry),(rx,ry+int(h)+4),(rx+int(w)+4,ry+int(h)+4)]:
            pygame.draw.rect(surface, (255,255,255), (c[0]-3, c[1]-3, 7, 7))
            pygame.draw.rect(surface, (59,130,246), (c[0]-3, c[1]-3, 7, 7), 1)

    def is_clicked(self, mouse_pos):
        """Deteksi klik area cincin dengan inverse rotation."""
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

        # Cek apakah di area cincin (antara inner dan outer radius)
        distance = math.hypot(local_x, local_y)
        c_outer = self.base_outer_radius * self.scale
        c_inner = self.base_inner_radius * self.scale
        return c_inner <= distance <= c_outer

    def to_dict(self):
        """Alur Data untuk fungsionalitas Save (JSON)."""
        data = super().to_dict()
        data.update({
            "outer_radius": self.base_outer_radius,
            "inner_radius": self.base_inner_radius,
            "angle_z": self.angle_z,
            "fill_type": self.fill_type
        })
        return data
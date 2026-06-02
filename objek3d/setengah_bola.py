import pygame
import math
from core.base import BaseShape
from core.math_utils import rotate_3d, project_3d_to_2d

class SetengahBola(BaseShape):
    """
    Implementasi Objek 3D Setengah Bola - Dirancang oleh System Architect (B).
    Wireframe berbasis vertex dengan Rotasi 3D penuh (WASDQE) + Skew.
    """
    def __init__(self, x, y, z, color, radius=50):
        super().__init__(x, y, z, color)
        self.base_radius = max(radius, 1)
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

    def _apply_transforms(self, vx, vy, vz):
        """Rotasi 3D + Proyeksi Perspektif menggunakan Math Utils."""
        vx, vy, vz = self.apply_mirroring(vx, vy, vz)
        vx, vy, vz = self.apply_skew(vx, vy, vz)
        rx, ry, rz = rotate_3d(vx, vy, vz, self.angle_x, self.angle_y, self.angle_z)
        px, py = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
        return (int(px), int(py))

    def draw(self, surface):
        """Merender Setengah Bola 3D wireframe yang bisa dirotasi."""
        r = self.base_radius * self.scale
        if r <= 0:
            return

        segments = 24
        t = max(1, self.outline_width)

        # 1. Gambar lingkaran alas (equator)
        equator_pts = []
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            equator_pts.append(self._apply_transforms(r * math.cos(theta), 0, r * math.sin(theta)))

        # 2. Gambar 2 lingkaran lintang (latitude) di bagian kubah
        latitude_pts_1 = []
        latitude_pts_2 = []
        for lat_frac, lat_pts in [(0.35, latitude_pts_1), (0.70, latitude_pts_2)]:
            lat_y = r * math.sin(lat_frac * math.pi / 2)
            lat_r = r * math.cos(lat_frac * math.pi / 2)
            if lat_r > 0:
                for i in range(segments):
                    theta = 2 * math.pi * i / segments
                    lat_pts.append(self._apply_transforms(lat_r * math.cos(theta), lat_y, lat_r * math.sin(theta)))

        # 3. Gambar garis meridian dari equator ke puncak
        apex = self._apply_transforms(0, r, 0)

        if self.show_outline:
            for i in range(segments):
                pygame.draw.line(surface, self.color, equator_pts[i], equator_pts[(i + 1) % segments], t)
            
            if len(latitude_pts_1) > 0:
                for i in range(segments):
                    pygame.draw.line(surface, self.color, latitude_pts_1[i], latitude_pts_1[(i + 1) % segments], t)
            if len(latitude_pts_2) > 0:
                for i in range(segments):
                    pygame.draw.line(surface, self.color, latitude_pts_2[i], latitude_pts_2[(i + 1) % segments], t)

            meridian_count = 8
            step = segments // meridian_count
            for i in range(meridian_count):
                eq_pt = equator_pts[i * step]
                pygame.draw.line(surface, self.color, eq_pt, apex, t)

        # 4. Indikator Seleksi
        if self.is_selected:
            all_pts = equator_pts + [apex] + latitude_pts_1 + latitude_pts_2
            min_x = min(p[0] for p in all_pts)
            max_x = max(p[0] for p in all_pts)
            min_y = min(p[1] for p in all_pts)
            max_y = max(p[1] for p in all_pts)
            
            rx, ry = int(min_x) - 2, int(min_y) - 2
            rw, rh = int(max_x - min_x) + 4, int(max_y - min_y) + 4
            pygame.draw.rect(surface, (59, 130, 246), (rx, ry, rw, rh), 2)
            for p in [(rx, ry), (rx + rw, ry), (rx, ry + rh), (rx + rw, ry + rh)]:
                pygame.draw.rect(surface, (255, 255, 255), (p[0] - 3, p[1] - 3, 7, 7))
                pygame.draw.rect(surface, (59, 130, 246), (p[0] - 3, p[1] - 3, 7, 7), 1)

    def is_clicked(self, mouse_pos):
        """Hit-Detection berdasarkan radius visual proyeksi Z."""
        mx, my = mouse_pos
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        r = self.base_radius * self.scale * factor
        return math.hypot(mx - self.x, my - self.y) <= r

    def to_dict(self):
        data = super().to_dict()
        data["radius"] = self.base_radius
        data["angle_x"] = self.angle_x
        data["angle_y"] = self.angle_y
        data["angle_z"] = self.angle_z
        return data
import pygame
import math
from core.base import BaseShape
from core.math_utils import rotate_3d, project_3d_to_2d

class SetengahBola(BaseShape):
    """
    Implementasi Objek 3D Setengah Bola - Dirancang oleh System Architect (B).
    Wireframe berbasis vertex dengan Rotasi 3D penuh (WASDQE).
    """
    def __init__(self, x, y, z, color, radius=50):
        super().__init__(x, y, z, color)
        self.base_radius = max(radius, 1)
        # Sudut rotasi (dalam radian) — wajib ada agar WASDQE berfungsi
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

    def _apply_transforms(self, vx, vy, vz):
        """Rotasi 3D + Proyeksi Perspektif menggunakan Math Utils."""
        vx, vy, vz = self.apply_mirroring(vx, vy, vz)
        rx, ry, rz = rotate_3d(vx, vy, vz, self.angle_x, self.angle_y, self.angle_z)
        px, py = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
        return (int(px), int(py))

    def draw(self, surface):
        """Merender Setengah Bola 3D wireframe yang bisa dirotasi."""
        r = self.base_radius * self.scale
        if r <= 0:
            return

        segments = 24

        # 1. Gambar lingkaran alas (equator)
        equator_pts = []
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            equator_pts.append(self._apply_transforms(r * math.cos(theta), 0, r * math.sin(theta)))
        for i in range(segments):
            pygame.draw.line(surface, self.color, equator_pts[i], equator_pts[(i + 1) % segments], 2)

        # 2. Gambar 2 lingkaran lintang (latitude) di bagian kubah
        for lat_frac in [0.35, 0.70]:
            lat_y = r * math.sin(lat_frac * math.pi / 2)
            lat_r = r * math.cos(lat_frac * math.pi / 2)
            if lat_r <= 0:
                continue
            pts = []
            for i in range(segments):
                theta = 2 * math.pi * i / segments
                pts.append(self._apply_transforms(lat_r * math.cos(theta), lat_y, lat_r * math.sin(theta)))
            for i in range(segments):
                pygame.draw.line(surface, self.color, pts[i], pts[(i + 1) % segments], 1)

        # 3. Gambar garis meridian dari equator ke puncak
        apex = self._apply_transforms(0, r, 0)
        meridian_count = 8
        step = segments // meridian_count
        for i in range(meridian_count):
            eq_pt = equator_pts[i * step]
            pygame.draw.line(surface, self.color, eq_pt, apex, 1)

        # 4. Indikator Seleksi
        if self.is_selected:
            all_pts = equator_pts + [apex]
            min_x = min(p[0] for p in all_pts)
            max_x = max(p[0] for p in all_pts)
            min_y = min(p[1] for p in all_pts)
            max_y = max(p[1] for p in all_pts)
            pygame.draw.rect(surface, (255, 0, 0), (min_x, min_y, max_x - min_x, max_y - min_y), 1)
            for p in [(min_x, min_y), (max_x, min_y), (min_x, max_y), (max_x, max_y)]:
                pygame.draw.rect(surface, (0, 0, 255), (p[0] - 3, p[1] - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Hit-Detection berdasarkan radius visual proyeksi Z."""
        mx, my = mouse_pos
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        r = self.base_radius * self.scale * factor
        return math.hypot(mx - self.x, my - self.y) <= r

    def to_dict(self):
        """Alur Data untuk Save: Mencatat X, Y, Z, Radius, dan sudut rotasi."""
        data = super().to_dict()
        data["radius"] = self.base_radius
        data["angle_x"] = self.angle_x
        data["angle_y"] = self.angle_y
        data["angle_z"] = self.angle_z
        return data
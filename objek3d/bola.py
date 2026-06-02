import pygame
import math
from core.base import BaseShape
from core.math_utils import rotate_3d

class Bola(BaseShape):
    """
    Implementasi Objek 3D Bola - Dirancang oleh System Architect (B).
    Menerapkan Proyeksi Perspektif nyata + Rotasi 3D penuh (WASDQE) + Skew.
    """
    def __init__(self, x, y, z, color, radius=50):
        super().__init__(x, y, z, color)
        self.base_radius = max(radius, 1)
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

    def _project_vertex(self, vx, vy, vz):
        """Rotasi + Proyeksi Perspektif satu vertex ke koordinat layar."""
        vx, vy, vz = self.apply_mirroring(vx, vy, vz)
        vx, vy, vz = self.apply_skew(vx, vy, vz)
        rx, ry, rz = rotate_3d(vx, vy, vz, self.angle_x, self.angle_y, self.angle_z)
        fov = 400
        z_real = self.z + rz
        factor = fov / (fov + z_real) if (fov + z_real) != 0 else 1
        px = self.x + rx * factor
        py = self.y - ry * factor  # Y dibalik sesuai konvensi layar
        return (int(px), int(py))

    def draw(self, surface):
        """Merender Bola 3D wireframe yang bisa dirotasi penuh."""
        r = self.base_radius * self.scale
        if r <= 0:
            return

        segments = 24
        t = max(1, self.outline_width)

        if self.show_outline:
            # Gambar 3 lingkaran lintang (latitude rings)
            for lat_frac in [-0.5, 0.0, 0.5]:
                lat_y = r * math.sin(lat_frac * math.pi)
                lat_r = r * math.cos(lat_frac * math.pi)
                if lat_r <= 0:
                    continue
                pts = []
                for i in range(segments):
                    theta = 2 * math.pi * i / segments
                    pts.append(self._project_vertex(lat_r * math.cos(theta), lat_y, lat_r * math.sin(theta)))
                for i in range(segments):
                    pygame.draw.line(surface, self.color, pts[i], pts[(i + 1) % segments], t)

            # Gambar 2 lingkaran bujur (longitude rings)
            for lon_idx in range(2):
                pts = []
                for i in range(segments):
                    theta = 2 * math.pi * i / segments
                    if lon_idx == 0:
                        pts.append(self._project_vertex(r * math.cos(theta), r * math.sin(theta), 0))
                    else:
                        pts.append(self._project_vertex(0, r * math.sin(theta), r * math.cos(theta)))
                for i in range(segments):
                    pygame.draw.line(surface, self.color, pts[i], pts[(i + 1) % segments], t)

            # Siluet luar (lingkaran besar berdasarkan proyeksi Z)
            fov = 400
            factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
            proj_radius = int(r * factor)
            if proj_radius > 0:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), proj_radius, t + 1)

        # Hitung bounding box seleksi berdasarkan vertex atau radius visual
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        proj_radius = int(r * factor)

        if self.is_selected:
            self._draw_selection_style(surface, int(self.x), int(self.y), proj_radius)

    def _draw_selection_style(self, surface, px, py, r):
        rect_x, rect_y = px - r - 2, py - r - 2
        size = r * 2 + 4
        pygame.draw.rect(surface, (59, 130, 246), (rect_x, rect_y, size, size), 2)
        for hx, hy in [(rect_x, rect_y), (rect_x + size, rect_y),
                       (rect_x, rect_y + size), (rect_x + size, rect_y + size)]:
            pygame.draw.rect(surface, (255, 255, 255), (hx - 3, hy - 3, 7, 7))
            pygame.draw.rect(surface, (59, 130, 246), (hx - 3, hy - 3, 7, 7), 1)

    def is_clicked(self, mouse_pos):
        """Hit-detection akurat terhadap hasil proyeksi di layar."""
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        proj_radius = self.base_radius * self.scale * factor
        distance = math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        return distance <= proj_radius

    def to_dict(self):
        data = super().to_dict()
        data["radius"] = self.base_radius
        data["angle_x"] = self.angle_x
        data["angle_y"] = self.angle_y
        data["angle_z"] = self.angle_z
        return data
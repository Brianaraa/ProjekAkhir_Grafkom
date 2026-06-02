import pygame
import math
from core.base import BaseShape
from core.pattern import PatternGenerator, PatternStyle
from fitur.algoritma import ManualAlgorithms
from core.math_utils import rotate_3d, project_3d_to_2d

class SetengahLingkaran(BaseShape):
    """
    Implementasi Objek 2D Setengah Lingkaran (Kubah — terbuka ke bawah).
    Full Manual Bresenham untuk garis tepi + Math Utils untuk Z-Depth & Rotasi Z.
    """
    def __init__(self, x, y, z, color, radius=60):
        super().__init__(x, y, z, color)
        self.base_radius = max(radius, 1)

        # Objek 2D murni HANYA punya rotasi Sumbu Z (Miring/Roll)
        self.angle_z = 0

        # Pengaturan tampilan
        self.line_style = PatternStyle.LINE_SOLID
        self.fill_type = PatternStyle.FILL_SOLID
        self.outline_color = (0, 0, 0)

    def draw(self, surface):
        """Render objek dengan kalkulasi titik dinamis, proyeksi 3D, dan algoritma manual."""
        r = self.base_radius * self.scale
        if r <= 0:
            return

        # 1. Tentukan titik lokal (mengelilingi pusat 0,0)
        #    theta 0..pi = setengah lingkaran ATAS (kubah)
        local_points = []
        for i in range(31):
            theta = math.pi * i / 30
            px = r * math.cos(theta)
            py = -r * math.sin(theta)  # Negatif agar kubah menghadap ke atas
            local_points.append((px, py, 0))

        # 2. Transform pipeline: Mirroring → Skew → Rotasi Z → Proyeksi
        projected_points = []
        for px, py, pz in local_points:
            px, py, pz = self.apply_mirroring(px, py, pz)
            px, py, pz = self.apply_skew(px, py, pz)
            rx, ry, rz = rotate_3d(px, py, pz, 0, 0, self.angle_z)
            fx, fy = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
            projected_points.append((fx, fy))

        # --- MENGHITUNG BOUNDING BOX DINAMIS ---
        min_x = min(p[0] for p in projected_points)
        max_x = max(p[0] for p in projected_points)
        min_y = min(p[1] for p in projected_points)
        max_y = max(p[1] for p in projected_points)

        surf_w = max_x - min_x
        surf_h = max_y - min_y

        # 3. PROSES FILLING
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

        # 4. PROSES OUTLINE (FULL MANUAL BRESENHAM)
        if self.show_outline:
            for i in range(len(projected_points) - 1):
                ManualAlgorithms.draw_line_bresenham(
                    surface, self.outline_color, projected_points[i], projected_points[i + 1], self.outline_width
                )
            ManualAlgorithms.draw_line_bresenham(
                surface, self.outline_color, projected_points[-1], projected_points[0], self.outline_width
            )

        # 5. Indikator Seleksi (Bounding Box)
        if self.is_selected:
            self._draw_selection_style(surface, min_x, min_y, surf_w, surf_h)

    def _draw_selection_style(self, surface, min_x, min_y, w, h):
        rx, ry = int(min_x)-2, int(min_y)-2
        pygame.draw.rect(surface, (59,130,246), (rx, ry, int(w)+4, int(h)+4), 2)
        for c in [(rx,ry),(rx+int(w)+4,ry),(rx,ry+int(h)+4),(rx+int(w)+4,ry+int(h)+4)]:
            pygame.draw.rect(surface, (255,255,255), (c[0]-3, c[1]-3, 7, 7))
            pygame.draw.rect(surface, (59,130,246), (c[0]-3, c[1]-3, 7, 7), 1)

    def is_clicked(self, mouse_pos):
        """Deteksi klik dengan koreksi angle_z (inverse transform), sama seperti BelahKetupat."""
        mx, my = mouse_pos
        # Translate ke koordinat lokal relatif pusat objek
        dx = mx - self.x
        dy = -(my - self.y)  # Balik Y sesuai konvensi project_3d_to_2d
        # Inverse proyeksi perspektif
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        dx /= factor
        dy /= factor
        # Rotasi balik sebesar -angle_z
        cos_a = math.cos(-self.angle_z)
        sin_a = math.sin(-self.angle_z)
        local_x = dx * cos_a - dy * sin_a
        local_y = dx * sin_a + dy * cos_a
        # Dalam ruang lokal: kubah adalah setengah lingkaran di sisi local_y >= 0
        r = self.base_radius * self.scale
        return math.hypot(local_x, local_y) <= r and local_y >= 0

    def to_dict(self):
        """Export data untuk sistem Save/Load JSON."""
        data = super().to_dict()
        data.update({
            "radius": self.base_radius,
            "fill_type": self.fill_type,
            "angle_z": self.angle_z
        })
        return data
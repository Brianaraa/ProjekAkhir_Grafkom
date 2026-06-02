import pygame
import math
from core.base import BaseShape
from fitur.algoritma import ManualAlgorithms 
from core.math_utils import rotate_3d, project_3d_to_2d

class Kerucut(BaseShape):
    """
    Implementasi Objek 3D Kerucut.
    Full Manual Bresenham
    FITUR: Rotasi 3D + Proyeksi Perspektif + Wireframe Manual + Skew.
    """
    def __init__(self, x, y, z, color, radius=50, height=100):
        super().__init__(x, y, z, color)
        self.base_radius = radius
        self.base_height = height
        
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        
        self.outline_color = color

    def _apply_transforms(self, vx, vy, vz):
        """Transformasi 3D ke 2D menggunakan Math Utils."""
        vx, vy, vz = self.apply_mirroring(vx, vy, vz)
        vx, vy, vz = self.apply_skew(vx, vy, vz)
        rx, ry, rz = rotate_3d(vx, vy, vz, self.angle_x, self.angle_y, self.angle_z)
        px, py = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
        return px, py

    def draw(self, surface):
        """Render Kerucut menggunakan algoritma Bresenham manual."""
        current_r = self.base_radius * self.scale
        current_h = self.base_height * self.scale
        
        segments = 24 
        
        # Puncak berada di tengah atas (height/2)
        apex_2d = self._apply_transforms(0, current_h / 2, 0)
        
        # Alas berada di posisi bawah (-height/2)
        base_points = []
        for i in range(segments):
            theta = (2 * math.pi * i) / segments
            bx = current_r * math.cos(theta)
            bz = current_r * math.sin(theta)
            base_points.append(self._apply_transforms(bx, -current_h / 2, bz))
            
        # PROSES RENDERING (FULL MANUAL BRESENHAM)
        if self.show_outline:
            t = max(1, self.outline_width)
            for i in range(segments):
                p1 = base_points[i]
                p2 = base_points[(i + 1) % segments]
                
                # Gambar Garis Lingkaran Alas
                ManualAlgorithms.draw_line_bresenham(surface, self.color, p1, p2, t)
                
                # Gambar Garis Selimut setiap 2 segmen
                if i % 2 == 0: 
                    ManualAlgorithms.draw_line_bresenham(surface, self.color, p1, apex_2d, t)

        # 4. Indikator Seleksi
        if self.is_selected:
            all_pts = base_points + [apex_2d]
            min_x = min([p[0] for p in all_pts])
            max_x = max([p[0] for p in all_pts])
            min_y = min([p[1] for p in all_pts])
            max_y = max([p[1] for p in all_pts])
            
            rx, ry = int(min_x) - 2, int(min_y) - 2
            rw, rh = int(max_x - min_x) + 4, int(max_y - min_y) + 4
            pygame.draw.rect(surface, (59, 130, 246), (rx, ry, rw, rh), 2)
            for p in [(rx, ry), (rx + rw, ry), (rx, ry + rh), (rx + rw, ry + rh)]:
                pygame.draw.rect(surface, (255, 255, 255), (p[0] - 3, p[1] - 3, 7, 7))
                pygame.draw.rect(surface, (59, 130, 246), (p[0] - 3, p[1] - 3, 7, 7), 1)

    def is_clicked(self, mouse_pos):
        mx, my = mouse_pos
        bound = max(self.base_radius, self.base_height / 2) * self.scale
        return math.hypot(mx - self.x, my - self.y) <= bound

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "radius": self.base_radius,
            "height": self.base_height,
            "angle_x": self.angle_x,
            "angle_y": self.angle_y,
            "angle_z": self.angle_z
        })
        return data
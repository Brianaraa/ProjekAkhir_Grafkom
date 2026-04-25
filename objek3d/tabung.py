import pygame
import math
from core.base import BaseShape
from fitur.algoritma import ManualAlgorithms 
from core.math_utils import rotate_3d, project_3d_to_2d

class Tabung(BaseShape):
    """
    Implementasi Objek 3D Tabung.
    Full Manual Bresenham
    FITUR: Rotasi 3D + Proyeksi Perspektif + Wireframe Manual.
    """
    def __init__(self, x, y, z, color, radius=40, height=80):
        super().__init__(x, y, z, color)
        self.base_radius = radius
        self.base_height = height
        
        # Sudut rotasi (dalam radian)
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        
        # Warna garis tepi
        self.outline_color = color

    def _apply_transforms(self, vx, vy, vz):
        """Transformasi 3D ke 2D menggunakan Math Utils."""
        
        # 1. Gunakan fungsi rotate_3d dari math_utils
        rx, ry, rz = rotate_3d(vx, vy, vz, self.angle_x, self.angle_y, self.angle_z)

        # 2. Gunakan fungsi project_3d_to_2d dari math_utils
        # Perhatikan: rz ditambah self.z untuk mendapatkan kedalaman absolut
        px, py = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
        
        return px, py

    def draw(self, surface):
        """Render wireframe tabung menggunakan algoritma Bresenham manual."""
        current_r = self.base_radius * self.scale
        current_h = self.base_height * self.scale
        
        # Gunakan 24 segmen agar lingkaran atas/bawah terlihat halus
        segments = 24 
        
        top_circle = []
        bottom_circle = []
        
        # Kalkulasi titik-titik lingkaran atas dan bawah
        for i in range(segments):
            theta = (2 * math.pi * i) / segments
            tx = current_r * math.cos(theta)
            tz = current_r * math.sin(theta)
            
            # Simpan koordinat 2D hasil transformasi
            top_circle.append(self._apply_transforms(tx, current_h / 2, tz))
            bottom_circle.append(self._apply_transforms(tx, -current_h / 2, tz))
            
        # PROSES RENDERING (FULL MANUAL BRESENHAM)
        for i in range(segments):
            t1, t2 = top_circle[i], top_circle[(i + 1) % segments]
            b1, b2 = bottom_circle[i], bottom_circle[(i + 1) % segments]
            
            # 1. Gambar Lingkaran Atas (Manual)
            ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, t1, t2)
            
            # 2. Gambar Lingkaran Bawah (Manual)
            ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, b1, b2)
            
            # 3. Gambar Tiang Penghubung (Garis Tegak Manual)
            # Kita gambar tiang setiap 4 segmen agar wireframe terlihat bersih
            if i % 4 == 0:
                ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, t1, b1)

        # 4. Indikator Seleksi
        if self.is_selected:
            all_pts = top_circle + bottom_circle
            min_x = min([p[0] for p in all_pts])
            max_x = max([p[0] for p in all_pts])
            min_y = min([p[1] for p in all_pts])
            max_y = max([p[1] for p in all_pts])
            
            pygame.draw.rect(surface, (255, 0, 0), (min_x, min_y, max_x - min_x, max_y - min_y), 1)
            for p in [(min_x, min_y), (max_x, min_y), (min_x, max_y), (max_x, max_y)]:
                pygame.draw.rect(surface, (0, 0, 255), (int(p[0]) - 3, int(p[1]) - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Deteksi klik sederhana berdasarkan area terluar objek."""
        mx, my = mouse_pos
        bound = max(self.base_radius, self.base_height / 2) * self.scale
        return math.hypot(mx - self.x, my - self.y) <= bound

    def to_dict(self):
        """Simpan data posisi, ukuran, dan sudut rotasi ke JSON."""
        data = super().to_dict()
        data.update({
            "radius": self.base_radius,
            "height": self.base_height,
            "angle_x": self.angle_x,
            "angle_y": self.angle_y,
            "angle_z": self.angle_z
        })
        return data
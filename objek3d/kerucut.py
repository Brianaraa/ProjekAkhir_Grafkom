import pygame
import math
from core.base import BaseShape
from fitur.algoritma import ManualAlgorithms 
from core.math_utils import rotate_3d, project_3d_to_2d

class Kerucut(BaseShape):
    """
    Implementasi Objek 3D Kerucut.
    Full Manual Bresenham 
    FITUR: Rotasi 3D + Proyeksi Perspektif + Wireframe Manual.
    """
    def __init__(self, x, y, z, color, radius=50, height=100):
        super().__init__(x, y, z, color)
        self.base_radius = radius
        self.base_height = height
        
        # Sudut rotasi (dalam radian)
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        
        # Warna outline
        self.outline_color = color

    def _apply_transforms(self, vx, vy, vz):
        """Transformasi 3D ke 2D menggunakan Math Utils."""
        
        # 1. Rotasi Matriks (Pitch, Yaw, Roll) dari math_utils
        rx, ry, rz = rotate_3d(vx, vy, vz, self.angle_x, self.angle_y, self.angle_z)

        # 2. Proyeksi Perspektif dari math_utils
        # rz ditambah self.z untuk memproses kedalaman/jarak objek
        px, py = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
        
        return px, py

    def draw(self, surface):
        """Render Kerucut menggunakan algoritma Bresenham manual."""
        current_r = self.base_radius * self.scale
        current_h = self.base_height * self.scale
        
        # Segmen lingkaran alas
        segments = 24 
        
        # 1. Hitung Titik Puncak (Apex)
        # Puncak berada di tengah atas (height/2)
        apex_2d = self._apply_transforms(0, current_h / 2, 0)
        
        # 2. Hitung Titik-titik Alas Lingkaran
        base_points = []
        for i in range(segments):
            theta = (2 * math.pi * i) / segments
            bx = current_r * math.cos(theta)
            bz = current_r * math.sin(theta)
            # Alas berada di posisi bawah (-height/2)
            base_points.append(self._apply_transforms(bx, -current_h / 2, bz))
            
        # 3. PROSES RENDERING (FULL MANUAL BRESENHAM)
        for i in range(segments):
            p1 = base_points[i]
            p2 = base_points[(i + 1) % segments]
            
            # --- Gambar Garis Lingkaran Alas ---
            ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, p1, p2)
            
            # --- Gambar Garis Selimut (Penghubung alas ke puncak) ---
            # Menggambar setiap 2 segmen agar wireframe terlihat elegan
            if i % 2 == 0: 
                ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, p1, apex_2d)

    def is_clicked(self, mouse_pos):
        """Deteksi klik sederhana berdasarkan area cakupan objek."""
        mx, my = mouse_pos
        bound = max(self.base_radius, self.base_height / 2) * self.scale
        return math.hypot(mx - self.x, my - self.y) <= bound

    def to_dict(self):
        """Data persistence untuk alur Save JSON."""
        data = super().to_dict()
        data.update({
            "radius": self.base_radius,
            "height": self.base_height,
            "angle_x": self.angle_x,
            "angle_y": self.angle_y,
            "angle_z": self.angle_z
        })
        return data
import pygame
import math
from core.base import BaseShape
from core.pattern import PatternGenerator, PatternStyle
from fitur.algoritma import ManualAlgorithms 
from core.math_utils import rotate_3d, project_3d_to_2d

class BelahKetupat(BaseShape):
    """
    Implementasi Objek 2D Belah Ketupat.
    Full Manual Bresenham untuk garis tepi + Math Utils untuk Z-Depth & Rotasi Z.
    """
    def __init__(self, x, y, z, color, width=100, height=150):
        super().__init__(x, y, z, color)
        # Dimensi diagonal dasar
        self.base_width = max(width, 1)
        self.base_height = max(height, 1)
        
        # Objek 2D murni HANYA punya rotasi Sumbu Z (Miring/Roll)
        self.angle_z = 0 
        
        # Pengaturan tampilan
        self.fill_type = PatternStyle.FILL_SOLID   # Jenis arsiran isi
        self.outline_color = (0, 0, 0)             # Warna garis tepi (Hitam)

    def draw(self, surface):
        """Render objek dengan kalkulasi titik dinamis, proyeksi 3D, dan algoritma manual."""
        current_w = self.base_width * self.scale
        current_h = self.base_height * self.scale
        
        if current_w <= 0 or current_h <= 0: return
        
        w = current_w / 2
        h = current_h / 2
        
        # 1. Tentukan titik lokal (mengelilingi pusat 0,0)
        local_points = [
            (0, -h, 0),  # Atas
            (w, 0, 0),   # Kanan
            (0, h, 0),   # Bawah
            (-w, 0, 0)   # Kiri
        ]
        
        projected_points = []
        for px, py, pz in local_points:
            px, py, pz = self.apply_mirroring(px, py, pz)
            # 2a. Rotasi Z saja (angle_x dan angle_y dikunci 0)
            rx, ry, rz = rotate_3d(px, py, pz, 0, 0, self.angle_z)
            # 2b. Proyeksi Perspektif (Ditambah self.z agar fitur </> berfungsi)
            fx, fy = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
            projected_points.append((fx, fy))
            
        # --- MENGHITUNG BOUNDING BOX DINAMIS (Agar arsiran dan seleksi tidak bocor/terpotong) ---
        min_x = min(p[0] for p in projected_points)
        max_x = max(p[0] for p in projected_points)
        min_y = min(p[1] for p in projected_points)
        max_y = max(p[1] for p in projected_points)
        
        surf_w = max_x - min_x
        surf_h = max_y - min_y

        # 3. PROSES FILLING (Pola Isi/Arsiran)
        if self.fill_type == PatternStyle.FILL_SOLID:
            pygame.draw.polygon(surface, self.color, projected_points)
        elif surf_w > 0 and surf_h > 0:
            # Sistem masking yang sudah di-upgrade agar mengikuti ukuran objek saat diputar
            temp_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            tile = PatternGenerator.create_fill_pattern(self.fill_type, self.outline_color)
            PatternGenerator.fill_surface_with_pattern(temp_surface, tile)
            
            mask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            # Menyesuaikan titik poligon relatif terhadap pojok kiri atas bounding box
            local_pts = [(p[0] - min_x, p[1] - min_y) for p in projected_points]
            pygame.draw.polygon(mask, (255, 255, 255, 255), local_pts)
            
            temp_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(temp_surface, (min_x, min_y))

        # 4. PROSES OUTLINE (FULL MANUAL BRESENHAM)
        for i in range(len(projected_points)):
            p1 = projected_points[i]
            p2 = projected_points[(i + 1) % len(projected_points)]
            ManualAlgorithms.draw_line_bresenham(surface, self.outline_color, p1, p2)

        # 5. Indikator Seleksi (Bounding Box)
        if self.is_selected:
            # Gunakan lebar dan tinggi dinamis (surf_w, surf_h) agar pas saat diputar
            self._draw_selection_style(surface, min_x, min_y, surf_w, surf_h)

    def _draw_selection_style(self, surface, min_x, min_y, w, h):
        """Visualisasi seleksi dinamis."""
        rect_x, rect_y = int(min_x), int(min_y)
        pygame.draw.rect(surface, (255, 0, 0), (rect_x, rect_y, int(w), int(h)), 1)
        # Handle kecil di pojok
        corners = [(rect_x, rect_y), (rect_x + w, rect_y), (rect_x, rect_y + h), (rect_x + w, rect_y + h)]
        for c in corners:
            pygame.draw.rect(surface, (0, 0, 255), (int(c[0]) - 3, int(c[1]) - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Deteksi klik dengan koreksi angle_z (inverse transform)."""
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
        # Rumus Belah Ketupat: (|lx|/a) + (|ly|/b) <= 1
        a = self.base_width * self.scale / 2
        b = self.base_height * self.scale / 2
        if a == 0 or b == 0:
            return False
        return (abs(local_x) / a + abs(local_y) / b) <= 1

    def to_dict(self):
        """Export data untuk sistem Save/Load JSON."""
        data = super().to_dict()
        data.update({
            "width": self.base_width,
            "height": self.base_height,
            "angle_z": self.angle_z,
            "fill_type": self.fill_type
        })
        return data
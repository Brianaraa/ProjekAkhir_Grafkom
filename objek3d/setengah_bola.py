import pygame
import math
from core.base import BaseShape

class SetengahBola(BaseShape):
    """
    Implementasi Objek 3D Setengah Bola - Dirancang oleh System Architect (B).
    Menggunakan proyeksi perspektif nyata berdasarkan koordinat Z.
    Terdiri dari Kubah (Arc) dan Alas (Elips).
    """
    def __init__(self, x, y, z, color, radius=50):
        # Meneruskan koordinat 3D ke BaseShape
        super().__init__(x, y, z, color)
        self.base_radius = max(radius, 1)

    def draw(self, surface):
        """Merender Kubah dan Alas dengan kalkulasi Perspektif Z."""
        # 1. Kalkulasi Proyeksi Perspektif (Betulan 3D)
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        
        proj_x = int(self.x)
        proj_y = int(self.y)
        proj_radius = int(self.base_radius * self.scale * factor)
        
        if proj_radius <= 0: return

        # Tinggi perspektif alas elips (30% dari radius hasil proyeksi)
        ellipse_h = proj_radius * 0.3
        
        # 2. Render Alas (Elips Bawah)
        rect_alas = pygame.Rect(
            int(proj_x - proj_radius), 
            int(proj_y - (ellipse_h / 2)), 
            int(proj_radius * 2), 
            int(ellipse_h)
        )
        pygame.draw.ellipse(surface, self.color, rect_alas, 2)

        # 3. Render Kubah (Arc Atas)
        # Bounding box untuk setengah lingkaran
        rect_kubah = pygame.Rect(
            int(proj_x - proj_radius), 
            int(proj_y - proj_radius), 
            int(proj_radius * 2), 
            int(proj_radius * 2)
        )
        pygame.draw.arc(surface, self.color, rect_kubah, 0, math.pi, 2)

        # 4. System Styling: Kotak Seleksi (Adobe-Style)
        # Digunakan sebagai indikator visual untuk fitur Coloring
        if self.is_selected:
            self._draw_selection_style(surface, proj_x, proj_y, proj_radius, ellipse_h)

    def _draw_selection_style(self, surface, px, py, r, eh):
        """Styling box seleksi yang presisi membungkus bentuk kubah."""
        rect_x = int(px - r)
        rect_y = int(py - r)
        rect_w = int(r * 2)
        rect_h = int(r + (eh / 2)) # Tinggi sampai batas bawah elips
        
        pygame.draw.rect(surface, (255, 0, 0), (rect_x, rect_y, rect_w, rect_h), 1)
        
        # Handle sudut (Styling Menengah-Tinggi)
        for hx, hy in [(rect_x, rect_y), (rect_x+rect_w, rect_y), 
                       (rect_x, rect_y+rect_h), (rect_x+rect_w, rect_y+rect_h)]:
            pygame.draw.rect(surface, (0, 0, 255), (hx - 3, hy - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Hit-Detection Hybrid: Mengecek area visual hasil proyeksi Z."""
        mx, my = mouse_pos
        
        # Hitung ukuran visual saat ini
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        r = self.base_radius * self.scale * factor
        eh = r * 0.3
        
        # Tahap 1: Cek area Kubah (Setengah Lingkaran Atas)
        dist = math.hypot(mx - self.x, my - self.y)
        if dist <= r and my <= self.y:
            return True
            
        # Tahap 2: Cek area Alas (Elips Bawah) menggunakan rumus elips baku
        dx = mx - self.x
        dy = my - self.y
        a, b = r, eh / 2
        if a > 0 and b > 0:
            if (dx**2 / a**2) + (dy**2 / b**2) <= 1:
                return True
                
        return False

    def to_dict(self):
        """Alur Data untuk Save: Mencatat X, Y, Z dan Radius."""
        data = super().to_dict()
        data["radius"] = self.base_radius
        return data
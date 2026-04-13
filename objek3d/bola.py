import pygame
import math
from core.base import BaseShape

class Bola(BaseShape):
    """
    Implementasi Objek 3D Bola - Dirancang oleh System Architect (B).
    Menerapkan Proyeksi Perspektif nyata berdasarkan koordinat Z.
    """
    def __init__(self, x, y, z, color, radius=50):
        # Mengirim koordinat 3D lengkap ke BaseShape
        super().__init__(x, y, z, color)
        self.base_radius = max(radius, 1)

    def draw(self, surface):
        """Merender Bola dengan perhitungan Perspektif Z."""
        # 1. Kalkulasi Perspektif (Betulan 3D)
        # Semakin besar Z (objek menjauh), objek akan terlihat semakin kecil
        # Rumus: fov / (fov + z)
        fov = 400 
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        
        # Koordinat proyeksi di layar
        proj_x = int(self.x)
        proj_y = int(self.y)
        proj_radius = int(self.base_radius * self.scale * factor)

        if proj_radius <= 0: return

        # 2. Render Wireframe 3D (Volume Representation)
        # Menggambar garis lintang dan bujur untuk menunjukkan volume bola
        
        # Siluet Luar
        pygame.draw.circle(surface, self.color, (proj_x, proj_y), proj_radius, 2)

        # Garis Lintang (Horizontal) - Perspektif Elips
        h_height = int(proj_radius * 0.5)
        rect_h = pygame.Rect(proj_x - proj_radius, proj_y - h_height//2, proj_radius * 2, h_height)
        pygame.draw.ellipse(surface, self.color, rect_h, 1)

        # Garis Bujur (Vertikal) - Perspektif Elips
        v_width = int(proj_radius * 0.5)
        rect_v = pygame.Rect(proj_x - v_width//2, proj_y - proj_radius, v_width, proj_radius * 2)
        pygame.draw.ellipse(surface, self.color, rect_v, 1)

        # 3. System Styling: Kotak Seleksi (Adobe-Style)
        if self.is_selected:
            self._draw_selection_style(surface, proj_x, proj_y, proj_radius)

    def _draw_selection_style(self, surface, px, py, r):
        """Styling indikator seleksi yang mengikuti hasil proyeksi 3D."""
        rect_x, rect_y = px - r, py - r
        size = r * 2
        pygame.draw.rect(surface, (255, 0, 0), (rect_x, rect_y, size, size), 1)
        
        # Titik kontrol di sudut
        for hx, hy in [(rect_x, rect_y), (rect_x+size, rect_y), 
                       (rect_x, rect_y+size), (rect_x+size, rect_y+size)]:
            pygame.draw.rect(surface, (0, 0, 255), (hx - 3, hy - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Hit-detection yang akurat terhadap hasil proyeksi di layar."""
        # Harus menghitung perspektif dulu agar area klik pas dengan visual
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        proj_radius = self.base_radius * self.scale * factor
        
        distance = math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        return distance <= proj_radius

    def to_dict(self):
        """Alur Data untuk Save: Mencatat koordinat 3D murni (X, Y, Z)."""
        data = super().to_dict()
        data["radius"] = self.base_radius
        return data
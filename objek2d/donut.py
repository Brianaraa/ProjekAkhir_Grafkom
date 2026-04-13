import pygame
import math
from core.base import BaseShape

class Donut(BaseShape):
    """
    Implementasi Objek 2D Donut - Dirancang oleh System Architect (B).
    Fokus pada alur data koordinat (X, Y, Z) dan fungsionalitas Coloring.
    """
    def __init__(self, x, y, z, color, outer_radius=60, inner_radius=30):
        # Meneruskan data ke BaseShape (termasuk sumbu Z)
        super().__init__(x, y, z, color)
        
        # Atribut Geometri
        self.base_outer_radius = max(outer_radius, 1)
        self.base_inner_radius = min(inner_radius, self.base_outer_radius - 1)

    def draw(self, surface):
        """Render donat dengan dukungan Scaling dan Styling Seleksi."""
        # 1. Kalkulasi Ukuran berdasarkan Scale
        current_outer = int(self.base_outer_radius * self.scale)
        current_inner = int(self.base_inner_radius * self.scale)
        
        if current_outer <= 0: return
        
        # 2. Render Body Donat (Logika Lubang Transparan)
        # Menggunakan ketebalan (thickness) agar tengahnya bolong murni
        thickness = max(1, current_outer - current_inner)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), current_outer, thickness)

        # 3. System Styling: Kotak Seleksi (Tugas B: Styling Menengah-Tinggi)
        # Muncul hanya jika objek dipilih untuk di-Coloring atau di-Save
        if self.is_selected:
            self._draw_selection_style(surface, current_outer)

    def _draw_selection_style(self, surface, radius):
        """Visualisasi seleksi profesional tanpa fitur Drag/Rotate."""
        rect_x = int(self.x - radius)
        rect_y = int(self.y - radius)
        size = int(radius * 2)
        
        # Garis pembatas tipis
        pygame.draw.rect(surface, (255, 0, 0), (rect_x, rect_y, size, size), 1)
        
        # Handle di pojok sebagai pemanis styling (non-fungsional sesuai permintaan)
        points = [(rect_x, rect_y), (rect_x + size, rect_y), 
                  (rect_x, rect_y + size), (rect_x + size, rect_y + size)]
        for p in points:
            pygame.draw.rect(surface, (0, 0, 255), (p[0] - 3, p[1] - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Logika deteksi klik untuk fitur Coloring."""
        mx, my = mouse_pos
        distance = math.hypot(mx - self.x, my - self.y)
        
        c_outer = self.base_outer_radius * self.scale
        c_inner = self.base_inner_radius * self.scale
        
        # Klik hanya terdeteksi jika mengenai 'daging' donat
        return c_inner <= distance <= c_outer

    def to_dict(self):
        """Alur Data untuk fungsionalitas Save (JSON)."""
        data = super().to_dict() # Mengambil X, Y, Z, Color, Scale
        data.update({
            "outer_radius": self.base_outer_radius,
            "inner_radius": self.base_inner_radius
        })
        return data
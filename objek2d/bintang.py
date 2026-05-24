import pygame
import math
from core.base import BaseShape

class Bintang(BaseShape):
    """
    Implementasi Objek 2D Bintang - Dirancang oleh Lead Developer (A).
    """
    def __init__(self, x, y, z, color, outer_radius=50, inner_radius=20):
        super().__init__(x, y, z, color)
        self.base_outer_radius = max(outer_radius, 1)
        self.base_inner_radius = max(inner_radius, 1)
    
    def draw(self, surface):
        current_outer = int(self.base_outer_radius * self.scale)
        current_inner = int(self.base_inner_radius * self.scale)
        
        if current_outer <= 0: return

        points = []
        for i in range(10):
            # Mulai dari atas: -90 derajat
            angle = math.radians(i * 36 - 90)
            r = current_outer if i % 2 == 0 else current_inner
            lx = r * math.cos(angle)
            ly = r * math.sin(angle)
            lx, ly, _ = self.apply_mirroring(lx, ly, 0)
            px = self.x + lx
            py = self.y + ly
            points.append((int(px), int(py)))

        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 1) # Outline warna hitam

        if self.is_selected:
            self._draw_selection_style(surface, current_outer)

    def _draw_selection_style(self, surface, radius):
        rect_x = int(self.x - radius)
        rect_y = int(self.y - radius)
        size = int(radius * 2)
        pygame.draw.rect(surface, (255, 0, 0), (rect_x, rect_y, size, size), 1)
        
        points = [(rect_x, rect_y), (rect_x + size, rect_y), 
                  (rect_x, rect_y + size), (rect_x + size, rect_y + size)]
        for p in points:
            pygame.draw.rect(surface, (0, 0, 255), (p[0] - 3, p[1] - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        mx, my = mouse_pos
        distance = math.hypot(mx - self.x, my - self.y)
        c_outer = self.base_outer_radius * self.scale
        return distance <= c_outer

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "outer_radius": self.base_outer_radius,
            "inner_radius": self.base_inner_radius
        })
        return data

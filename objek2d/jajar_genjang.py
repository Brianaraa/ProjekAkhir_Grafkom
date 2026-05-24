import pygame
import math
from core.base import BaseShape

class JajarGenjang(BaseShape):
    """
    Implementasi Objek 2D Jajar Genjang - Dirancang oleh Lead Developer (A).
    """
    def __init__(self, x, y, z, color, width=100, height=60, offset=30):
        super().__init__(x, y, z, color)
        self.base_width = width
        self.base_height = height
        self.base_offset = offset

    def draw(self, surface):
        current_w = int(self.base_width * self.scale)
        current_h = int(self.base_height * self.scale)
        current_off = int(self.base_offset * self.scale)
        
        if current_w <= 0 or current_h <= 0: return

        hw = current_w / 2
        hh = current_h / 2
        ho = current_off / 2

        local_pts = [
            (-hw + ho, -hh, 0),
            (hw + ho, -hh, 0),
            (hw - ho, hh, 0),
            (-hw - ho, hh, 0)
        ]
        points = []
        for lx, ly, lz in local_pts:
            lx, ly, _ = self.apply_mirroring(lx, ly, 0)
            points.append((self.x + lx, self.y + ly))

        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 1)

        if self.is_selected:
            rx = int(self.x - hw - abs(ho))
            ry = int(self.y - hh)
            rw = int(current_w + abs(current_off))
            rh = current_h
            
            pygame.draw.rect(surface, (255, 0, 0), (rx, ry, rw, rh), 1)
            ctrl_points = [(rx, ry), (rx + rw, ry), (rx, ry + rh), (rx + rw, ry + rh)]
            for p in ctrl_points:
                pygame.draw.rect(surface, (0, 0, 255), (p[0] - 3, p[1] - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        mx, my = mouse_pos
        current_w = self.base_width * self.scale
        current_h = self.base_height * self.scale
        current_off = self.base_offset * self.scale

        hw = current_w / 2
        hh = current_h / 2
        ho = current_off / 2

        # Menggunakan algoritma Point-in-Polygon (Ray Casting) dengan koordinat yang dicerminkan
        local_pts = [
            (-hw + ho, -hh, 0),
            (hw + ho, -hh, 0),
            (hw - ho, hh, 0),
            (-hw - ho, hh, 0)
        ]
        points = []
        for lx, ly, lz in local_pts:
            lx, ly, _ = self.apply_mirroring(lx, ly, 0)
            points.append((self.x + lx, self.y + ly))
        
        inside = False
        n = len(points)
        p1x, p1y = points[0]
        for i in range(1, n + 1):
            p2x, p2y = points[i % n]
            if my > min(p1y, p2y):
                if my <= max(p1y, p2y):
                    if mx <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (my - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or mx <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "width": self.base_width,
            "height": self.base_height,
            "offset": self.base_offset
        })
        return data

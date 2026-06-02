import pygame
import math
from core.base import BaseShape

class TextShape(BaseShape):
    """
    Implementasi Objek 2D Teks Dinamis.
    Mendukung rotasi Z, scaling, coloring, mirroring, skewing, serta save/load JSON.
    """
    def __init__(self, x, y, z, color, text="Teks Baru", size=30):
        super().__init__(x, y, z, color)
        self.text = text
        self.size = max(10, size)
        
        self.angle_z = 0
        self.font_name = "Segoe UI"
        self.last_rect = pygame.Rect(x, y, 0, 0)

    def _skew_surface(self, surface, skew_x, skew_y):
        """Skew (geser) Surface secara horizontal/vertikal."""
        if skew_x == 0 and skew_y == 0:
            return surface
        
        w, h = surface.get_size()
        # Hitung space tambahan agar tidak terpotong
        add_w = int(abs(skew_x) * h)
        add_h = int(abs(skew_y) * w)
        new_w = w + add_w
        new_h = h + add_h
        
        skewed_surf = pygame.Surface((new_w, new_h), pygame.SRCALPHA)
        
        for y in range(h):
            for x in range(w):
                # Geser x berdasarkan y, geser y berdasarkan x
                # Normalisasi offset agar gambar selalu berada di koordinat positif
                nx = x + skew_x * (h - y if skew_x >= 0 else -y)
                ny = y + skew_y * (x if skew_y >= 0 else x - w)
                
                offset_x = int(nx + (abs(skew_x) * h if skew_x < 0 else 0))
                offset_y = int(ny + (abs(skew_y) * w if skew_y < 0 else 0))
                
                if 0 <= offset_x < new_w and 0 <= offset_y < new_h:
                    skewed_surf.set_at((offset_x, offset_y), surface.get_at((x, y)))
        return skewed_surf

    def draw(self, surface):
        if not self.text:
            return

        font_size = max(6, int(self.size * self.scale))
        try:
            font = pygame.font.SysFont(self.font_name, font_size)
        except Exception:
            font = pygame.font.Font(None, font_size)

        # Render awal
        text_surf = font.render(self.text, True, self.color)
        
        # Mirroring
        if self.flip_x or self.flip_y:
            text_surf = pygame.transform.flip(text_surf, self.flip_x, self.flip_y)

        # Skewing
        if self.skew_x != 0 or self.skew_y != 0:
            text_surf = self._skew_surface(text_surf, self.skew_x, self.skew_y)

        # Rotasi
        if self.angle_z != 0:
            deg = math.degrees(-self.angle_z)
            text_surf = pygame.transform.rotate(text_surf, deg)

        # Draw to screen
        render_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, render_rect.topleft)
        self.last_rect = render_rect

        # Selection border
        if self.is_selected:
            self._draw_selection_style(surface, render_rect)

    def _draw_selection_style(self, surface, rect):
        rx, ry = rect.x - 2, rect.y - 2
        rw, rh = rect.width + 4, rect.height + 4
        pygame.draw.rect(surface, (59, 130, 246), (rx, ry, rw, rh), 2)
        corners = [(rx, ry), (rx + rw, ry), (rx, ry + rh), (rx + rw, ry + rh)]
        for c in corners:
            pygame.draw.rect(surface, (255, 255, 255), (c[0] - 3, c[1] - 3, 7, 7))
            pygame.draw.rect(surface, (59, 130, 246), (c[0] - 3, c[1] - 3, 7, 7), 1)

    def is_clicked(self, mouse_pos):
        inflated_rect = self.last_rect.inflate(10, 10)
        return inflated_rect.collidepoint(mouse_pos)

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "text": self.text,
            "size": self.size,
            "angle_z": self.angle_z,
            "font_name": self.font_name
        })
        return data

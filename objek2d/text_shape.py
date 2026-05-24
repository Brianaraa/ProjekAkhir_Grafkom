import pygame
import math
from core.base import BaseShape

class TextShape(BaseShape):
    """
    Implementasi Objek 2D Teks Dinamis.
    Mendukung rotasi Z, scaling, coloring, mirroring, serta save/load JSON.
    """
    def __init__(self, x, y, z, color, text="Teks Baru", size=30):
        super().__init__(x, y, z, color)
        self.text = text
        self.size = max(10, size)
        
        # Objek 2D murni HANYA punya rotasi Sumbu Z (Miring/Roll)
        self.angle_z = 0
        self.font_name = "Segoe UI"
        
        # Simpan rect rendering terakhir untuk deteksi klik (is_clicked)
        self.last_rect = pygame.Rect(x, y, 0, 0)

    def draw(self, surface):
        if not self.text:
            return

        # 1. Buat font sesuai skala dinamis
        font_size = max(6, int(self.size * self.scale))
        try:
            font = pygame.font.SysFont(self.font_name, font_size)
        except Exception:
            font = pygame.font.Font(None, font_size)

        # 2. Render teks awal
        # Gunakan anti-aliasing (True)
        text_surf = font.render(self.text, True, self.color)
        
        # 3. Terapkan Mirroring (Refleksi)
        if self.flip_x or self.flip_y:
            text_surf = pygame.transform.flip(text_surf, self.flip_x, self.flip_y)

        # 4. Terapkan Rotasi
        if self.angle_z != 0:
            # pygame.transform.rotate menerima derajat (berlawanan jarum jam)
            # Konversi angle_z (radian) ke derajat, berikan tanda minus untuk arah yang sesuai
            deg = math.degrees(-self.angle_z)
            text_surf = pygame.transform.rotate(text_surf, deg)

        # 5. Gambar ke layar utama
        # Titik (x, y) adalah pusat objek
        render_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, render_rect.topleft)
        
        # Simpan rect ini untuk deteksi is_clicked
        self.last_rect = render_rect

        # 6. Gambar kotak seleksi jika objek terpilih
        if self.is_selected:
            self._draw_selection_style(surface, render_rect)

    def _draw_selection_style(self, surface, rect):
        """Gambar bounding box seleksi di sekeliling teks."""
        pygame.draw.rect(surface, (255, 0, 0), rect, 1)
        # Handle kecil di pojok
        corners = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
        for c in corners:
            pygame.draw.rect(surface, (0, 0, 255), (c[0] - 3, c[1] - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        """Deteksi apakah posisi mouse mengeklik area teks."""
        # Menambahkan toleransi margin kecil di sekeliling teks agar mudah diklik
        inflated_rect = self.last_rect.inflate(10, 10)
        return inflated_rect.collidepoint(mouse_pos)

    def to_dict(self):
        """Alur Data untuk save JSON."""
        data = super().to_dict()
        data.update({
            "text": self.text,
            "size": self.size,
            "angle_z": self.angle_z,
            "font_name": self.font_name
        })
        return data

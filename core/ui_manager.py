import pygame
from core.constants import *

class UIManager:
    """
    Kelas untuk mengelola antarmuka pengguna (UI).
    Bertanggung jawab atas pembagian area layar, rendering menu, 
    dan konversi koordinat.
    """
    def __init__(self, screen):
        self.screen = screen
        
        # Inisialisasi area Rect untuk deteksi klik
        self.toolbar_rect = pygame.Rect(0, 0, TOOLBAR_WIDTH, WINDOW_HEIGHT)
        self.canvas_rect = pygame.Rect(TOOLBAR_WIDTH, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        self.status_rect = pygame.Rect(0, WINDOW_HEIGHT - STATUS_HEIGHT, WINDOW_WIDTH, STATUS_HEIGHT)
        
        # Font untuk UI (Gunakan font sistem yang umum)
        self.font = pygame.font.SysFont("Arial", 14)
        self.header_font = pygame.font.SysFont("Arial", 16, bold=True)

    def draw_layout(self):
        """Menggambar background area UI dasar."""
        # 1. Area Toolbar (Kiri)
        pygame.draw.rect(self.screen, COLOR_BG_UI, self.toolbar_rect)
        
        # 2. Area Canvas (Kanan)
        pygame.draw.rect(self.screen, COLOR_CANVAS, self.canvas_rect)
        
        # 3. Area Status Bar (Bawah)
        pygame.draw.rect(self.screen, COLOR_STATUS, self.status_rect)
        
        # 4. Garis Pembatas (Border)
        pygame.draw.line(self.screen, COLOR_BORDER, (TOOLBAR_WIDTH, 0), (TOOLBAR_WIDTH, WINDOW_HEIGHT), 2)
        pygame.draw.line(self.screen, COLOR_BORDER, (0, WINDOW_HEIGHT - STATUS_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT - STATUS_HEIGHT), 2)

    def draw_status_info(self, mouse_pos):
        """Menampilkan informasi koordinat di Status Bar (Fitur Nilai Tambah)."""
        if self.canvas_rect.collidepoint(mouse_pos):
            # Normalisasi: Mengubah koordinat layar menjadi koordinat lokal Canvas
            local_x = mouse_pos[0] - TOOLBAR_WIDTH
            local_y = mouse_pos[1]
            status_str = f"Canvas Position: {local_x}, {local_y} px"
        else:
            status_str = "Mouse outside canvas"
            
        text_surface = self.font.render(status_str, True, COLOR_TEXT)
        # Tempel teks di pojok kiri bawah (Status Bar)
        self.screen.blit(text_surface, (TOOLBAR_WIDTH + 10, WINDOW_HEIGHT - STATUS_HEIGHT + 7))

    def is_canvas_clicked(self, mouse_pos):
        """Mengecek apakah user mengklik di area gambar."""
        return self.canvas_rect.collidepoint(mouse_pos)

    def get_local_coords(self, mouse_pos):
        """Mengonversi koordinat global layar menjadi koordinat lokal canvas."""
        return (mouse_pos[0] - TOOLBAR_WIDTH, mouse_pos[1])
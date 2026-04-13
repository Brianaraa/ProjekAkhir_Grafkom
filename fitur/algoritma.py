import pygame
import math
from collections import deque

class ManualAlgorithms:
    """
    Kumpulan Algoritma Grafika Komputer - Dirancang oleh System Architect (B).
    Fokus pada efisiensi alur data koordinat dan manipulasi pixel manual.
    """

    # --- 1. LOGIKA PROYEKSI 3D (Tugas B: Betulan 3D) ---
    @staticmethod
    def project_3d_to_2d(x, y, z, win_width, win_height, fov=400):
        """
        Mengonversi koordinat 3D (x, y, z) menjadi koordinat 2D (x', y').
        Fungsi ini memastikan objek memiliki perspektif: makin jauh Z, makin kecil.
        """
        # Weak Perspective Projection
        # Rumus: x' = x * (fov / (fov + z))
        factor = fov / (fov + z) if (fov + z) != 0 else 1
        
        projected_x = x * factor
        projected_y = y * factor
        
        return int(projected_x), int(projected_y), factor

    # --- 2. ALGORITMA PEMBENTUKAN GARIS (Bresenham) ---
    @staticmethod
    def draw_line_bresenham(surface, color, start_pos, end_pos):
        """
        Implementasi manual pembentukan garis sesuai Modul Perkuliahan.
        Hanya menggunakan operasi integer untuk performa maksimal.
        """
        x1, y1 = int(start_pos[0]), int(start_pos[1])
        x2, y2 = int(end_pos[0]), int(end_pos[1])

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            # Set_at adalah metode manipulasi pixel langsung
            if 0 <= x1 < surface.get_width() and 0 <= y1 < surface.get_height():
                surface.set_at((x1, y1), color)

            if x1 == x2 and y1 == y2: break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    # --- 3. FITUR FILL AREA (Queue-based Flood Fill) ---
    @staticmethod
    def flood_fill(surface, start_pos, fill_color):
        """
        Implementasi Fill Area (Tugas B).
        Menggunakan struktur data Queue untuk menghindari stack overflow pada area luas.
        """
        x, y = int(start_pos[0]), int(start_pos[1])
        width, height = surface.get_size()

        if x < 0 or y < 0 or x >= width or y >= height: return

        # Mengambil warna target (warna yang akan diganti)
        target_color = surface.get_at((x, y))
        if target_color == fill_color: return

        # Menggunakan PixelArray untuk akses memori langsung (High Speed)
        pixels = pygame.PixelArray(surface)
        
        # Mapping warna ke format integer Pygame
        fill_rgb = surface.map_rgb(fill_color)
        target_rgb = surface.map_rgb(target_color)

        queue = deque([(x, y)])
        while queue:
            curr_x, curr_y = queue.popleft()

            if pixels[curr_x, curr_y] == target_rgb:
                pixels[curr_x, curr_y] = fill_rgb
                
                # Cek 4 tetangga (Kanan, Kiri, Bawah, Atas)
                if curr_x + 1 < width: queue.append((curr_x + 1, curr_y))
                if curr_x - 1 >= 0: queue.append((curr_x - 1, curr_y))
                if curr_y + 1 < height: queue.append((curr_x, curr_y + 1))
                if curr_y - 1 >= 0: queue.append((curr_x, curr_y - 1))

        pixels.close() # Penting: Selalu tutup PixelArray setelah digunakan
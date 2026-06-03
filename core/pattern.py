import pygame
import math

class PatternStyle:
    """
    Konstanta untuk jenis-jenis pola garis dan isian (Atribut Output Primitif).
    """
    # Tipe Garis (Line Styles)
    LINE_SOLID = 0
    LINE_DASHED = 1
    LINE_DOTTED = 2

    # Tipe Isian (Fill Patterns)
    FILL_SOLID = 10
    FILL_HATCH_DIAGONAL = 11
    FILL_HATCH_CROSS = 12
    FILL_DOTS = 13
    FILL_HOLLOW = 14 # Tanpa Isian (Transparan)


class PatternGenerator:
    """
    Kelas utilitas (Static Class) untuk menghasilkan atribut pola gambar.
    A dan AY akan memanggil fungsi di kelas ini jika objek mereka ingin
    memiliki garis putus-putus atau arsiran.
    """

    @staticmethod
    def draw_styled_line(surface, color, start_pos, end_pos, width=1, style=PatternStyle.LINE_SOLID):
        """
        Fungsi canggih untuk menggambar garis dengan berbagai gaya (Solid, Dashed, Dotted).
        Mengimplementasikan vektor matematika untuk menghitung jarak spasi putus-putus.
        """
        if style == PatternStyle.LINE_SOLID:
            pygame.draw.line(surface, color, start_pos, end_pos, width)
            return

        # Logika untuk garis putus-putus (Dashed) atau titik-titik (Dotted)
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Hitung panjang total garis menggunakan Pythagoras
        panjang_garis = math.hypot(x2 - x1, y2 - y1)
        if panjang_garis == 0:
            return

        # Tentukan panjang coretan dan spasi berdasarkan style
        if style == PatternStyle.LINE_DASHED:
            dash_length = 10  # Panjang 1 coretan
            space_length = 5  # Jarak antar coretan
        elif style == PatternStyle.LINE_DOTTED:
            dash_length = 2
            space_length = 6

        # Normalisasi vektor arah (Direction Vector)
        dx = (x2 - x1) / panjang_garis
        dy = (y2 - y1) / panjang_garis

        jarak_tempuh = 0
        is_drawing = True # Flag penanda sedang menggores atau spasi kosong

        while jarak_tempuh < panjang_garis:
            sisa_panjang = panjang_garis - jarak_tempuh
            step = dash_length if is_drawing else space_length
            
            # Jangan sampai goresan melebihi titik akhir
            step = min(step, sisa_panjang)

            # Titik awal segmen
            seg_x1 = x1 + (dx * jarak_tempuh)
            seg_y1 = y1 + (dy * jarak_tempuh)
            
            # Titik akhir segmen
            seg_x2 = x1 + (dx * (jarak_tempuh + step))
            seg_y2 = y1 + (dy * (jarak_tempuh + step))

            if is_drawing:
                pygame.draw.line(surface, color, (seg_x1, seg_y1), (seg_x2, seg_y2), width)

            jarak_tempuh += step
            is_drawing = not is_drawing # Tukar status (gores -> spasi -> gores)

    @staticmethod
    def create_fill_pattern(pattern_type, fg_color, bg_color=None, size=10):
        """
        Fungsi untuk membuat 'ubin' (tile) berukuran kecil (misal 10x10 px) yang berisi pola.
        Ubin ini nantinya diulang-ulang (tiling) untuk mengisi area poligon yang luas.
        """
        # Buat surface transparan kecil
        pattern_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if bg_color:
            pattern_surface.fill(bg_color)

        if pattern_type == PatternStyle.FILL_HATCH_DIAGONAL:
            # Menggambar garis miring dari kiri bawah ke kanan atas
            pygame.draw.line(pattern_surface, fg_color, (0, size), (size, 0), 1)
            
        elif pattern_type == PatternStyle.FILL_HATCH_CROSS:
            # Menggambar garis miring silang (X)
            pygame.draw.line(pattern_surface, fg_color, (0, size), (size, 0), 1)
            pygame.draw.line(pattern_surface, fg_color, (0, 0), (size, size), 1)
            
        elif pattern_type == PatternStyle.FILL_DOTS:
            # Menggambar polkadot (titik di tengah)
            center = size // 2
            pygame.draw.circle(pattern_surface, fg_color, (center, center), max(1, size//4))
            
        elif pattern_type == PatternStyle.FILL_HOLLOW:
            # Tidak diisi apa-apa (Transparan total)
            pattern_surface.fill((0, 0, 0, 0))
            
        else:
            # Default FILL_SOLID
            pattern_surface.fill(fg_color)

        return pattern_surface

    @staticmethod
    def fill_surface_with_pattern(target_surface, pattern_surface):
        """
        Fungsi utilitas untuk menempelkan pola berulang-ulang ke seluruh area target.
        (Mirip konsep kerja lantai keramik).
        """
        t_width, t_height = target_surface.get_size()
        p_width, p_height = pattern_surface.get_size()

        for x in range(0, t_width, p_width):
            for y in range(0, t_height, p_height):
                target_surface.blit(pattern_surface, (x, y))
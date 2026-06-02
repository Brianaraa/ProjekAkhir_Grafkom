import pygame
from fitur.save_load import SaveLoadManager
from fitur.algoritma import ManualAlgorithms
from core.pattern import PatternStyle

# Import objek 
from objek2d.donut import Donut
from objek2d.belah_ketupat import BelahKetupat
from objek2d.setengah_lingkaran import SetengahLingkaran
from objek3d.bola import Bola
from objek3d.setengah_bola import SetengahBola
from objek3d.tabung import Tabung
from objek3d.kerucut import Kerucut

# Import objek A (Lead Developer)
from objek2d.bintang import Bintang
from objek2d.jajar_genjang import JajarGenjang
from objek3d.balok import Balok
from objek2d.text_shape import TextShape

class InputHandler:
    """
    Sistem Pengelola Input Keyboard dan Mouse.
    Kini menjadi Central Controller untuk Sistem  dan Transformasi.
    """
    is_dragging = False
    last_mouse_pos = (0, 0)
    
    @staticmethod
    def handle_event(event, mouse_pos, screen, ui, shapes, history, 
                     current_tool, selected_shape, palette, color_idx, current_color, bg_surface=None):
        
        # ==========================================
        # A. LOGIKA KEYBOARD
        # ==========================================
        if event.type == pygame.KEYDOWN:
            
            # --- 1. GLOBAL SYSTEM (Bisa dilakukan walau tidak ada objek terpilih) ---
            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                if event.key == pygame.K_z: 
                    shapes[:] = history.undo(shapes)
                    selected_shape = None
                elif event.key == pygame.K_y: 
                    shapes[:] = history.redo(shapes)
                    selected_shape = None
                elif event.key == pygame.K_s: 
                    SaveLoadManager.save_project(shapes)
                elif event.key == pygame.K_o: 
                    loaded = SaveLoadManager.load_project()
                    if loaded:
                        shapes[:] = loaded
                        history.clear_history()
                        history.save_state(shapes)
                        selected_shape = None

            # Tool Switcher (Ganti Alat Gambar)
            elif event.key == pygame.K_1: current_tool = "SELECT"
            elif event.key == pygame.K_2: current_tool = "DONUT"
            elif event.key == pygame.K_3: current_tool = "BOLA"
            elif event.key == pygame.K_4: current_tool = "SETENGAH_BOLA"
            elif event.key == pygame.K_5: current_tool = "BELAH_KETUPAT"
            elif event.key == pygame.K_6: current_tool = "SETENGAH_LINGKARAN"
            elif event.key == pygame.K_7: current_tool = "TABUNG"
            elif event.key == pygame.K_8: current_tool = "KERUCUT"
            elif event.key == pygame.K_9: current_tool = "FILL"# Fitur Fill Area
            
            # Tool Switcher (Objek A - Lead Developer)
            elif event.key == pygame.K_F1: current_tool = "BINTANG"
            elif event.key == pygame.K_F2: current_tool = "JAJAR_GENJANG"
            elif event.key == pygame.K_F3: current_tool = "BALOK"
            elif event.key == pygame.K_F4: current_tool = "TEXT"

            # --- 2. OBJECT MANIPULATION (HANYA jalan jika ada objek terpilih) ---
            elif selected_shape:
                # Flag pintar agar setiap pergerakan/skala dicatat di history (Undo/Redo)
                state_changed = False 
                
                # Fitur Coloring (Tekan 'C' untuk ganti warna aktif/objek terpilih)
                if event.key == pygame.K_c:
                    color_idx = (color_idx + 1) % len(palette)
                    current_color = palette[color_idx]
                    selected_shape.set_color(current_color)
                    state_changed = True

                # Fitur Mirroring (M/N)
                elif event.key == pygame.K_m:
                    selected_shape.flip_x = not selected_shape.flip_x
                    state_changed = True
                elif event.key == pygame.K_n:
                    selected_shape.flip_y = not selected_shape.flip_y
                    state_changed = True

                # Fitur Scaling (Ubah Ukuran Fisik) 
                # + / = : Perbesar Objek (Scaling Up) Memperbesar objek sebesar 10% (0.1)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    selected_shape.scale += 0.1
                    state_changed = True
                # - : Perkecil Objek (Scaling Down) (Dibatasi minimal skala 0.2 agar objek tidak hilang atau terbalik)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    selected_shape.scale = max(0.2, selected_shape.scale - 0.1)
                    state_changed = True

                # Fitur Z-Depth (Efek Zoom Jarak Kamera) ---
                # > : Geser Menjauh(Z+) (Mundur ke dalam layar)
                elif event.key == pygame.K_PERIOD: 
                    selected_shape.translate(0, 0, 10)
                    state_changed = True
                # <  : Geser Mendekat (Z-) (Maju ke arah user)
                elif event.key == pygame.K_COMMA:  
                    selected_shape.translate(0, 0, -10)
                    state_changed = True

                # Fitur Rotasi 3D (WASDQE) 
                elif event.key in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_q, pygame.K_e):
                    # Hanya putar jika objeknya 3D (punya atribut sudut)
                    if hasattr(selected_shape, 'angle_x'):
                        step = 0.1 

                        # W / S : Rotasi Sumbu X (Putar Atas/Bawah)
                        if event.key == pygame.K_w: selected_shape.angle_x += step
                        elif event.key == pygame.K_s: selected_shape.angle_x -= step

                        # A / D : Rotasi Sumbu Y (Putar Kiri/Kanan)
                        elif event.key == pygame.K_a: selected_shape.angle_y -= step
                        elif event.key == pygame.K_d: selected_shape.angle_y += step

                        # Q / E : Rotasi Sumbu Z (Miring Kiri/Kanan)
                        elif event.key == pygame.K_q: selected_shape.angle_z -= step
                        elif event.key == pygame.K_e: selected_shape.angle_z += step

                        state_changed = True

                # Fitur Pattern/Arsiran (P)
                elif event.key == pygame.K_p:
                    if hasattr(selected_shape, 'fill_type'):
                        # Cycle through 10, 11, 12, 13
                        patterns = [PatternStyle.FILL_SOLID, PatternStyle.FILL_HATCH_DIAGONAL, PatternStyle.FILL_HATCH_CROSS, PatternStyle.FILL_DOTS]
                        try:
                            idx = patterns.index(selected_shape.fill_type)
                        except ValueError:
                            idx = 0
                        selected_shape.fill_type = patterns[(idx + 1) % len(patterns)]
                        state_changed = True

                # Fitur Hapus Objek (Delete)
                elif event.key == pygame.K_DELETE:
                    shapes.remove(selected_shape)
                    selected_shape = None
                    state_changed = True
                    
                # Jika ada perubahan (Rotasi, Skala, Warna, dsb), rekam ke Stack Undo
                if state_changed:
                    history.save_state(shapes)

        # ==========================================
        # B. LOGIKA MOUSE
        # ==========================================
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and ui.is_canvas_clicked(mouse_pos):
                
                # Fitur: Fill Area (Flood Fill Manual)
                if current_tool == "FILL" and bg_surface is not None:
                    ManualAlgorithms.flood_fill(bg_surface, mouse_pos, current_color)
                    # Karena bg_surface bukan bagian dari shapes, idealnya kita tidak perlu 
                    # history.save_state(shapes) untuk flood_fill (kecuali kita juga membackup bg_surface).
                    # Untuk tugas ini, bg_surface berdiri terpisah dari undo stack.

                # Fitur: Seleksi (Styling untuk Coloring)    
                elif current_tool == "SELECT":
                    selected_shape = None
                    for s in reversed(shapes):
                        s.is_selected = False
                        if not selected_shape and s.is_clicked(mouse_pos):
                            s.is_selected = True
                            selected_shape = s
                    
                    if selected_shape:
                        InputHandler.is_dragging = True
                        InputHandler.last_mouse_pos = mouse_pos
                            
                # Fitur Penambahan Objek
                else:
                    new_obj = None
                    x, y, z = mouse_pos[0], mouse_pos[1], 0
                    
                    if current_tool == "DONUT": new_obj = Donut(x, y, z, current_color)
                    elif current_tool == "BOLA": new_obj = Bola(x, y, z, current_color)
                    elif current_tool == "SETENGAH_BOLA": new_obj = SetengahBola(x, y, z, current_color)
                    elif current_tool == "BELAH_KETUPAT": new_obj = BelahKetupat(x, y, z, current_color)
                    elif current_tool == "SETENGAH_LINGKARAN": new_obj = SetengahLingkaran(x, y, z, current_color)
                    elif current_tool == "TABUNG": new_obj = Tabung(x, y, z, current_color)
                    elif current_tool == "KERUCUT": new_obj = Kerucut(x, y, z, current_color)
                    elif current_tool == "BINTANG": new_obj = Bintang(x, y, z, current_color)
                    elif current_tool == "JAJAR_GENJANG": new_obj = JajarGenjang(x, y, z, current_color)
                    elif current_tool == "BALOK": new_obj = Balok(x, y, z, current_color)
                    elif current_tool == "TEXT": new_obj = TextShape(x, y, z, current_color)
                    
                    if new_obj:
                        shapes.append(new_obj)
                        history.save_state(shapes)

        # Fitur Translasi / Rotasi / Skala Drag & Drop (Logika Mouse Motion)
        elif event.type == pygame.MOUSEMOTION:
            if InputHandler.is_dragging and selected_shape and current_tool == "SELECT":
                dx = mouse_pos[0] - InputHandler.last_mouse_pos[0]
                dy = mouse_pos[1] - InputHandler.last_mouse_pos[1]
                
                if ui.ctrl_mode == "TRANSLASI":
                    selected_shape.translate(dx, dy, 0)
                elif ui.ctrl_mode == "ROTASI":
                    # Putar objek sesuai gerakan mouse
                    if hasattr(selected_shape, "angle_x"):
                        selected_shape.angle_x += dy * 0.01
                        selected_shape.angle_y += dx * 0.01
                    elif hasattr(selected_shape, "angle_z"):
                        selected_shape.angle_z += dx * 0.01
                elif ui.ctrl_mode == "SKALA":
                    # Skala objek sesuai gerakan vertikal mouse
                    selected_shape.scale = max(0.2, round(selected_shape.scale - dy * 0.01, 2))
                
                InputHandler.last_mouse_pos = mouse_pos

        # Fitur Translasi Drag & Drop (Logika Mouse Release)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and InputHandler.is_dragging:
                InputHandler.is_dragging = False
                history.save_state(shapes) # Simpan posisi terakhir setelah drag dilepas

        # Kembalikan semua nilai string/integer yang mungkin berubah
        return current_tool, selected_shape, color_idx, current_color
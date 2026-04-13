import pygame
import sys

# --- Import Core & Fitur (Tugas Utama B: Logic & Persistensi) ---
from core.ui_manager import UIManager
from fitur.undo_redo import UndoRedoManager
from fitur.save_load import SaveLoadManager
from fitur.algoritma import ManualAlgorithms

# --- Import Objek Jatah B ---
from objek2d.donut import Donut
from objek3d.bola import Bola
from objek3d.setengah_bola import SetengahBola

# --- REGISTRY: Alur data untuk fungsionalitas Save/Load ---
SaveLoadManager.register_shape("Donut", Donut)
SaveLoadManager.register_shape("Bola", Bola)
SaveLoadManager.register_shape("SetengahBola", SetengahBola)

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("PyPaint - System Architect (B) Edition")

    ui = UIManager(screen)
    history = UndoRedoManager(max_history=30)
    
    # State Variabel (Fokus pada Alur Data)
    shapes = []
    current_tool = "SELECT"
    
    # Fitur Coloring: Palet warna sederhana untuk alur data warna
    palette = [(41, 128, 185), (231, 76, 60), (46, 204, 113), (241, 196, 15), (0, 0, 0)]
    color_idx = 0
    current_color = palette[color_idx]
    
    selected_shape = None
    history.save_state(shapes) # Initial state untuk Stack Undo
    
    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # === A. SYSTEM LOGIC: KEYBOARD (Shortcut & Tools) ===
            elif event.type == pygame.KEYDOWN:
                # 1. Fungsionalitas Save & Load (Ctrl+S / Ctrl+O)
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if event.key == pygame.K_z: 
                        shapes = history.undo(shapes)
                        selected_shape = None
                    elif event.key == pygame.K_y: 
                        shapes = history.redo(shapes)
                        selected_shape = None
                    elif event.key == pygame.K_s: 
                        SaveLoadManager.save_project(shapes)
                    elif event.key == pygame.K_o: 
                        loaded = SaveLoadManager.load_project()
                        if loaded:
                            shapes = loaded
                            history.clear_history()
                            history.save_state(shapes)
                            selected_shape = None

                # 2. Fitur Coloring (Tekan 'C' untuk ganti warna aktif/objek terpilih)
                elif event.key == pygame.K_c:
                    color_idx = (color_idx + 1) % len(palette)
                    current_color = palette[color_idx]
                    if selected_shape:
                        selected_shape.set_color(current_color)
                        history.save_state(shapes)

                # 3. Fitur Z-Depth (Gerakkan objek di sumbu Z: Betulan 3D)
                elif selected_shape:
                    if event.key == pygame.K_PERIOD: # Tombol '>' geser menjauh (Z+)
                        selected_shape.translate(0, 0, 10)
                        history.save_state(shapes)
                    elif event.key == pygame.K_COMMA: # Tombol '<' geser mendekat (Z-)
                        selected_shape.translate(0, 0, -10)
                        history.save_state(shapes)
                    elif event.key == pygame.K_DELETE:
                        shapes.remove(selected_shape)
                        selected_shape = None
                        history.save_state(shapes)

                # Tool Switcher
                elif event.key == pygame.K_1: current_tool = "SELECT"
                elif event.key == pygame.K_2: current_tool = "DONUT"
                elif event.key == pygame.K_3: current_tool = "BOLA"
                elif event.key == pygame.K_4: current_tool = "SETENGAH_BOLA"
                elif event.key == pygame.K_5: current_tool = "FILL" # Fitur Fill Area

            # === B. SYSTEM LOGIC: MOUSE (Interaction) ===
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and ui.is_canvas_clicked(mouse_pos):
                    
                    # Fitur: Fill Area (Flood Fill Manual)
                    if current_tool == "FILL":
                        ManualAlgorithms.flood_fill(screen, mouse_pos, current_color)
                        # Flood fill memanipulasi pixel langsung, rekam ke stack
                        history.save_state(shapes)
                    
                    # Fitur: Seleksi (Styling untuk Coloring)
                    elif current_tool == "SELECT":
                        selected_shape = None
                        for s in reversed(shapes):
                            s.is_selected = False
                            if not selected_shape and s.is_clicked(mouse_pos):
                                s.is_selected = True
                                selected_shape = s
                    
                    # Fitur: Penambahan Objek (Koordinat X, Y, Z=0)
                    elif current_tool in ["DONUT", "BOLA", "SETENGAH_BOLA"]:
                        new_obj = None
                        if current_tool == "DONUT":
                            new_obj = Donut(mouse_pos[0], mouse_pos[1], 0, current_color)
                        elif current_tool == "BOLA":
                            new_obj = Bola(mouse_pos[0], mouse_pos[1], 0, current_color)
                        elif current_tool == "SETENGAH_BOLA":
                            new_obj = SetengahBola(mouse_pos[0], mouse_pos[1], 0, current_color)
                        
                        if new_obj:
                            shapes.append(new_obj)
                            history.save_state(shapes)

        # --- C. RENDERING (Output Visual) ---
        screen.fill((240, 240, 240))
        ui.draw_layout()
        
        # Area Clip Canvas
        screen.set_clip(ui.canvas_rect)
        for shape in shapes:
            shape.draw(screen)
        screen.set_clip(None)
        
        # Render UI Text & Instructions
        title = ui.header_font.render("SYSTEM ARCHITECT PANEL", True, (0, 0, 0))
        screen.blit(title, (20, 20))
        
        instructions = [
            f"Active Tool: {current_tool}",
            f"Active Color: {current_color}",
            "",
            "[1] Select Mode",
            "[2] Donut 2D",
            "[3] Bola 3D",
            "[4] Hemisphere 3D",
            "[5] Fill Area (Manual)",
            "",
            "Logic Controls:",
            "- C: Cycle Color (Coloring)",
            "- </>: Move Z-Axis (Betulan 3D)",
            "- Del: Remove Object",
            "",
            "Data Persistence:",
            "- Ctrl+Z/Y: Undo/Redo",
            "- Ctrl+S/O: Save/Load JSON"
        ]
        
        for i, text in enumerate(instructions):
            surf = ui.font.render(text, True, (50, 50, 50))
            screen.blit(surf, (20, 60 + (i * 22)))

        ui.draw_status_info(mouse_pos)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
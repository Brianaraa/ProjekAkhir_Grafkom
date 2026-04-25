import pygame
import sys

# --- Import Core & Fitur  ---
from core.ui_manager import UIManager
from fitur.undo_redo import UndoRedoManager
from fitur.save_load import SaveLoadManager
from fitur.algoritma import ManualAlgorithms
from core.input_handler import InputHandler 

# --- Import Objek ---
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

# --- REGISTRY: Alur data untuk fungsionalitas Save/Load ---
SaveLoadManager.register_shape("Donut", Donut)
SaveLoadManager.register_shape("Bola", Bola)
SaveLoadManager.register_shape("SetengahBola", SetengahBola)
SaveLoadManager.register_shape("BelahKetupat", BelahKetupat)
SaveLoadManager.register_shape("SetengahLingkaran", SetengahLingkaran)
SaveLoadManager.register_shape("Kerucut", Kerucut)
SaveLoadManager.register_shape("Tabung", Tabung)
SaveLoadManager.register_shape("Bintang", Bintang)
SaveLoadManager.register_shape("JajarGenjang", JajarGenjang)
SaveLoadManager.register_shape("Balok", Balok)

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("PyPaint - System Architect & Lead Developer Edition")

    ui = UIManager(screen)
    history = UndoRedoManager(max_history=30)
    
    # State Variabel (Fokus pada Alur Data)
    shapes = []
    current_tool = "SELECT"
    
    # Kanvas persistent untuk fitur Flood Fill
    bg_surface = pygame.Surface((1000, 700))
    bg_surface.fill((240, 240, 240))
    
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
                
            #  Panggil Input Handler untuk menyambungkan semua klik dan keyboard ke file input_handler.py
            current_tool, selected_shape, color_idx, current_color = InputHandler.handle_event(
                event, mouse_pos, screen, ui, shapes, history, 
                current_tool, selected_shape, palette, color_idx, current_color, bg_surface
            )

        # --- C. RENDERING (Output Visual) ---
        screen.blit(bg_surface, (0, 0))
        ui.draw_layout()
        
        # Area Clip Canvas
        screen.set_clip(ui.canvas_rect)
        for shape in shapes:
            shape.draw(screen)
        screen.set_clip(None)
        
        # Render UI Text & Instructions
        title = ui.header_font.render("LEAD DEVELOPER PANEL", True, (0, 0, 0))
        screen.blit(title, (20, 20))
        
        instructions = [
            f"Active Tool: {current_tool}",
            f"Active Color: {current_color}",
            "",
            "[1] Select Mode",
            "[2] Donut 2D | [F1] Bintang",
            "[3] Bola 3D | [F2] Jajar Genjang",
            "[4] Hemisphere 3D | [F3] Balok",
            "[5] Belah Ketupat",
            "[6] Semicircle",
            "[7] Tabung 3D",
            "[8] Kerucut 3D",
            "[9] Fill Area (Manual)",
            "",
            "Logic & Transform:",
            "- Drag/Drop: Translasi X/Y",
            "- C: Cycle Color",
            "- +/-: Scaling Objek",
            "- </>: Move Z-Axis",
            "- WASDQE: Rotasi 3D",
            "- Del: Remove Object",
            "",
            "Data Persistence:",
            "- Ctrl+Z/Y: Undo/Redo",
            "- Ctrl+S/O: Save/Load"
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
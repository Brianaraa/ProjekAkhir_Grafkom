import pygame
import sys

# --- Import Core & Fitur ---
from core.constants import *
from core.ui_manager import UIManager, PALETTE
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
from objek2d.bintang import Bintang
from objek2d.jajar_genjang import JajarGenjang
from objek3d.balok import Balok

# --- Registry Save/Load ---
SaveLoadManager.register_shape("Donut",             Donut)
SaveLoadManager.register_shape("Bola",              Bola)
SaveLoadManager.register_shape("SetengahBola",      SetengahBola)
SaveLoadManager.register_shape("BelahKetupat",      BelahKetupat)
SaveLoadManager.register_shape("SetengahLingkaran", SetengahLingkaran)
SaveLoadManager.register_shape("Kerucut",           Kerucut)
SaveLoadManager.register_shape("Tabung",            Tabung)
SaveLoadManager.register_shape("Bintang",           Bintang)
SaveLoadManager.register_shape("JajarGenjang",      JajarGenjang)
SaveLoadManager.register_shape("Balok",             Balok)

# Map nama tool → kelas objek
TOOL_CLASS_MAP = {
    "DONUT":             Donut,
    "BOLA":              Bola,
    "SETENGAH_BOLA":     SetengahBola,
    "BELAH_KETUPAT":     BelahKetupat,
    "SETENGAH_LINGKARAN":SetengahLingkaran,
    "TABUNG":            Tabung,
    "KERUCUT":           Kerucut,
    "BINTANG":           Bintang,
    "JAJAR_GENJANG":     JajarGenjang,
    "BALOK":             Balok,
}


def main():
    pygame.init()
    screen  = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PyPaint — Grafika 2D 3D")

    ui       = UIManager(screen)
    history  = UndoRedoManager(max_history=30)

    shapes         = []
    current_tool   = "SELECT"
    selected_shape = None
    palette        = PALETTE[:]
    color_idx      = 0
    current_color  = palette[color_idx]

    # Canvas persistent (flood fill background)
    bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    bg_surface.fill(C_CANVAS_BG)

    history.save_state(shapes)
    clock   = pygame.time.Clock()
    running = True

    while running:
        dt         = clock.tick(60)
        mouse_pos  = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ── 1. UI Panel events (tombol-tombol di panel) ──
            ui_actions = ui.handle_ui_event(
                event, mouse_pos, shapes, selected_shape, current_tool
            )

            for act in ui_actions:
                a = act["action"]

                if a == "SET_TOOL":
                    current_tool = act["value"]
                    # Update active state tombol Select/Fill
                    ui.btn_select.active = (current_tool == "SELECT")
                    ui.btn_fill.active   = (current_tool == "FILL")
                    for btn, tk in ui.shape_buttons:
                        btn.active = (tk == current_tool)

                elif a == "SET_COLOR_IDX":
                    color_idx     = act["value"]
                    current_color = palette[color_idx]
                    ui.color_idx  = color_idx

                elif a == "APPLY_SIZE":
                    if selected_shape:
                        ui.apply_size_to_shape(selected_shape, act["w"], act["h"], act["d"])
                        history.save_state(shapes)

                elif a == "RESET":
                    shapes.clear()
                    selected_shape = None
                    bg_surface.fill(C_CANVAS_BG)
                    history.clear_history()
                    history.save_state(shapes)

                elif a == "HAPUS":
                    if selected_shape and selected_shape in shapes:
                        shapes.remove(selected_shape)
                        selected_shape = None
                        history.save_state(shapes)

                elif a == "STATE_CHANGED":
                    history.save_state(shapes)

            # ── 2. Input Handler (keyboard + canvas mouse) ──
            current_tool, selected_shape, color_idx, current_color = InputHandler.handle_event(
                event, mouse_pos, screen, ui, shapes, history,
                current_tool, selected_shape, palette, color_idx, current_color, bg_surface
            )

            # Sinkron color_idx ke UI panel
            ui.color_idx = color_idx

            # Sinkron input ukuran jika objek terpilih berubah
            if selected_shape:
                ui.update_inputs_from_shape(selected_shape)

        # ── 3. Tick update (cursor blink TextInput) ──
        ui.update(dt)

        # ══════════════════════════════════════════════════
        # RENDERING
        # ══════════════════════════════════════════════════

        # 1. Latar belakang
        screen.blit(bg_surface, (0, 0))

        # 2. UI layout (navbar + panel + canvas)
        ui.draw_layout()

        # 3. Gambar objek (clip ke canvas agar tidak meluber ke panel)
        screen.set_clip(ui.canvas_rect)
        for shape in shapes:
            shape.draw(screen)
        screen.set_clip(None)

        # 4. Status bar kecil di bawah canvas
        ui.draw_status_info(mouse_pos, current_tool, selected_shape)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
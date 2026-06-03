# File: core/ui_manager.py
# UIManager baru — layout modern: Navbar, Panel Kiri, Canvas, Tools, Kontrol

import pygame
from core.constants import *
from core.ui_components import (Button, TextInput, ColorSwatch,
                                 draw_section_header, draw_panel_bg)


# Daftar objek per kategori
SHAPES_2D = [
    ("Donut",             "DONUT"),
    ("Belah Ketupat",     "BELAH_KETUPAT"),
    ("Setengah Lingkaran","SETENGAH_LINGKARAN"),
    ("Bintang",           "BINTANG"),
    ("Jajar Genjang",     "JAJAR_GENJANG"),
    ("Teks",              "TEXT"),
]
SHAPES_3D = [
    ("Bola",              "BOLA"),
    ("Setengah Bola",     "SETENGAH_BOLA"),
    ("Tabung",            "TABUNG"),
    ("Kerucut",           "KERUCUT"),
    ("Balok",             "BALOK"),
]

PALETTE = [
    (41, 128, 185),
    (231, 76, 60),
    (46, 204, 113),
    (241, 196, 15),
    (0, 0, 0),
]

SHORTCUTS = [
    ("1",        "Mode Select"),
    ("2-8/F1-F4","Pilih Objek"),
    ("C",        "Ganti Warna"),
    ("P",        "Ganti Arsiran"),
    ("+/-",      "Skala"),
    ("</> ",     "Geser Z"),
    ("WASDQE",   "Rotasi 3D"),
    ("M/N",      "Mirror H/V"),
    ("Del",      "Hapus"),
    ("Ctrl+Z/Y", "Undo/Redo"),
    ("Ctrl+S/O", "Save/Load"),
]


class UIManager:
    def __init__(self, screen):
        self.screen = screen

        # ── Font ──────────────────────────────────────────────
        self.font_sm   = pygame.font.SysFont("Segoe UI", 12)
        self.font_md   = pygame.font.SysFont("Segoe UI", 13)
        self.font_btn  = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_hdr  = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.font_nav  = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_sect = pygame.font.SysFont("Segoe UI", 12, bold=True)
        # Aliases
        self.font       = self.font_md
        self.header_font = self.font_hdr

        # ── Rects utama ───────────────────────────────────────
        self.navbar_rect  = pygame.Rect(0, 0, WINDOW_WIDTH, NAVBAR_HEIGHT)
        self.canvas_rect  = pygame.Rect(CANVAS_X, CANVAS_Y, CANVAS_WIDTH, CANVAS_HEIGHT)
        self.left_rect    = pygame.Rect(0, NAVBAR_HEIGHT, LEFT_PANEL_WIDTH, CANVAS_HEIGHT)
        self.tools_rect   = pygame.Rect(CANVAS_X + CANVAS_WIDTH, NAVBAR_HEIGHT,
                                        TOOLS_PANEL_WIDTH, CANVAS_HEIGHT)
        self.control_rect = pygame.Rect(CANVAS_X + CANVAS_WIDTH + TOOLS_PANEL_WIDTH,
                                        NAVBAR_HEIGHT, CONTROL_PANEL_WIDTH, CANVAS_HEIGHT)

        # ── State UI ──────────────────────────────────────────
        self.mode_2d3d    = "2D"        # "2D" atau "3D"
        self.ctrl_mode    = "TRANSLASI" # "TRANSLASI" / "ROTASI" / "SKALA"
        self.color_idx    = 0
        self.palette      = PALETTE[:]

        # ── Bangun semua tombol ───────────────────────────────
        self._build_left_panel()
        self._build_tools_panel()
        self._build_control_panel()

    # ══════════════════════════════════════════════════════════
    #  BUILDER
    # ══════════════════════════════════════════════════════════

    def _build_left_panel(self):
        lx  = 10
        lw  = LEFT_PANEL_WIDTH - 20
        y   = NAVBAR_HEIGHT + 36   # di bawah section header

        # Toggle 2D / 3D
        hw = (lw - 6) // 2
        self.btn_2d = Button(lx, y, hw, 28, "2D", active=True)
        self.btn_3d = Button(lx + hw + 6, y, hw, 28, "3D")
        y += 38

        # Tombol SELECT
        self.btn_select = Button(lx, y, lw, 28, "[ 1 ] Mode Select", active=True)
        y += 34

        # Tombol FILL
        self.btn_fill = Button(lx, y, lw, 28, "[ 9 ] Fill Area")
        y += 34

        # Shape buttons (diisi di _refresh_shape_buttons)
        # Tambahkan jarak untuk header "Pilih Bentuk" di _draw_left_panel
        self._shape_btn_y_start = y + 36
        self.shape_buttons = []
        self._refresh_shape_buttons()

        # Reset & Hapus (di bagian bawah panel)
        by = NAVBAR_HEIGHT + CANVAS_HEIGHT - 80
        hw2 = (lw - 6) // 2
        self.btn_reset = Button(lx, by, hw2, 30, "Reset")
        self.btn_hapus = Button(lx + hw2 + 6, by, hw2, 30, "Hapus", accent=False)

    def _refresh_shape_buttons(self):
        lx  = 10
        lw  = LEFT_PANEL_WIDTH - 20
        y   = self._shape_btn_y_start
        shapes = SHAPES_2D if self.mode_2d3d == "2D" else SHAPES_3D
        self.shape_buttons = []
        for label, tool_key in shapes:
            self.shape_buttons.append((Button(lx, y, lw, 28, label), tool_key))
            y += 34

    def _build_tools_panel(self):
        tx  = self.tools_rect.x + 10
        tw  = TOOLS_PANEL_WIDTH - 20
        y   = NAVBAR_HEIGHT + 36

        # ── Ukuran & Konten Bentuk ──
        y += 26   # section header space
        self.inp_lebar   = TextInput(tx, y + 18, tw, 26, "Lebar (W)")
        y += 50
        self.inp_tinggi  = TextInput(tx, y + 18, tw, 26, "Tinggi (H)")
        y += 50
        self.inp_depth   = TextInput(tx, y + 18, tw, 26, "Kedalaman (Z)")
        y += 50
        self.inp_teks    = TextInput(tx, y + 18, tw, 26, "Isi Teks", value="Teks Baru", numeric=False)
        y += 52
        self.btn_terapkan_ukuran = Button(tx, y, tw, 28, "Terapkan Ukuran", accent=True)
        y += 36

        # ── Warna ──
        y += 30   # section header space
        sw_size = 32
        sw_gap  = 8
        self.color_swatches = []
        sx = tx
        for i, col in enumerate(self.palette):
            self.color_swatches.append(ColorSwatch(sx, y, sw_size, col))
            sx += sw_size + sw_gap
        y += sw_size + 14

        # ── Outline ──
        y += 30   # section header space
        self.btn_outline = Button(tx, y, tw, 28, "Aktifkan Outline")
        y += 40
        self.inp_outline_w = TextInput(tx, y + 18, tw, 28, "Ketebalan Outline")

    def _build_control_panel(self):
        cx  = self.control_rect.x + 10
        cw  = CONTROL_PANEL_WIDTH - 20
        y   = NAVBAR_HEIGHT

        # ── Section: Kontrol (top header, drawn in _draw) ──
        y += 26  # section header "Kontrol" height

        # ── Section: Kontrol Mouse ──
        y += 26  # section header "Kontrol Mouse" height
        self.btn_mode_translasi = Button(cx, y, cw, 24, "Mode Translasi", active=True)
        y += 26
        self.btn_mode_rotasi    = Button(cx, y, cw, 24, "Mode Rotasi")
        y += 26
        self.btn_mode_skala     = Button(cx, y, cw, 24, "Mode Skala")
        y += 28

        # ── Section: Rotasi ──
        y += 26  # section header "Rotasi" height
        hw = (cw - 6) // 2
        self.btn_rot_kiri  = Button(cx, y, hw, 24, "◀ Rot Kiri")
        self.btn_rot_kanan = Button(cx + hw + 6, y, hw, 24, "Rot Kanan ▶")
        y += 28

        # ── Section: Translasi ──
        y += 26  # section header "Translasi" height
        bs  = 24
        gap = 3
        mid = cx + (cw - bs) // 2
        self.btn_t_up    = Button(mid, y, bs, bs, "↑")
        self.btn_t_left  = Button(mid - bs - gap, y + bs + gap, bs, bs, "←")
        self.btn_t_down  = Button(mid, y + bs + gap, bs, bs, "↓")
        self.btn_t_right = Button(mid + bs + gap, y + bs + gap, bs, bs, "→")
        y += bs * 2 + gap + 6

        # ── Section: Skala & Mirror ──
        y += 26  # section header "Skala & Mirror" height
        self.btn_perbesar = Button(cx, y, cw, 24, "＋ Perbesar", accent=True)
        y += 26
        self.btn_perkecil = Button(cx, y, cw, 24, "－ Perkecil")
        y += 26
        hw = (cw - 6) // 2
        self.btn_mirror_h = Button(cx, y, hw, 24, "↔ Mirror H")
        self.btn_mirror_v = Button(cx + hw + 6, y, hw, 24, "↕ Mirror V")
        y += 28

        # ── Section: Skew ──
        y += 26  # section header "Skew" height
        hw = (cw - 6) // 2
        self.btn_skew_x_min = Button(cx, y, hw, 24, "Skew X -")
        self.btn_skew_x_plus = Button(cx + hw + 6, y, hw, 24, "Skew X +")
        y += 26
        self.btn_skew_y_min = Button(cx, y, hw, 24, "Skew Y -")
        self.btn_skew_y_plus = Button(cx + hw + 6, y, hw, 24, "Skew Y +")
        y += 26
        self.btn_skew_reset = Button(cx, y, cw, 24, "Reset Skew")

    # ══════════════════════════════════════════════════════════
    #  DRAW
    # ══════════════════════════════════════════════════════════

    def draw_layout(self, current_tool="", selected_shape=None):
        mp = pygame.mouse.get_pos()
        self._draw_navbar()
        self._draw_canvas_bg()
        self._draw_left_panel(mp, current_tool)
        self._draw_tools_panel(mp, selected_shape)
        self._draw_control_panel(mp)

    def _draw_navbar(self):
        pygame.draw.rect(self.screen, C_NAVBAR, self.navbar_rect)
        title = self.font_nav.render("GRAFIKA 2D 3D", True, C_NAVBAR_TXT)
        self.screen.blit(title, (20, (NAVBAR_HEIGHT - title.get_height()) // 2))
        group = self.font_nav.render("Anggota Kelompok", True, C_TEXT_LIGHT)
        self.screen.blit(group, (WINDOW_WIDTH - group.get_width() - 20,
                                  (NAVBAR_HEIGHT - group.get_height()) // 2))

    def _draw_canvas_bg(self):
        pygame.draw.rect(self.screen, C_CANVAS_BG, self.canvas_rect)
        # Grid titik-titik
        step = 20
        for gx in range(self.canvas_rect.x + step, self.canvas_rect.right, step):
            for gy in range(self.canvas_rect.y + step, self.canvas_rect.bottom, step):
                pygame.draw.circle(self.screen, C_CANVAS_GRID, (gx, gy), 1)

    def _draw_left_panel(self, mp, current_tool=""):
        draw_panel_bg(self.screen, 0, NAVBAR_HEIGHT, LEFT_PANEL_WIDTH, CANVAS_HEIGHT)

        y = NAVBAR_HEIGHT
        y = draw_section_header(self.screen, self.font_sect, 0, y, LEFT_PANEL_WIDTH, "Pilih Objek")

        # Toggle 2D/3D
        self.btn_2d.active = (self.mode_2d3d == "2D")
        self.btn_3d.active = (self.mode_2d3d == "3D")
        self.btn_2d.draw(self.screen, self.font_btn, mp)
        self.btn_3d.draw(self.screen, self.font_btn, mp)

        # Mode Select & Fill (Sync active state)
        self.btn_select.active = (current_tool == "SELECT")
        self.btn_fill.active = (current_tool == "FILL")
        self.btn_select.draw(self.screen, self.font_md, mp)
        self.btn_fill.draw(self.screen, self.font_md, mp)

        # Section "Pilih Bentuk"
        sec_y = self._shape_btn_y_start - 32
        draw_section_header(self.screen, self.font_sect, 0, sec_y, LEFT_PANEL_WIDTH,
                             f"Pilih Bentuk {'2D' if self.mode_2d3d == '2D' else '3D'}")

        for btn, tool_key in self.shape_buttons:
            btn.active = (current_tool == tool_key)
            btn.draw(self.screen, self.font_md, mp)

        # Reset/Hapus
        draw_section_header(self.screen, self.font_sect, 0,
                             self.btn_reset.rect.y - 28, LEFT_PANEL_WIDTH, "Aksi")
        self.btn_reset.draw(self.screen, self.font_btn, mp)
        self.btn_hapus.draw(self.screen, self.font_btn, mp)

    def _draw_tools_panel(self, mp, selected_shape=None):
        tx = self.tools_rect.x
        tw = TOOLS_PANEL_WIDTH
        draw_panel_bg(self.screen, tx, NAVBAR_HEIGHT, tw, CANVAS_HEIGHT)

        y = NAVBAR_HEIGHT
        y = draw_section_header(self.screen, self.font_sect, tx, y, tw, "Tools")

        # ── Ukuran & Konten Bentuk ──
        y = draw_section_header(self.screen, self.font_sect, tx, y, tw, "Ukuran & Konten")
        self.inp_lebar.draw(self.screen, self.font_md, self.font_sm, mp)
        self.inp_tinggi.draw(self.screen, self.font_md, self.font_sm, mp)
        self.inp_depth.draw(self.screen, self.font_md, self.font_sm, mp)
        
        # Tampilkan input teks konten hanya jika objek terpilih berjenis TextShape
        from objek2d.text_shape import TextShape
        if isinstance(selected_shape, TextShape):
            self.inp_teks.draw(self.screen, self.font_md, self.font_sm, mp)

        self.btn_terapkan_ukuran.draw(self.screen, self.font_btn, mp)

        # ── Warna ──
        y = self.color_swatches[0].rect.y - 32
        draw_section_header(self.screen, self.font_sect, tx, y, tw, "Warna")
        for i, sw in enumerate(self.color_swatches):
            sw.draw(self.screen, selected=(i == self.color_idx))

        # Teks warna aktif
        cy = self.color_swatches[0].rect.bottom + 6
        ct = self.font_sm.render(f"Warna aktif: {self.palette[self.color_idx]}", True, C_TEXT_LIGHT)
        self.screen.blit(ct, (tx + 10, cy))

        # ── Outline ──
        y_out = self.inp_outline_w.rect.y - 62
        draw_section_header(self.screen, self.font_sect, tx, y_out, tw, "Outline")
        self.btn_outline.draw(self.screen, self.font_btn, mp)
        self.inp_outline_w.draw(self.screen, self.font_md, self.font_sm, mp)

    def _draw_control_panel(self, mp):
        cx = self.control_rect.x
        cw = CONTROL_PANEL_WIDTH
        draw_panel_bg(self.screen, cx, NAVBAR_HEIGHT, cw, CANVAS_HEIGHT)

        y = NAVBAR_HEIGHT
        y = draw_section_header(self.screen, self.font_sect, cx, y, cw, "Kontrol")

        # ── Kontrol Mouse ──
        draw_section_header(self.screen, self.font_sect, cx,
                             self.btn_mode_translasi.rect.y - 26, cw, "Kontrol Mouse")
        self.btn_mode_translasi.active = (self.ctrl_mode == "TRANSLASI")
        self.btn_mode_rotasi.active    = (self.ctrl_mode == "ROTASI")
        self.btn_mode_skala.active     = (self.ctrl_mode == "SKALA")
        self.btn_mode_translasi.draw(self.screen, self.font_btn, mp)
        self.btn_mode_rotasi.draw(self.screen, self.font_btn, mp)
        self.btn_mode_skala.draw(self.screen, self.font_btn, mp)

        # ── Rotasi ──
        draw_section_header(self.screen, self.font_sect, cx,
                             self.btn_rot_kiri.rect.y - 26, cw, "Rotasi")
        self.btn_rot_kiri.draw(self.screen, self.font_btn, mp)
        self.btn_rot_kanan.draw(self.screen, self.font_btn, mp)

        # ── Translasi ──
        draw_section_header(self.screen, self.font_sect, cx,
                             self.btn_t_up.rect.y - 26, cw, "Translasi")
        self.btn_t_up.draw(self.screen, self.font_btn, mp)
        self.btn_t_left.draw(self.screen, self.font_btn, mp)
        self.btn_t_down.draw(self.screen, self.font_btn, mp)
        self.btn_t_right.draw(self.screen, self.font_btn, mp)

        # ── Skala & Mirroring ──
        draw_section_header(self.screen, self.font_sect, cx,
                             self.btn_perbesar.rect.y - 26, cw, "Skala & Mirror")
        self.btn_perbesar.draw(self.screen, self.font_btn, mp)
        self.btn_perkecil.draw(self.screen, self.font_btn, mp)
        self.btn_mirror_h.draw(self.screen, self.font_btn, mp)
        self.btn_mirror_v.draw(self.screen, self.font_btn, mp)

        # ── Skew ──
        draw_section_header(self.screen, self.font_sect, cx,
                             self.btn_skew_x_min.rect.y - 26, cw, "Skew")
        self.btn_skew_x_min.draw(self.screen, self.font_btn, mp)
        self.btn_skew_x_plus.draw(self.screen, self.font_btn, mp)
        self.btn_skew_y_min.draw(self.screen, self.font_btn, mp)
        self.btn_skew_y_plus.draw(self.screen, self.font_btn, mp)
        self.btn_skew_reset.draw(self.screen, self.font_btn, mp)

        # ── Keyboard Shortcuts ──
        sy = self.btn_skew_reset.rect.bottom + 8
        if sy + 26 < NAVBAR_HEIGHT + CANVAS_HEIGHT - 10:
            draw_section_header(self.screen, self.font_sect, cx, sy, cw, "Keyboard Shortcuts")
            sy += 28
            for key, desc in SHORTCUTS:
                if sy + 16 > NAVBAR_HEIGHT + CANVAS_HEIGHT - 5:
                    break
                ks = self.font_sm.render(key, True, C_ACCENT)
                ds = self.font_sm.render(f"  {desc}", True, C_TEXT_LIGHT)
                self.screen.blit(ks, (cx + 10, sy))
                self.screen.blit(ds, (cx + 10 + ks.get_width(), sy))
                sy += 16

    # ══════════════════════════════════════════════════════════
    #  STATUS BAR (di atas canvas, bawah navbar)
    # ══════════════════════════════════════════════════════════

    def draw_status_info(self, mouse_pos, current_tool="", selected_shape=None):
        mx, my = mouse_pos
        if self.canvas_rect.collidepoint(mouse_pos):
            lx = mx - CANVAS_X
            ly = my - CANVAS_Y
            info = f"Canvas: ({lx}, {ly})  |  Tool: {current_tool}"
            if selected_shape:
                info += f"  |  Objek: {selected_shape.__class__.__name__}  Z={int(selected_shape.z)}"
        else:
            info = "Arahkan mouse ke canvas"
        ts = self.font_sm.render(info, True, C_TEXT_LIGHT)
        # Tampilkan di pojok kiri bawah canvas
        bx = CANVAS_X + 8
        by = CANVAS_Y + CANVAS_HEIGHT - 20
        pygame.draw.rect(self.screen, (255, 255, 255, 180),
                         (bx - 4, by - 2, ts.get_width() + 8, ts.get_height() + 4))
        self.screen.blit(ts, (bx, by))

    # ══════════════════════════════════════════════════════════
    #  HANDLE CLICK — returns action dict or None
    # ══════════════════════════════════════════════════════════

    def handle_ui_event(self, event, mouse_pos, shapes, selected_shape, current_tool):
        """
        Cek klik pada semua elemen UI panel.
        Return: dict {"action": ..., "value": ...} atau None
        """
        actions = []

        # ── Toggle 2D / 3D ──
        if self.btn_2d.is_clicked(mouse_pos, event):
            self.mode_2d3d = "2D"
            self._refresh_shape_buttons()

        if self.btn_3d.is_clicked(mouse_pos, event):
            self.mode_2d3d = "3D"
            self._refresh_shape_buttons()

        # ── Mode Select / Fill ──
        if self.btn_select.is_clicked(mouse_pos, event):
            actions.append({"action": "SET_TOOL", "value": "SELECT"})
            self.btn_select.active = True
            self.btn_fill.active   = False

        if self.btn_fill.is_clicked(mouse_pos, event):
            actions.append({"action": "SET_TOOL", "value": "FILL"})
            self.btn_fill.active   = True
            self.btn_select.active = False

        # ── Shape Buttons ──
        for btn, tool_key in self.shape_buttons:
            if btn.is_clicked(mouse_pos, event):
                actions.append({"action": "SET_TOOL", "value": tool_key})

        # ── Reset & Hapus ──
        if self.btn_reset.is_clicked(mouse_pos, event):
            actions.append({"action": "RESET"})

        if self.btn_hapus.is_clicked(mouse_pos, event):
            actions.append({"action": "HAPUS"})

        # ── Color Swatches ──
        for i, sw in enumerate(self.color_swatches):
            if sw.is_clicked(mouse_pos, event):
                self.color_idx = i
                actions.append({"action": "SET_COLOR_IDX", "value": i})
                if selected_shape:
                    selected_shape.set_color(self.palette[i])

        # ── Terapkan Ukuran & Konten ──
        if self.btn_terapkan_ukuran.is_clicked(mouse_pos, event):
            if selected_shape:
                w = self.inp_lebar.get_value()
                h = self.inp_tinggi.get_value()
                d = self.inp_depth.get_value()
                actions.append({"action": "APPLY_SIZE", "w": w, "h": h, "d": d})
                
                try:
                    ow = int(self.inp_outline_w.get_value())
                    selected_shape.outline_width = max(1, ow)
                except ValueError:
                    pass

                from objek2d.text_shape import TextShape
                if isinstance(selected_shape, TextShape):
                    selected_shape.text = self.inp_teks.get_value()
                actions.append({"action": "STATE_CHANGED"})

        # ── Outline Toggle ──
        if self.btn_outline.is_clicked(mouse_pos, event):
            if selected_shape:
                selected_shape.show_outline = not selected_shape.show_outline
                self.btn_outline.active = selected_shape.show_outline
                actions.append({"action": "STATE_CHANGED"})

        # ── TextInput events ──
        for inp in [self.inp_lebar, self.inp_tinggi, self.inp_depth, self.inp_outline_w, self.inp_teks]:
            val = inp.handle_event(event, mouse_pos)
            if val is not None and selected_shape:
                if inp == self.inp_outline_w:
                    try:
                        selected_shape.outline_width = max(1, int(val))
                        actions.append({"action": "STATE_CHANGED"})
                    except ValueError:
                        pass
                elif inp in [self.inp_lebar, self.inp_tinggi, self.inp_depth]:
                    w = self.inp_lebar.get_value()
                    h = self.inp_tinggi.get_value()
                    d = self.inp_depth.get_value()
                    actions.append({"action": "APPLY_SIZE", "w": w, "h": h, "d": d})
                elif inp == self.inp_teks:
                    from objek2d.text_shape import TextShape
                    if isinstance(selected_shape, TextShape):
                        selected_shape.text = str(val)
                    actions.append({"action": "STATE_CHANGED"})

        # ── Kontrol Mouse Mode ──
        if self.btn_mode_translasi.is_clicked(mouse_pos, event):
            self.ctrl_mode = "TRANSLASI"
        if self.btn_mode_rotasi.is_clicked(mouse_pos, event):
            self.ctrl_mode = "ROTASI"
        if self.btn_mode_skala.is_clicked(mouse_pos, event):
            self.ctrl_mode = "SKALA"

        # ── Rotasi tombol ──
        step = 0.1
        if self.btn_rot_kiri.is_clicked(mouse_pos, event) and selected_shape:
            if hasattr(selected_shape, "angle_z"):
                selected_shape.angle_z -= step
            actions.append({"action": "STATE_CHANGED"})

        if self.btn_rot_kanan.is_clicked(mouse_pos, event) and selected_shape:
            if hasattr(selected_shape, "angle_z"):
                selected_shape.angle_z += step
            actions.append({"action": "STATE_CHANGED"})

        # ── Translasi arah ──
        MOVE = 10
        if self.btn_t_up.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.translate(0, -MOVE)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_t_down.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.translate(0, MOVE)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_t_left.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.translate(-MOVE, 0)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_t_right.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.translate(MOVE, 0)
            actions.append({"action": "STATE_CHANGED"})

        # ── Skala & Mirroring ──
        if self.btn_perbesar.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.scale = round(selected_shape.scale + 0.1, 2)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_perkecil.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.scale = round(max(0.2, selected_shape.scale - 0.1), 2)
            actions.append({"action": "STATE_CHANGED"})

        # Mirroring Cermin
        if self.btn_mirror_h.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.flip_x = not selected_shape.flip_x
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_mirror_v.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.flip_y = not selected_shape.flip_y
            actions.append({"action": "STATE_CHANGED"})

        # ── Skew tombol ──
        skew_step = 0.05
        if self.btn_skew_x_min.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.skew_x = round(selected_shape.skew_x - skew_step, 2)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_skew_x_plus.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.skew_x = round(selected_shape.skew_x + skew_step, 2)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_skew_y_min.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.skew_y = round(selected_shape.skew_y - skew_step, 2)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_skew_y_plus.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.skew_y = round(selected_shape.skew_y + skew_step, 2)
            actions.append({"action": "STATE_CHANGED"})
        if self.btn_skew_reset.is_clicked(mouse_pos, event) and selected_shape:
            selected_shape.skew_x = 0.0
            selected_shape.skew_y = 0.0
            actions.append({"action": "STATE_CHANGED"})

        return actions

    def update_inputs_from_shape(self, shape):
        """Sinkronisasi nilai TextInput dari atribut objek terpilih."""
        if shape is None:
            return
            
        from objek2d.text_shape import TextShape
        if isinstance(shape, TextShape):
            self.inp_lebar.set_value(shape.size)
            self.inp_tinggi.set_value(shape.size)
            self.inp_depth.set_value(getattr(shape, "z", 0))
            self.inp_teks.set_value(shape.text)
        else:
            w = getattr(shape, "base_width", None) or getattr(shape, "base_outer_radius", None) or getattr(shape, "base_radius", 50)
            h = getattr(shape, "base_height", None) or getattr(shape, "base_outer_radius", None) or getattr(shape, "base_radius", 50)
            d = getattr(shape, "base_depth", None) or getattr(shape, "z", 0)
            self.inp_lebar.set_value(w)
            self.inp_tinggi.set_value(h)
            self.inp_depth.set_value(d)
        
        self.inp_outline_w.set_value(getattr(shape, "outline_width", 1))
        self.btn_outline.active = getattr(shape, "show_outline", True)

    def apply_size_to_shape(self, shape, w, h, d):
        """Terapkan nilai input ke atribut objek yang relevan."""
        if shape is None:
            return
            
        from objek2d.text_shape import TextShape
        if isinstance(shape, TextShape):
            shape.size = max(10, w)
        else:
            if hasattr(shape, "base_width"):   shape.base_width  = max(10, w)
            if hasattr(shape, "base_height"):  shape.base_height = max(10, h)
            if hasattr(shape, "base_depth"):   shape.base_depth  = max(10, d)
            if hasattr(shape, "base_outer_radius"): shape.base_outer_radius = max(10, w)
            if hasattr(shape, "base_radius"):  shape.base_radius = max(10, w)

    def update(self, dt_ms):
        """Tick update untuk animasi TextInput (cursor blink)."""
        for inp in [self.inp_lebar, self.inp_tinggi, self.inp_depth, self.inp_outline_w, self.inp_teks]:
            inp.update(dt_ms)

    # Compat: dipanggil dari kode lama
    def is_canvas_clicked(self, mouse_pos):
        return self.canvas_rect.collidepoint(mouse_pos)

    def get_local_coords(self, mouse_pos):
        return (mouse_pos[0] - CANVAS_X, mouse_pos[1] - CANVAS_Y)
# File: core/ui_components.py
# Widget-widget UI reusable untuk tampilan modern PyPaint

import pygame
from core.constants import *


class Button:
    """Tombol dengan hover effect, state aktif, dan varian aksen."""

    def __init__(self, x, y, w, h, text, active=False, accent=False):
        self.rect   = pygame.Rect(x, y, w, h)
        self.text   = text
        self.active = active
        self.accent = accent

    def draw(self, surface, font, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)

        if self.active:
            bg, fg, border = C_BTN_ACTIVE, C_BTN_ACT_TXT, C_BTN_ACTIVE
        elif self.accent:
            bg = C_ACCENT_HVR if hovered else C_ACCENT
            fg, border = C_ACCENT_TXT, C_ACCENT
        elif hovered:
            bg, fg, border = C_BTN_HOVER, C_BTN_NRM_TXT, C_BTN_BORDER
        else:
            bg, fg, border = C_BTN_NORMAL, C_BTN_NRM_TXT, C_BTN_BORDER

        pygame.draw.rect(surface, border, self.rect, border_radius=5)
        pygame.draw.rect(surface, bg, self.rect.inflate(-2, -2), border_radius=4)

        txt_surf = font.render(self.text, True, fg)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def is_clicked(self, mouse_pos, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(mouse_pos))


class TextInput:
    """Input teks numerik sederhana."""

    def __init__(self, x, y, w, h, label="", value="0", numeric=True):
        self.rect   = pygame.Rect(x, y, w, h)
        self.label  = label
        self.text   = str(value)
        self.active = False
        self._blink = True
        self._timer = 0
        self.numeric = numeric
        
        self.btn_w = 16
        self.up_rect = pygame.Rect(self.rect.right - self.btn_w, self.rect.y, self.btn_w, self.rect.h // 2)
        self.down_rect = pygame.Rect(self.rect.right - self.btn_w, self.rect.y + self.rect.h // 2, self.btn_w, self.rect.h - (self.rect.h // 2))

    def set_value(self, val):
        if self.numeric:
            v = int(val) if isinstance(val, float) and val == int(val) else val
            self.text = str(v)
        else:
            self.text = str(val)

    def get_value(self):
        if self.numeric:
            try:
                return int(self.text)
            except ValueError:
                return 0
        else:
            return self.text

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.numeric:
                    if self.up_rect.collidepoint(mouse_pos):
                        self.set_value(self.get_value() + 1)
                        return self.get_value()
                    elif self.down_rect.collidepoint(mouse_pos):
                        self.set_value(self.get_value() - 1)
                        return self.get_value()
                
                self.active = self.rect.collidepoint(mouse_pos)
            return None
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.numeric:
                    self.text = self.text[:-1] or "0"
                else:
                    self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
                return self.get_value()
            else:
                if self.numeric:
                    if event.unicode.isdigit() and len(self.text) < 5:
                        if self.text == "0":
                            self.text = event.unicode
                        else:
                            self.text += event.unicode
                else:
                    # Izinkan pengetikan huruf/karakter umum untuk teks
                    if event.unicode and len(self.text) < 30 and event.key not in (pygame.K_ESCAPE, pygame.K_TAB):
                        self.text += event.unicode
        return None

    def update(self, dt_ms):
        self._timer += dt_ms
        if self._timer >= 500:
            self._blink = not self._blink
            self._timer = 0

    def draw(self, surface, font, label_font, mouse_pos):
        if self.label:
            lbl = label_font.render(self.label, True, C_TEXT_LIGHT)
            surface.blit(lbl, (self.rect.x, self.rect.y - 17))

        border = C_ACCENT if self.active else C_BTN_BORDER
        pygame.draw.rect(surface, border, self.rect, border_radius=4)
        pygame.draw.rect(surface, C_WHITE, self.rect.inflate(-2, -2), border_radius=3)

        if self.numeric:
            pygame.draw.line(surface, C_BTN_BORDER, (self.rect.right - self.btn_w, self.rect.top), (self.rect.right - self.btn_w, self.rect.bottom), 1)
            pygame.draw.line(surface, C_BTN_BORDER, (self.rect.right - self.btn_w, self.rect.centery), (self.rect.right, self.rect.centery), 1)
            
            up_hover = self.up_rect.collidepoint(mouse_pos)
            down_hover = self.down_rect.collidepoint(mouse_pos)
            
            if up_hover: pygame.draw.rect(surface, C_BTN_HOVER, self.up_rect.inflate(-2, -2))
            if down_hover: pygame.draw.rect(surface, C_BTN_HOVER, self.down_rect.inflate(-2, -2))
            
            # Segitiga atas
            ux, uy = self.up_rect.center
            pygame.draw.polygon(surface, C_TEXT, [(ux - 4, uy + 2), (ux + 4, uy + 2), (ux, uy - 3)])
            
            # Segitiga bawah
            dx, dy = self.down_rect.center
            pygame.draw.polygon(surface, C_TEXT, [(dx - 4, dy - 2), (dx + 4, dy - 2), (dx, dy + 3)])

        display = self.text + ("|" if self.active and self._blink else "")
        ts = font.render(display, True, C_TEXT)
        surface.blit(ts, (self.rect.x + 8,
                          self.rect.y + (self.rect.h - ts.get_height()) // 2))


class ColorSwatch:
    """Kotak warna yang bisa diklik."""

    def __init__(self, x, y, size, color):
        self.rect  = pygame.Rect(x, y, size, size)
        self.color = color

    def draw(self, surface, selected=False):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        bc = C_ACCENT if selected else C_BTN_BORDER
        bw = 2 if selected else 1
        pygame.draw.rect(surface, bc, self.rect, bw, border_radius=5)

    def is_clicked(self, mouse_pos, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(mouse_pos))


def draw_section_header(surface, font, x, y, w, text):
    """Gambar header section dengan background abu dan teks."""
    r = pygame.Rect(x, y, w, 26)
    pygame.draw.rect(surface, C_PANEL_SECT, r)
    pygame.draw.line(surface, C_PANEL_BORD, (x, y + 26), (x + w, y + 26), 1)
    ts = font.render(text, True, C_TEXT)
    surface.blit(ts, (x + 10, y + (26 - ts.get_height()) // 2))
    return y + 26


def draw_panel_bg(surface, x, y, w, h):
    """Gambar background panel putih dengan border kiri."""
    pygame.draw.rect(surface, C_PANEL_BG, (x, y, w, h))
    pygame.draw.line(surface, C_PANEL_BORD, (x, y), (x, y + h), 1)
    pygame.draw.line(surface, C_PANEL_BORD, (x + w - 1, y), (x + w - 1, y + h), 1)

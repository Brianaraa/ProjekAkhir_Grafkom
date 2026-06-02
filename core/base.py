import pygame
from abc import ABC, abstractmethod

class BaseShape(ABC):
    """
    Abstract Base Class - Dirancang oleh System Architect (B).
    Menangani alur data koordinat 3D (X, Y, Z), pewarnaan, dan persistensi.
    """
    
    def __init__(self, x, y, z, color):
        # Koordinat 3D murni
        self.x = x
        self.y = y
        self.z = z 
        self.color = color
        
        # Atribut Pendukung
        self.scale = 1.0
        self.is_selected = False

        # Fitur Mirroring (Pencerminan)
        self.flip_x = False
        self.flip_y = False

        # Fitur Skew (Kemiringan)
        self.skew_x = 0.0   # Kemiringan horizontal (dalam satuan tan sudut)
        self.skew_y = 0.0   # Kemiringan vertikal

        # Outline state
        self.show_outline = True
        self.outline_width = 1

    @abstractmethod
    def draw(self, surface):
        """Wajib diimplementasikan oleh tiap objek."""
        pass

    @abstractmethod
    def is_clicked(self, mouse_pos):
        """Digunakan untuk memilih objek."""
        pass

    # --- SYSTEM LOGIC: TRANSFORMASI ---
    
    def translate(self, dx, dy, dz=0):
        """Update posisi berdasarkan input koordinat (termasuk Z)"""
        self.x += dx
        self.y += dy
        self.z += dz

    def apply_scaling(self, factor):
        """Manajemen skala objek"""
        self.scale = max(0.1, self.scale + factor)

    def set_color(self, new_color):
        """Implementasi Fitur Coloring"""
        self.color = new_color

    def apply_mirroring(self, px, py, pz=0):
        """Pencerminan titik koordinat lokal sebelum rotasi/proyeksi"""
        if getattr(self, "flip_x", False):
            px = -px
        if getattr(self, "flip_y", False):
            py = -py
        return px, py, pz

    def apply_skew(self, px, py, pz=0):
        """Terapkan transformasi skew (geser) pada titik lokal."""
        # skew_x: geser x berdasarkan y (shear horizontal)
        # skew_y: geser y berdasarkan x (shear vertikal)
        new_px = px + self.skew_x * py
        new_py = py + self.skew_y * px
        return new_px, new_py, pz

    # --- SYSTEM LOGIC: PERSISTENSI DATA ---

    def to_dict(self):
        """Mengubah objek menjadi data JSON-ready."""
        return {
            "class_name": self.__class__.__name__,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "color": list(self.color) if isinstance(self.color, tuple) else self.color,
            "scale": self.scale,
            "flip_x": self.flip_x,
            "flip_y": self.flip_y,
            "skew_x": self.skew_x,
            "skew_y": self.skew_y,
            "show_outline": self.show_outline,
            "outline_width": self.outline_width,
        }
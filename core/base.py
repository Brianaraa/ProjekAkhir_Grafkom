import pygame
from abc import ABC, abstractmethod

class BaseShape(ABC):
    """
    Abstract Base Class - Dirancang oleh System Architect (B).
    Menangani alur data koordinat 3D (X, Y, Z), pewarnaan, dan persistensi.
    """
    
    def __init__(self, x, y, z, color):
        # Koordinat 3D murni (Tugas B: Fokus pada data 3D betulan)
        self.x = x
        self.y = y
        self.z = z 
        self.color = color
        
        # Atribut Pendukung (Hanya yang diperlukan untuk tugas B)
        self.scale = 1.0
        self.is_selected = False # Penting untuk menentukan objek mana yang akan di-Coloring

    @abstractmethod
    def draw(self, surface):
        """Wajib diimplementasikan oleh jatah objek B (Donut, Bola, 1/2 Bola)"""
        pass

    @abstractmethod
    def is_clicked(self, mouse_pos):
        """Digunakan untuk memilih objek sebelum diganti warnanya (Fitur Coloring)"""
        pass

    # --- SYSTEM LOGIC: TRANSFORMASI DATA (Jatah B) ---
    
    def translate(self, dx, dy, dz=0):
        """Update posisi berdasarkan input koordinat (termasuk Z)"""
        self.x += dx
        self.y += dy
        self.z += dz

    def apply_scaling(self, factor):
        """Manajemen skala objek"""
        self.scale = max(0.1, self.scale + factor)

    def set_color(self, new_color):
        """Implementasi Fitur Coloring (Tugas B)"""
        self.color = new_color

    # --- SYSTEM LOGIC: PERSISTENSI DATA (Jatah B - Save/Load) ---

    def to_dict(self):
        """
        Mengubah objek menjadi data JSON-ready. 
        Mencatat X, Y, Z secara lengkap.
        """
        return {
            "class_name": self.__class__.__name__,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "color": list(self.color) if isinstance(self.color, tuple) else self.color,
            "scale": self.scale
        }
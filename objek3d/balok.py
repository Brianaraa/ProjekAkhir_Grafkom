import pygame
import math
from core.base import BaseShape
from core.math_utils import rotate_3d, project_3d_to_2d

class Balok(BaseShape):
    """
    Implementasi Objek 3D Balok - Dirancang oleh Lead Developer (A).
    Menerapkan rotasi 3D dan proyeksi perspektif.
    """
    def __init__(self, x, y, z, color, width=80, height=50, depth=60):
        super().__init__(x, y, z, color)
        self.base_width = max(width, 1)
        self.base_height = max(height, 1)
        self.base_depth = max(depth, 1)
        
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

    def draw(self, surface):
        w = self.base_width * self.scale
        h = self.base_height * self.scale
        d = self.base_depth * self.scale
        
        if w <= 0 or h <= 0 or d <= 0: return

        # 8 titik kubus (pusat di 0,0,0 lokal)
        vertices = [
            [-w/2, -h/2, -d/2], [w/2, -h/2, -d/2], [w/2, h/2, -d/2], [-w/2, h/2, -d/2],
            [-w/2, -h/2, d/2],  [w/2, -h/2, d/2],  [w/2, h/2, d/2],  [-w/2, h/2, d/2]
        ]
        
        projected = []
        
        for v in vertices:
            vx, vy, vz = v
            vx, vy, vz = self.apply_mirroring(vx, vy, vz)
            
            # Gunakan math_utils.rotate_3d (konsisten dengan objek 3D lainnya)
            rx, ry, rz = rotate_3d(vx, vy, vz, self.angle_x, self.angle_y, self.angle_z)
            
            # Gunakan math_utils.project_3d_to_2d (Y dibalik — konsisten dengan Bola/Tabung/Kerucut)
            px, py = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
            projected.append((int(px), int(py)))
            
        # Draw edges
        edges = [
            (0,1), (1,2), (2,3), (3,0), # Back face
            (4,5), (5,6), (6,7), (7,4), # Front face
            (0,4), (1,5), (2,6), (3,7)  # Connecting edges
        ]
        
        for e in edges:
            pygame.draw.line(surface, self.color, projected[e[0]], projected[e[1]], 2)
            
        if self.is_selected:
            min_x = min([p[0] for p in projected])
            max_x = max([p[0] for p in projected])
            min_y = min([p[1] for p in projected])
            max_y = max([p[1] for p in projected])
            
            pygame.draw.rect(surface, (255, 0, 0), (min_x, min_y, max_x - min_x, max_y - min_y), 1)
            
            for p in [(min_x, min_y), (max_x, min_y), (min_x, max_y), (max_x, max_y)]:
                pygame.draw.rect(surface, (0, 0, 255), (p[0] - 3, p[1] - 3, 6, 6))

    def is_clicked(self, mouse_pos):
        mx, my = mouse_pos
        w = self.base_width * self.scale
        h = self.base_height * self.scale
        d = self.base_depth * self.scale
        
        max_dim = max(w, h, d)
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        radius = max_dim * factor
        
        distance = math.hypot(mx - self.x, my - self.y)
        return distance <= radius

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "width": self.base_width,
            "height": self.base_height,
            "depth": self.base_depth,
            "angle_x": self.angle_x,
            "angle_y": self.angle_y,
            "angle_z": self.angle_z
        })
        return data

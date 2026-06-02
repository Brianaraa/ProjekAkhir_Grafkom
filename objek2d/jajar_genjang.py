import pygame
import math
from core.base import BaseShape
from core.pattern import PatternGenerator, PatternStyle
from fitur.algoritma import ManualAlgorithms
from core.math_utils import rotate_3d, project_3d_to_2d

class JajarGenjang(BaseShape):
    def __init__(self, x, y, z, color, width=100, height=60, offset=30):
        super().__init__(x, y, z, color)
        self.base_width = width
        self.base_height = height
        self.base_offset = offset
        self.angle_z = 0
        self.fill_type = PatternStyle.FILL_SOLID
        self.outline_color = (0, 0, 0)

    def _get_local_points(self):
        hw = (self.base_width * self.scale) / 2
        hh = (self.base_height * self.scale) / 2
        ho = (self.base_offset * self.scale) / 2
        return [(-hw+ho,-hh,0),(hw+ho,-hh,0),(hw-ho,hh,0),(-hw-ho,hh,0)]

    def draw(self, surface):
        if self.base_width * self.scale <= 0 or self.base_height * self.scale <= 0:
            return
        projected_points = []
        for px, py, pz in self._get_local_points():
            px, py, pz = self.apply_mirroring(px, py, pz)
            px, py, pz = self.apply_skew(px, py, pz)
            rx, ry, rz = rotate_3d(px, py, pz, 0, 0, self.angle_z)
            fx, fy = project_3d_to_2d(rx, ry, rz + self.z, self.x, self.y)
            projected_points.append((fx, fy))

        min_x = min(p[0] for p in projected_points)
        max_x = max(p[0] for p in projected_points)
        min_y = min(p[1] for p in projected_points)
        max_y = max(p[1] for p in projected_points)
        surf_w = max_x - min_x
        surf_h = max_y - min_y

        if self.fill_type == PatternStyle.FILL_SOLID:
            pygame.draw.polygon(surface, self.color, projected_points)
        elif surf_w > 0 and surf_h > 0:
            temp_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            tile = PatternGenerator.create_fill_pattern(self.fill_type, self.outline_color)
            PatternGenerator.fill_surface_with_pattern(temp_surface, tile)
            mask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            local_pts = [(p[0]-min_x, p[1]-min_y) for p in projected_points]
            pygame.draw.polygon(mask, (255,255,255,255), local_pts)
            temp_surface.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(temp_surface, (min_x, min_y))

        if self.show_outline:
            for i in range(len(projected_points)):
                ManualAlgorithms.draw_line_bresenham(surface, self.outline_color,
                    projected_points[i], projected_points[(i+1)%len(projected_points)], self.outline_width)

        if self.is_selected:
            self._draw_selection_style(surface, min_x, min_y, surf_w, surf_h)

    def _draw_selection_style(self, surface, min_x, min_y, w, h):
        rx, ry = int(min_x)-2, int(min_y)-2
        pygame.draw.rect(surface, (59,130,246), (rx, ry, int(w)+4, int(h)+4), 2)
        for c in [(rx,ry),(rx+int(w)+4,ry),(rx,ry+int(h)+4),(rx+int(w)+4,ry+int(h)+4)]:
            pygame.draw.rect(surface, (255,255,255), (c[0]-3, c[1]-3, 7, 7))
            pygame.draw.rect(surface, (59,130,246), (c[0]-3, c[1]-3, 7, 7), 1)

    def is_clicked(self, mouse_pos):
        mx, my = mouse_pos
        dx = mx - self.x
        dy = -(my - self.y)
        fov = 400
        factor = fov / (fov + self.z) if (fov + self.z) != 0 else 1
        dx /= factor; dy /= factor
        cos_a = math.cos(-self.angle_z); sin_a = math.sin(-self.angle_z)
        local_x = dx*cos_a - dy*sin_a; local_y = dx*sin_a + dy*cos_a
        if self.flip_x: local_x = -local_x
        if self.flip_y: local_y = -local_y
        hw = (self.base_width*self.scale)/2; hh = (self.base_height*self.scale)/2
        ho = (self.base_offset*self.scale)/2
        points = [(-hw+ho,-hh),(hw+ho,-hh),(hw-ho,hh),(-hw-ho,hh)]
        inside = False; n = len(points); p1x,p1y = points[0]
        for i in range(1, n+1):
            p2x,p2y = points[i%n]
            if local_y > min(p1y,p2y) and local_y <= max(p1y,p2y) and local_x <= max(p1x,p2x):
                if p1y != p2y:
                    xinters = (local_y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                if p1x == p2x or local_x <= xinters:
                    inside = not inside
            p1x,p1y = p2x,p2y
        return inside

    def to_dict(self):
        data = super().to_dict()
        data.update({"width":self.base_width,"height":self.base_height,
                     "offset":self.base_offset,"angle_z":self.angle_z,"fill_type":self.fill_type})
        return data

import math

from projections.generic import GenericProjection


class GnomonicProjection(GenericProjection):

    def __init__(self):
        self.projection_type = self.ProjectionType.Azimuthal
        self.central_x = 0
        self.central_y = 0
        self.depth = 40

    def get_coords(self, x, y):
        if abs(x - self.central_x / 360) > 1.7:
            return 0, 0
        cosx = math.cos(x)
        cosy = math.cos(y)
        sinx = math.sin(x)
        siny = math.sin(y)
        cos_c = cosy * cosx
        val_x = (cosy * sinx) / cos_c
        val_y = siny / cos_c

        return int(max(-500, min(val_x * self.depth, 500))), int(max(-500, min(val_y * self.depth, 500)))

    def set_distance(self, value):
        self.depth = value

    def set_central_point(self, x, y):
        self.central_x = x
        self.central_y = y

import math

from projections.generic import GenericProjection


class GnomonicProjection(GenericProjection):
    """Equatorial gnomonic, tangent at (lon 0, lat 0).

    Every great circle projects to a straight line. Only the hemisphere within
    90 degrees of the centre can be shown; beyond that the projection runs to
    infinity, so those points are dropped.
    """

    def __init__(self):
        self.projection_type = self.ProjectionType.Azimuthal

    def get_coords(self, x, y):
        cos_c = math.cos(y) * math.cos(x)
        if cos_c <= 0.03:
            return -10000, -10000
        return 40 * math.cos(y) * math.sin(x) / cos_c, 40 * math.sin(y) / cos_c

import math

from projections.generic import GenericProjection


class AzimuthalOrthographicProjection(GenericProjection):
    """Equatorial orthographic, tangent at (lon 0, lat 0): the globe as seen
    from infinite distance. Only the facing hemisphere is drawn.
    """

    def __init__(self):
        self.projection_type = self.ProjectionType.Azimuthal

    def get_coords(self, x, y):
        if math.cos(y) * math.cos(x) < 0:
            return -10000, -10000
        return 170 * math.cos(y) * math.sin(x), 170 * math.sin(y)

import math

from projections.generic import GenericProjection


class AzimuthalEquidistantProjection(GenericProjection):
    """Equatorial azimuthal equidistant, centred at (lon 0, lat 0).

    Distance and direction from the centre are true to scale, so the whole
    world fits inside a disc whose radius grows in proportion to the angular
    distance from the centre.
    """

    def __init__(self):
        self.projection_type = self.ProjectionType.Azimuthal

    def get_coords(self, x, y):
        c = math.acos(max(-1.0, min(1.0, math.cos(y) * math.cos(x))))
        sin_c = math.sin(c)
        if sin_c < 1e-9:
            return 0.0, 0.0
        k = 55 * c / sin_c
        return k * math.cos(y) * math.sin(x), k * math.sin(y)

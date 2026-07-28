import math

from projections.generic import GenericProjection


class AitoffProjection(GenericProjection):
    """Aitoff: the azimuthal-equidistant hemisphere stretched 2:1, so the whole
    world fits in an ellipse twice as wide as it is tall. Its unstretched form
    is exactly the azimuthal equidistant applied to half the longitude.
    """

    def __init__(self):
        self.projection_type = self.ProjectionType.Azimuthal

    def get_coords(self, x, y):
        cos_y = math.cos(y)
        alpha = math.acos(max(-1.0, min(1.0, cos_y * math.cos(x / 2))))
        sin_a = math.sin(alpha)
        if sin_a < 1e-9:
            return 0.0, 0.0
        k = 55 * alpha / sin_a
        return 2 * k * cos_y * math.sin(x / 2), k * math.sin(y)

import math

from projections.proj_generic import GenericProjection


class AzimuthalOrthographicProjection(GenericProjection):

	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		if (x < 0 or x > 180):
			return -10000, -10000
		x = 170 * - math.cos(y) * math.cos(x)
		y = 170 * math.sin(y) 
		return x, y
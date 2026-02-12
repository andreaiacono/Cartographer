import math

from projections.generic import GenericProjection


class MercatorProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Cylindrical

	def get_coords(self, x, y):

		return math.degrees(x), 60 * math.asinh(math.tan(y))

	

import math

from projections.generic import GenericProjection


class SinusoidalProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.PseudoCylindrical

	def get_coords(self, x, y):
		return 70 * x * math.cos(y), 2 * math.degrees(y)


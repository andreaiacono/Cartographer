import math

from projections.proj_generic import GenericProjection


class MillerProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Cylindric
		self.pi_div_four = math.pi / float(4)

	def get_coords(self, x, y):
		
		val = self.pi_div_four + 0.4 * y
		tan = math.tan(val)
		if tan <= 0:
			tan = 0.00001
		return 1.5 * math.degrees(x), 75 * math.log(tan)

	
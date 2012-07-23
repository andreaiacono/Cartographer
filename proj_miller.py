from proj_generic import GenericProjection
import math

class MillerProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Cylindric
		self.pi_div_four = math.pi / float(4)

	def get_coords(self, x, y):
		
		return x, 50 * math.log(math.tan(self.pi_div_four + 0.4 * math.radians(y)))

	
import math

from projections.generic import GenericProjection


class CollignonProjection(GenericProjection):
	
	def __init__(self):
		self.constant_x = 2 / math.sqrt(math.pi)
		self.constant_y = math.sqrt(math.pi)
		self.projection_type = self.ProjectionType.PseudoCylindrical

	def get_coords(self, x, y):
		return self.constant_x * math.degrees(x) * math.sqrt(1 - math.sin(y)), 95 * self.constant_y * (1 - math.sqrt(1 - math.sin(y)))


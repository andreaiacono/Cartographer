import math

from projections.generic import GenericProjection


class MollweideProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.PseudoCylindric

	def get_coords(self, x, y):
		
		val = 2 * y / math.pi
		if val < -1:
			val = -1
		elif val > 1:
			val = 1
		theta = math.asin(val)
		return 240 * x * math.cos(theta) / math.pi, 120 * math.sin(theta)
	
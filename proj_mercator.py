from proj_generic import GenericProjection
import math

class MercatorProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Cylindric

	def get_coords(self, x, y):
		
		return math.degrees(x), 30 * math.asinh(math.tan(y))

	

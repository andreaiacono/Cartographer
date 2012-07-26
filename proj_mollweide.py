from proj_generic import GenericProjection
import math

class MollweideProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.PseudoCylindric

	def get_coords(self, x, y):
		
		theta = math.asin(2 * y / math.pi)
		return 100 * math.sqrt(2) * x * math.cos(theta) / math.pi, 50 * math.sqrt(2) * math.sin(theta)
	
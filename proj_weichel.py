from proj_generic import GenericProjection
import math

class WeichelProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		
		r = 2 * math.sin(0.25 * (math.pi - (2 * y)))
		theta = x + 0.25 * (math.pi - 2 * y)
		
		x = r * math.cos(theta)
		y = r * math.sin(theta)
		
		return 85 * x, 85 * y 

	

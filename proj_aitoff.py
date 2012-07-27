from proj_generic import GenericProjection
import math

class AitoffProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		
		cos_y = math.cos(y)
		z = math.acos(cos_y * math.cos(x/2))
		if z == 0:
			z = 0.000001
		return 110 * z * cos_y * math.sin(x / 2) / math.sin(z), 110 * z * math.sin(y) / math.sin(z) 

	
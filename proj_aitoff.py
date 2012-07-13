from proj_generic import GenericProjection
import math

class AitoffProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		
		cos_y = math.cos(math.radians(y))
		z = math.acos(cos_y * math.cos(math.radians(x/2)))
		return 50 * z * cos_y * math.sin(math.radians(x / 2)) / math.sin(z), 50 * z * math.sin(math.radians(y)) / math.sin(z) 

	
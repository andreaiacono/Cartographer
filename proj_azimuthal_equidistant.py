from proj_generic import GenericProjection
import math

class AzimuthalEquidistantProjection(GenericProjection):

	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		
		a = math.acos(math.cos(y) * math.cos(x/2))
		if (a == 0):
			a = 0.00001
		new_x = 110 * a * math.cos(y) * math.sin (x/2) / math.sin(a)
		new_y = 110 * a * math.sin(y) / math.sin(a)
		return new_x, new_y
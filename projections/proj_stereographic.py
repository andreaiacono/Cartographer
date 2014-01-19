import math

from projections.proj_generic import GenericProjection


class StereographicProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		cos_y = math.cos(y)
		den= 1 + cos_y * math.cos(x)
		if den == 0:
			den = 0.00001
		k = 30 / den
		new_x = k * cos_y * math.sin(x)
		new_y = k * math.sin(y) 

		return new_x, new_y
		
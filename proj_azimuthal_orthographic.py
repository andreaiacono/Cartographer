from proj_generic import GenericProjection
import math

class AzimuthalOrthographicProjection(GenericProjection):

	def get_coords(self, x, y):
		if (x < 0 or x > 180):
			return -10000, -10000
		x = 90 * - math.cos(math.radians(y)) * math.cos(math.radians(x))
		y = 90 * math.sin(math.radians(y)) 
		return x, y
from proj_generic import GenericProjection
import math

class SinusoidalProjection(GenericProjection):

	def get_coords(self, x, y):
		return 35* math.radians(x) * math.cos(math.radians(y)), y


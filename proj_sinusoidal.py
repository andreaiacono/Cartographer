from proj_generic import GenericProjection
import math

class SinusoidalProjection(GenericProjection):

	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		return 35* math.radians(x) * math.cos(math.radians(y)), y


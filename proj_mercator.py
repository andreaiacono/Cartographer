from proj_generic import GenericProjection
import math

class MercatorProjection(GenericProjection):

	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		y = 30 * math.asinh(math.tan(math.radians(y)))
		return x, y


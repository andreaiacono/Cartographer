from proj_generic import GenericProjection
import math

class MercatorProjection(GenericProjection):

	def get_x_coord(self, x, centerx, y, centery, width, height):
		
		return x

	def get_y_coord(self, x, centerx, y, centery, width, height):
		
		py = 30 * math.asinh(math.tan(math.radians(y)))
		return py

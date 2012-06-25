from proj_generic import GenericProjection
import math

class PetersProjection(GenericProjection):

	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		new_y = 85 * math.sin(math.radians(y))
		return x, new_y


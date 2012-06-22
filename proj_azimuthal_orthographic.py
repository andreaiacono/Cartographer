from proj_generic import GenericProjection
import math

class AzimuthalOrthographicProjection(GenericProjection):

	def get_coords(self, x, centerx, y, centery, width, height):
		#x = 100 * math.cos(math.radians(y)) * math.sin(math.radians(x))
		#y = 100 * math.cos(math.radians(y)) * math.cos(math.radians(x))
		#x = width * math.cos(math.radians(y) * math.sin(math.radians(x - centerx)))
		#y = height * math.cos(math.radians(centery) * math.sin(math.radians(y))) - math.sin(math.radians(centery)) * math.cos(math.radians(y)) * math.sin(math.radians(x - centerx))
		x = 100 * - math.cos(math.radians(y)) * math.cos(math.radians(x))
		y = 100 * math.sin(math.radians(y)) 
		return x, y
from proj_generic import GenericProjection
import math

class AzimuthalOrthographicProjection(GenericProjection):

	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		#x = 100 * math.cos(math.radians(y)) * math.sin(math.radians(x))
		#y = 100 * math.cos(math.radians(y)) * math.cos(math.radians(x))
		#x = width * math.cos(math.radians(y) * math.sin(math.radians(x - centerx)))
		#y = height * math.cos(math.radians(centery) * math.sin(math.radians(y))) - math.sin(math.radians(centery)) * math.cos(math.radians(y)) * math.sin(math.radians(x - centerx))
		#if (math.fabs(centerx - original_x) > 90 or math.fabs(centery - original_y) > 90):
		#	return -10000, -10000
		if (x < 0 or x > 180):
			return -10000, -10000
		x = 90 * - math.cos(math.radians(y)) * math.cos(math.radians(x))
		y = 90 * math.sin(math.radians(y)) 
		return x, y
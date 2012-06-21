from proj_generic import GenericProjection
import math

class AzimuthalOrthographicProjection(GenericProjection):

	def get_x_coord(self, x, centerx, y, centery, width, height):
		px = width * math.cos(math.radians(y) * math.sin(math.radians(x - centerx)))
		return px

	def get_y_coord(self, x, centerx, y, centery, width, height):
		py = height * math.cos(math.radians(centery) * math.sin(math.radians(y))) - math.sin(math.radians(centery)) * math.cos(math.radians(y)) * math.sin(math.radians(x - centerx))
		return py

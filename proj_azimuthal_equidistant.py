from proj_generic import GenericProjection
import math

class AzimuthalEquidistantProjection(GenericProjection):

	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		
#		if x == 0:
#			x=0.001
#		
#		c = math.atan(math.radians(y/(float(x))))
#		k = c / math.sin(c)
#		
#		if (x < 90 or x > 90):
#			return -10000, -10000
#		x = 20 * k * math.cos(math.radians(y)) * math.sin(math.radians(x))
#		y = 20 * k * math.sin(math.radians(y)) 

		new_x = 80 * math.sqrt(2 * (1-math.sin(math.radians(y)))) * math.sin(math.radians(x))
		new_y = -80 * math.sqrt(2 * (1-math.sin(math.radians(y)))) * math.cos(math.radians(x))
		return new_x, new_y
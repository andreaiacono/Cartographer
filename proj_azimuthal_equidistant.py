from proj_generic import GenericProjection
import math

class AzimuthalEquidistantProjection(GenericProjection):

	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal

	def get_coords(self, x, y):
		
#		if x == 0:
#			x=0.001
#		
#		c = math.atan(y/(float(x))))
#		k = c / math.sin(c)
#		
#		if (x < 90 or x > 90):
#			return -10000, -10000
#		x = 20 * k * math.cos(y)) * math.sin(x))
#		y = 20 * k * math.sin(y)) 

#		new_x = 80 * math.sqrt(2 * (1-math.sin(y)))) * math.sin(x))
#		new_y = -80 * math.sqrt(2 * (1-math.sin(y)))) * math.cos(x))

		a = math.acos(math.cos(y) * math.cos(x/2))
		if (a == 0):
			a = 0.00001
		new_x = 80 * a * math.cos(y) * math.sin (x/2) / math.sin(a)
		new_y = 80 * a * math.sin(y) / math.sin(a)
		return new_x, new_y
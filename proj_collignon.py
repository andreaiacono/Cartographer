from proj_generic import GenericProjection
import math

class CollignonProjection(GenericProjection):
	
	def __init__(self):
		self.constant_x = 2 / math.sqrt(math.pi)
		self.constant_y = math.sqrt(math.pi)
		

	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		return -self.constant_x * x * math.sqrt(1 - math.sin(math.radians(y))), - 45 * self.constant_y * (1 - math.sqrt(1 - math.sin(math.radians(y))))


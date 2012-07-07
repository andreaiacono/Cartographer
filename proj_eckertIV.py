from proj_generic import GenericProjection
import math

class EckertIVProjection(GenericProjection):

	def __init__(self):
		self.constant_x = 2 / math.sqrt(math.pi * (4 + math.pi))
		self.constant_y = 2 * math.sqrt(math.pi / (4 + math.pi))
		self.projection_type = self.ProjectionType.PseudoCylindric

	def get_coords(self, x, y):
		new_x = 60 * self.constant_x * math.radians(x) * (1 + math.cos(math.radians(y)))
		new_y = 60 * self.constant_y * math.sin(math.radians(y))
		return new_x, new_y

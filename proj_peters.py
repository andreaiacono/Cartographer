from proj_generic import GenericProjection
import math

class PetersProjection(GenericProjection):

	def __init__(self):
		self.projection_type = self.ProjectionType.Cylindric


	def get_coords(self, x, y):
		return x, 85 * math.sin(math.radians(y))

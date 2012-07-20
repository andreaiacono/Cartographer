from proj_generic import GenericProjection
import math
import mpmath

class EqualAreaProjection(GenericProjection):

	def __init__(self):
		self.projection_type = self.ProjectionType.Cylindric
		self.set_standard_latitude(44.138)


	def get_coords(self, x, y):
		return x * self.cos_standard_latitude, 120 * math.sin(math.radians(y)) * self.sec_standard_latitude

	def set_standard_latitude(self, val):
		self.cos_standard_latitude = math.cos(math.radians(val))
		self.sec_standard_latitude = mpmath.sec(math.radians(val))
		
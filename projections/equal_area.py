import math

import mpmath

from projections.generic import GenericProjection


class EqualAreaProjection(GenericProjection):

	def __init__(self):
		self.projection_type = self.ProjectionType.Cylindrical
		self.set_standard_latitude(math.radians(44.138))


	def get_coords(self, x, y):
		# Cylindrical equal-area projection formula:
		# x_proj = λ * cos(φ₀)  [longitude scaled by cosine of standard parallel]
		# y_proj = sin(φ) / cos(φ₀)  [sine of latitude divided by cosine of standard parallel]
		# Scale up by 1.5 for x and 90 for y to make the map larger and fill canvas better
		return 1.5 * math.degrees(x) * self.cos_standard_latitude, 90 * math.sin(y) / self.cos_standard_latitude

	def set_standard_latitude(self, val):
		self.cos_standard_latitude = math.cos(val)
		self.sec_standard_latitude = mpmath.sec(val)
		
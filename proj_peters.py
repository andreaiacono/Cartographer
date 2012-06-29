from proj_generic import GenericProjection
import math

class PetersProjection(GenericProjection):

	def __init__(self):
		
		self.new_y = [0.0 for col in range(-18000,18000)]
		
		for i in range (-18000, 18000):
			fract_y = i / float(100)
			self.new_y[i] = 85 * math.sin(math.radians(fract_y))

	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		return x, self.new_y[int(y*100)]


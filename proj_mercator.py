from proj_generic import GenericProjection
import math
import mpmath

class MercatorProjection(GenericProjection):

	def __init__(self):
		
		self.new_y = [0.0 for col in range(-1800,1800)]
		
		for i in range (-1800, 1800):
			fract_y = i / float(10)
			self.new_y[i] = (35*mpmath.asinh(math.tan(math.radians(fract_y))))
	
	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		#y = 35*math.asinh(math.tan(math.radians(y)))
		return x, self.new_y[int(y*10)]


from proj_generic import GenericProjection
import math
import mpmath

class MercatorProjection(GenericProjection):
	

	def __init__(self):
		
		self.new_y = [0.0 for col in range(-18000,18000)]
		self.phi1 = 0
		self.phi2 = 0
		
		for i in range (-18000, 18000):
			fract_y = i / float(100)
			self.new_y[i] = (35*mpmath.asinh(math.tan(math.radians(fract_y))))
	
	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		#y = 35*math.asinh(math.tan(math.radians(y)))
		return x, self.new_y[int(y*100)]

	def set_phi(self, phi1, phi2):
		self.phi1 = phi1
		self.phi2 = phi2
		

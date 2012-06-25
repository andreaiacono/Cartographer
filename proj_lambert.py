from proj_generic import GenericProjection
import math
import mpmath

class LambertProjection(GenericProjection):

	def __init__(self):
	
		self.phi1 = math.radians(30)
		self.phi2 = math.radians(60)
		self.n = (math.log(math.cos(self.phi1) * mpmath.sec(self.phi2)))/	math.log(math.tan(math.pi/4 + self.phi2/2) * mpmath.cot(math.pi/4 + self.phi1/2))
		self.F = (math.cos(self.phi1) * math.tan(math.pi / 4 + self.phi1 / 2))/ self.n
		
		
	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		
		#print "y=" + str(original_y) +"  n = " + str(self.n)
		r = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(y)/2) , self.n)
		r0 = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(y)/2 ), self.n)
			
		new_x = r * math.sin(self.n*(math.radians(x - centerx)))	
		new_y = r0 - r * math.cos(self.n * (math.radians(x-centerx)))					
		
		return 4*new_x, 4*new_y
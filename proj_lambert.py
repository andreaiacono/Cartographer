from proj_generic import GenericProjection
import math
import mpmath

class LambertProjection(GenericProjection):

	def __init__(self):
	
		self.phi1 = math.radians(30)
		self.phi2 = math.radians(60)
		self.n = (math.log(math.cos(self.phi1) * mpmath.sec(self.phi2)))/	math.log(math.tan(math.pi/4 + self.phi2/2) * mpmath.cot(math.pi/4 + self.phi1/2))
		self.F = (math.cos(self.phi1) * math.tan(math.pi / 4 + self.phi1 / 2))/ self.n
		self.r0 = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(30)/2 ), self.n)
		
		for y in range (-9000, 9000):
			print "y=" + str(y)
			fract_y = y / float(100)
			self.r[y] = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(fract_y/2)) , self.n)
		
	def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
		
		#print "y=" + str(original_y) +"  n = " + str(self.n)
		#r = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(y)/2) , self.n)
		#print "val=" + str(x-centerx) + " y=" + str(y)
		new_x = self.r[int(y*100)] * math.sin(self.n*(math.radians(x - centerx)))	
		new_y = self.r0 - self.r[int(y*100)] * math.cos(self.n * (math.radians(x-centerx)))					
		
		return 4*new_x, 4*new_y
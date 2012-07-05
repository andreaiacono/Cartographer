from proj_generic import GenericProjection
import math
import mpmath

class LambertProjection(GenericProjection):

	def __init__(self):
	
		self.phi1 = math.radians(30)
		self.phi2 = math.radians(60)
		self.precompute_values()
			
	def get_coords(self, x, y):
		
		r = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(y)/2) , self.n)
		new_x = r * math.sin(self.n*(math.radians(x)))	
		new_y = self.r0 - r * math.cos(self.n * (math.radians(x)))					
		
		return 7*new_x, 7*new_y
	
	def set_phi(self, phi1, phi2):
		self.phi1 = math.radians(phi1)
		self.phi2 = math.radians(phi2)
		self.precompute_values()

		
	def precompute_values(self):
		print "precomputing values: phi1=" + str(self.phi1) + " phi2=" + str(self.phi2)
		self.n = (math.log(math.cos(self.phi1) * mpmath.sec(self.phi2)))/	math.log(math.tan(math.pi/4 + self.phi2/2) * mpmath.cot(math.pi/4 + self.phi1/2))
		self.F = (math.cos(self.phi1) * math.tan(math.pi / 4 + self.phi1 / 2))/ self.n
		self.r0 = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(self.phi1)/2 ), self.n)

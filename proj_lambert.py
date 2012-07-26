from proj_generic import GenericProjection
import math
import mpmath

class LambertProjection(GenericProjection):

	def __init__(self):
	
		self.phi1 = math.radians(30)
		self.phi2 = math.radians(60)
		self.projection_type = self.ProjectionType.Conic
		self.precompute_values()
		
			
	def get_coords(self, x, y):
		
		val = math.pi/4 + y/2
		if round(val,4) == 0.0000:
			val = 0.00001
		if round(val, 4) == 1.5708:
			val = 1.5707
		r = self.F * math.pow( mpmath.cot(val) , self.n)
		new_x = r * math.sin(self.n*x)	
		new_y = self.r0 - r * math.cos(self.n * x)					
		
		return 7*new_x, 7*new_y
	
	def set_phi(self, phi1, phi2):
		self.phi1 = math.radians(phi1)
		self.phi2 = math.radians(phi2)
		self.precompute_values()

		
	def precompute_values(self):
		self.n = (math.log(math.cos(self.phi1) * mpmath.sec(self.phi2)))/	math.log(math.tan(math.pi/4 + self.phi2/2) * mpmath.cot(math.pi/4 + self.phi1/2))
		self.F = (math.cos(self.phi1) * math.tan(math.pi / 4 + self.phi1 / 2))/ self.n
		self.r0 = self.F * math.pow( mpmath.cot(math.pi/4 + math.radians(self.phi1)/2 ), self.n)

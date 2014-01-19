import math

import mpmath

from projections.proj_generic import GenericProjection


class LambertProjection(GenericProjection):

	def __init__(self):
	
		self.phi1 = math.radians(30)
		self.phi2 = math.radians(60)
		self.projection_type = self.ProjectionType.Conic
		self.precompute_values()
#		self.last_x = 0
#		self.last_y = 0
		
			
	def get_coords(self, x, y):
		
		val = math.pi/4 + y/2

		if round(val,4) == 0.0000:
			val = 0.00001
		elif round(val, 4) >= 1.5708:
			val = 1.5707
		elif round(val, 4) < 0:
			return (-10000, -10000)
		
		r = self.F * math.pow( mpmath.cot(val) , self.n)
		new_x = r * math.sin(self.n*x)	
		new_y = - r * math.cos(self.n * x)					
		
		return 80*new_x, 80*new_y
	
	def set_phi(self, phi1, phi2):
		self.phi1 = math.radians(phi1)
		self.phi2 = math.radians(phi2)
		self.precompute_values()

		
	def precompute_values(self):
		self.n = (math.log(math.cos(self.phi1) * mpmath.sec(self.phi2)))/	math.log(math.tan(math.pi/4 + self.phi2/2) * mpmath.cot(math.pi/4 + self.phi1/2))
		if self.n == 0.0000:
			self.n = 0.00001
		self.F = (math.cos(self.phi1) * math.pow(math.tan(math.pi / 4 + self.phi1 / 2), self.n))/ self.n
		#self.r0 = self.F * math.pow( mpmath.cot(math.pi/4 + self.last_y	/2 ), self.n)

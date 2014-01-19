import math

from projections.proj_generic import GenericProjection


class AlbersProjection(GenericProjection):

	def __init__(self):
	
		self.phi1 = math.radians(30)
		self.phi2 = math.radians(60)
		self.projection_type = self.ProjectionType.Conic
		self.precompute_values()
		
			
	def get_coords(self, x, y):
		
		rho = math.sqrt(self.C - (2 * self.n * math.sin(y))) / self.n
		theta = self.n * x
		new_x = rho * math.sin(theta)	
		new_y = -rho * math.cos(theta)
		den = (math.degrees(self.phi2) + math.degrees(self.phi1))
		if den == 0:
			den = 0.00001
		
		return 70 * new_x, 70 * new_y - 50 + 8000 / den
	
	def set_phi(self, phi1, phi2):
		self.phi1 = phi1
		self.phi2 = phi2
		self.precompute_values()

		
	def precompute_values(self):
		self.n = 0.5 * (math.sin(self.phi1) + math.sin(self.phi2))
		if self.n == 0:
			self.n = 0.00001
		self.C = math.pow(math.cos(self.phi1), 2) + 2 * self.n * math.sin(self.phi1)

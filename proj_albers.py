from proj_generic import GenericProjection
import math

class AlbersProjection(GenericProjection):

	def __init__(self):
	
		self.phi1 = math.radians(30)
		self.phi2 = math.radians(60)
		self.projection_type = self.ProjectionType.Conic
		self.precompute_values()
		
			
	def get_coords(self, x, y):
		
		rho = math.sqrt(self.C - (2 * self.n * math.sin(y))) / self.n
		theta = self.n * x
		new_x = 10 * rho * math.sin(theta)	
		new_y = 10 * -rho * math.cos(theta)					
		
		return 7 * new_x, 7 * new_y
	
	def set_phi(self, phi1, phi2):
		self.phi1 = phi1
		self.phi2 = phi2
		print "phi1=" + str(self.phi1) + " phi2=" + str(self.phi2)
		self.precompute_values()

		
	def precompute_values(self):
		self.n = 0.5 * (math.sin(self.phi1) + math.sin(self.phi2))
		if self.n == 0:
			self.n = 0.00001
		self.C = math.pow(math.cos(self.phi1), 2) + 2 * self.n * math.sin(self.phi1)
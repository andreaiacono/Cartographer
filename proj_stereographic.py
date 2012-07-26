from proj_generic import GenericProjection
import math


class StereographicProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal
		self.central_lat = math.radians(30)
		self.central_lon = math.radians(60)


	def get_coords(self, x, y):
		cos_y = math.cos(y)
		den= 1 + cos_y * math.cos(x)
		if den == 0:
			den = 0.00001
		k = 120 / den
		new_x = k * cos_y * math.sin(x)
		new_y = k * math.sin(y) 

		return new_x, new_y
	
	def set_central_coords(self, lat, lon):
		
		self.central_lat = math.radians(lat)
		self.central_lon = math.radians(lon) 
		
		
from proj_generic import GenericProjection
import math


class StereographicProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal
		self.central_lat = math.radians(30)
		self.central_lon = math.radians(60)


	def get_coords(self, x, y):
		cos_y = math.cos(math.radians(y))
		k = 120 / (1 + cos_y * math.cos(math.radians(x)))
		new_x = k * math.cos(math.radians(y)) * math.sin(math.radians(x))
		new_y = k * math.sin(math.radians(y)) 

		return new_x, new_y
	
	def set_central_coords(self, lat, lon):
		
		self.central_lat = math.radians(lat)
		self.central_lon = math.radians(lon) 
		
		
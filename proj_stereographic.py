from proj_generic import GenericProjection
import math


class StereographicProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal
		self.central_lat = math.radians(30)
		self.central_lon = math.radians(60)


	def get_coords(self, x, y):
		
		cos_y = math.cos(math.radians(y))
		k = 200 / (1 + math.sin(self.central_lat)) * math.sin(math.radians(y)) + math.cos(self.central_lat) * cos_y * math.cos(math.radians(x) - self.central_lon)
		return k * cos_y * math.sin(math.radians(x) - self.central_lon),  k * ( math.cos(self.central_lat) * math.sin(math.radians(y)) - math.sin(self.central_lat) * cos_y * math.cos(math.radians(x) - self.central_lon))
	
	def set_central_coords(self, lat, lon):
		
		self.central_lat = math.radians(lat)
		self.central_lon = math.radians(lon) 
		
		
from proj_generic import GenericProjection
import math


class StereographicProjection(GenericProjection):
	
	def __init__(self):
		self.projection_type = self.ProjectionType.Azimuthal
		self.central_lat = math.radians(30)
		self.central_lon = math.radians(60)


	def get_coords(self, x, y):
		
		# if (x < -90 or x > 90):
		#	return -10000, -10000
		
#		cos_y = math.cos(math.radians(y))
#		k = 200 / (1 + math.sin(self.central_lat)) * math.sin(math.radians(y)) + math.cos(self.central_lat) * cos_y * math.cos(math.radians(x) - self.central_lon)
#		new_x = k * cos_y * math.sin(math.radians(x) - self.central_lon)
#		new_y = k * ( math.cos(self.central_lat) * math.sin(math.radians(y)) - math.sin(self.central_lat) * cos_y * math.cos(math.radians(x) - self.central_lon))
		
		new_x = 30 * math.tan((math.pi/4 - math.radians(y)/2) * math.sin(math.radians(x))) 
		new_y = -30 * math.tan((math.pi/4 - math.radians(y)/2) * math.cos(math.radians(x)))
		return new_x, new_y
	
	def set_central_coords(self, lat, lon):
		
		self.central_lat = math.radians(lat)
		self.central_lon = math.radians(lon) 
		
		
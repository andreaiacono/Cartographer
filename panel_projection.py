import lib.euclid
import lib.shapefile
import math
import wx




class ProjectionPanel(wx.Panel):

	def __init__(self, parent, window_id):
		sty = wx.NO_BORDER
		wx.Window.__init__(self, parent, window_id, style=sty)
		self.parent = parent
		shapeReader = lib.shapefile.Reader("shapes/110m_land.shp")
		self.shapes = shapeReader.shapes()
		wx.EVT_PAINT(self, self.OnPaint)
		wx.EVT_SIZE(self, self.OnSize)
		self.lastWidth = 0
		self.lastHeight = 0
		self.rotationx = 0.0
		self.rotationy = 0.0
		self.rotationz = 0.0
		self.projection = None
		self.proj_width = 2000
		self.proj_height = 2000
		self.last_lat = None
		self.last_lon = None
		self.resolution = 15
		
		
#		self.new_lat = []
#		self.new_lon = []
#
#		self.latlon_to_cartesian_x = [[0.0 for col in range(-180,180)] for row in range(-90,90)]
#		self.latlon_to_cartesian_y = [[0.0 for col in range(-180,180)] for row in range(-90,90)]
#		self.latlon_to_cartesian_z = [[0.0 for col in range(-180,180)] for row in range(-90,90)]
#		
#		for lon in range (-180, 180):
#			for lat in range (-90, 90):
#				
#				self.latlon_to_cartesian_x[lat][lon] = math.cos(math.radians(lat)) * math.cos(math.radians(lon))  
#				self.latlon_to_cartesian_y[lat][lon] = math.cos(math.radians(lat)) * math.sin(math.radians(lon))
#				self.latlon_to_cartesian_z[lat][lon] = math.sin(math.radians(lat))
#				
#		print "finished lat to cart"
#
#		self.cartesian_to_lat = [[[0.0 for x in range(-180,180)] for y in range(-180,180)] for z in range(-180,180)] 
#		self.cartesian_to_lon = [[[0.0 for x in range(-180,180)] for y in range(-180,180)] for z in range(-180,180)]
#		
#		for x in range (-180, 180):
#			for y in range (-180, 180):
#				for z in range (-180, 180):
#					
#					try:
#						self.cartesian_to_lat[x][y][z] = math.asin(math.radians(z/float(z)))  
#						self.cartesian_to_lon[x][y][z] = math.atan2(math.radians(y), math.radians(x))
#					except:
#						pass
#		print "finished cart to lat"
		
#		for lat in range(-9, 9):
#			for lon in range (-18, 18):
#				for rx in range(-18, 18):
#					for ry in range(-18, 18):
#						for rz in range(-18, 18):
#						
#							x, y, z = self.latlong_to_cartesian(lat/float(10), lon/float(10))
#							x, y, z = self.apply_rotation(rx*10, ry*10, rz*10, x, y, z)
#							new_lat_tmp, new_lon_tmp = self.cartesian_to_latlong(x, y, z)
#							self.new_lat.append(new_lat_tmp)
#							self.new_lon.append(new_lon_tmp)
#			print "lat=" + str(lat)
				
		
	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		self.drawProjection(dc)


	def OnSize(self, event):
		self.width, self.height = self.GetSizeTuple()
		if (self.width != self.lastWidth or self.height != self.lastHeight):
			
			if (self.width > self.height):
				self.mf = self.height / float(180)
				self.tx = self.mf * 180 + (self.width - self.mf * 360) / 2
				self.proj_width = self.width - self.mf * 360 - 10
				self.proj_height = self.height - 10
				self.ty = self.mf * 90
			else:
				self.mf = self.width / float(360)
				self.tx = self.mf * 180 
				self.ty = self.mf * 90 + (self.height - self.mf * 180) / 2
				self.proj_width = self.width
				self.proj_height = self.height - self.mf * 180
			dc = wx.PaintDC(self)
			self.drawProjection(dc)
			
		self.lastWidth = self.width
		self.lastHeight = self.height


	def drawParallel(self, latitude, dc):
		
		last_lat = None
		last_lon = None

		for point in range (-45, 45):
	
			if (point % self.resolution == 0):
				lon = point * 8
				lat, lon = self.transform_coords(latitude, lon)
				
				if (last_lat != None):
	
					x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, self.rotationx, lon, self.rotationy, lat, lon, self.proj_width, self.proj_height))
					last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(last_lat, self.rotationx, last_lon, self.rotationy, last_lat, last_lon, self.proj_width, self.proj_height))
					
					if (math.fabs(x - last_x) < self.proj_width/2):
						dc.DrawLine(x + self.tx, y + self.ty, last_x + self.tx, last_y + self.ty)
								
				last_lat = lat
				last_lon = lon


	def drawProjection(self, dc):
		dc.BeginDrawing()
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.DrawRectangle(0, 0, self.width, self.height)

		# draws meridian and parallels
		dc.SetPen(wx.Pen("light gray", 1))
		for meridian in range (-6, 6):
			
			self.last_lat = None
			self.last_lon = None
			
			for point in range (-45, 45):
				
				if (point % self.resolution == 0):
					lon = meridian * 15
					lat = point * 4
					lat, lon = self.transform_coords(lat, lon)
					
					if (self.last_lat != None):
						x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, self.rotationx, lon, self.rotationy, lat, lon, self.proj_width, self.proj_height))
						last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(self.last_lat, self.rotationx, self.last_lon, self.rotationy, self.last_lat, self.last_lon, self.proj_width, self.proj_height))
						
						if (math.fabs(y - last_y) < self.proj_height/2 and math.fabs(x - last_x) < self.proj_width/2):
							dc.DrawLine(x + self.tx, y + self.ty, last_x + self.tx, last_y + self.ty)
					
					self.last_lat = lat
					self.last_lon = lon
	
	
		for parallel in range (-6, 7):

			# the equator parallel is in a darker grey
			if (parallel == 0):
				dc.SetPen(wx.Pen("black", 1))
			else:
				dc.SetPen(wx.Pen("light gray", 1))

			self.drawParallel(parallel*15, dc)
			
			
		dc.SetPen(wx.Pen("gray", 1))	
		for tropics in (-23.5, 23.5):

			self.drawParallel(tropics, dc)
				
				
		# draws the shapes of lands
		dc.SetPen(wx.Pen("blue", 1))		
		for shape in self.shapes:
			for i in range(len(shape.parts)):
				startIndex = shape.parts[i]
				if (i < len(shape.parts) - 1):
					endIndex = shape.parts[i + 1] - 1
				else:
					endIndex = len(shape.points) - 1

				rx1, ry1 = self.transform_coords(shape.points[startIndex][1], -shape.points[startIndex][0])
				start_x, start_y = tuple(val * self.mf for val in self.projection.get_coords(rx1, self.rotationx, ry1, self.rotationy, shape.points[startIndex][1], shape.points[startIndex][0], self.proj_width, self.proj_height))
				
				for point in range(startIndex+1, endIndex):
					
					if (point % self.resolution == 0):
						
						rx2, ry2 = self.transform_coords(shape.points[point + 1][1], -shape.points[point + 1][0]) 
						end_x, end_y = tuple(val * self.mf for val in self.projection.get_coords(rx2, self.rotationx, ry2, self.rotationy, shape.points[point + 1][1], shape.points[point + 1][0], self.proj_width, self.proj_height))
					
						if (math.fabs(start_x - end_x) < self.proj_width / 4 and math.fabs(start_y - end_y) < self.proj_height / 4):
							dc.DrawLine(start_x + self.tx, start_y + self.ty, end_x + self.tx, end_y + self.ty)
							
						start_x, start_y = end_x, end_y
						
		dc.EndDrawing
		
	def transform_coords(self, lat, lon):
		
		
		x, y, z = self.latlong_to_cartesian(lat, lon)
#		x = self.latlon_to_cartesian_x[int(lat)][int(lon)]
#		y = self.latlon_to_cartesian_y[int(lat)][int(lon)]
#		z = self.latlon_to_cartesian_z[int(lat)][int(lon)]
		
		x, y, z = self.apply_rotation(self.rotationx, self.rotationy, self.rotationz, x, y, z)
		
		new_lat, new_lon = self.cartesian_to_latlong(x, y, z)
		
#		new_lat = self.cartesian_to_lat[int(x)][int(y)][int(z)]
#		new_lon = self.cartesian_to_lon[int(x)][int(y)][int(z)]
		
		#print "old=(" + str(lat) + "," + str(lon) + " new=(" + str(new_lat) + "," + str(new_lon) + ")"
		
		#return math.degrees(-self.new_lon[int(lon/10)]), math.degrees(-self.new_lat[int(lat/10)])*80
		return math.degrees(-new_lon), math.degrees(-new_lat)*80
	
	
	def latlong_to_cartesian(self, lat, lon):
		x = math.cos(math.radians(lat)) * math.cos(math.radians(lon))
		y = math.cos(math.radians(lat)) * math.sin(math.radians(lon))
		z = math.sin(math.radians(lat))
		
		return x, y, z
	

	def cartesian_to_latlong(self, x, y, z):
		lat = math.asin(math.radians(z))
		lon = math.atan2(math.radians(y), math.radians(x))
		
		return lat, lon

	def apply_rotation(self, rx, ry, rz, x, y, z):
		
		m = lib.euclid.Matrix4().new_rotate_euler(math.radians(rz), math.radians(rx), math.radians(ry))
		v = lib.euclid.Vector3(x, y, z)
		
		rv = m * v
		return rv.x, rv.y, rv.z
		
		#return x,y,z

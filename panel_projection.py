import lib.shapefile
import math
import wx
import lib.euclid




class Projection(wx.Window):

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


	def drawProjection(self, dc):
		dc.BeginDrawing()
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.DrawRectangle(0, 0, self.width, self.height)

		# draws meridian and parallels
		dc.SetPen(wx.Pen("gray", 1))
		for meridian in range (-6, 6):
			
			self.last_lat = None
			self.last_lon = None
			
			for point in range (-90, 91):
				lon = meridian * 30
				lat = point
				lat, lon = self.transform_coords(lat, lon)
				
				if (self.last_lat != None):
					x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, self.rotationx, lon, self.rotationy, lat, lon, self.proj_width, self.proj_height))
					last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(self.last_lat, self.rotationx, self.last_lon, self.rotationy, self.last_lat, self.last_lon, self.proj_width, self.proj_height))
					
					if (math.fabs(y - last_y) < self.proj_height/2 and math.fabs(x - last_x) < self.proj_width/2):
						dc.DrawLine(x + self.tx, y + self.ty, last_x + self.tx, last_y + self.ty)
				
				self.last_lat = lat
				self.last_lon = lon

	
		for parallel in range (-6, 7):

			self.last_lat = None
			self.last_lon = None
			
			for point in range (-179, 181):

				lon = point
				lat = parallel*15
				lat, lon = self.transform_coords(lat, lon)
				
				
				if (self.last_lat != None):
				
					# the equator parallel is in a darker grey
					if (parallel == 0):
						dc.SetPen(wx.Pen("black", 1))
					else:
						dc.SetPen(wx.Pen("gray", 1))
				
					x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, self.rotationx, lon, self.rotationy, lat, lon, self.proj_width, self.proj_height))
					last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(self.last_lat, self.rotationx, self.last_lon, self.rotationy, self.last_lat, self.last_lon, self.proj_width, self.proj_height))
					
					if (math.fabs(x - last_x) < self.proj_width/2):
						dc.DrawLine(x + self.tx, y + self.ty, last_x + self.tx, last_y + self.ty)
				
				
				self.last_lat = lat
				self.last_lon = lon
			
			
				
				
				
		# draws the shapes of lands
		dc.SetPen(wx.Pen("blue", 1))		
		for shape in self.shapes:
			for i in range(len(shape.parts)):
				startIndex = shape.parts[i]
				if (i < len(shape.parts) - 1):
					endIndex = shape.parts[i + 1] - 1
				else:
					endIndex = len(shape.points) - 1

				for point in range(startIndex, endIndex):
					
					rx1, ry1 = self.transform_coords(shape.points[point][1], -shape.points[point][0]) 
					rx2, ry2 = self.transform_coords(shape.points[point + 1][1], -shape.points[point + 1][0]) 
				
					start_x, start_y = tuple(val * self.mf for val in self.projection.get_coords(rx1, self.rotationx, ry1, self.rotationy, shape.points[point][1], shape.points[point][0], self.proj_width, self.proj_height))
					end_x, end_y = tuple(val * self.mf for val in self.projection.get_coords(rx2, self.rotationx, ry2, self.rotationy, shape.points[point + 1][1], shape.points[point + 1][0], self.proj_width, self.proj_height))
					
					if (math.fabs(start_x - end_x) < self.proj_width / 4 and math.fabs(start_y - end_y) < self.proj_height / 4):
						dc.DrawLine(start_x + self.tx, start_y + self.ty, end_x + self.tx, end_y + self.ty)

		dc.EndDrawing
		
	def transform_coords(self, lat, lon):
		
		x, y, z = self.latlong_to_cartesian(lat, lon)
		x, y, z = self.apply_rotation(self.rotationx, self.rotationy, self.rotationz, x, y, z)
		new_lat, new_lon = self.cartesian_to_latlong(x, y, z)
		
		#print "old=(" + str(lat) + "," + str(lon) + " new=(" + str(new_lat) + "," + str(new_lon) + ")"
		
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

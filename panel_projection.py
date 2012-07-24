#coding=UTF-8
import lib.euclid
import lib.shapefile
import math
import wx




class ProjectionPanel(wx.Panel):


	
	def __init__(self, parent, window_id, cartographer):
		sty = wx.NO_BORDER
		wx.Window.__init__(self, parent, window_id, style=sty)
		self.parent = parent
		self.cartographer = cartographer
		
		countriesShapeReader = lib.shapefile.Reader("shapes/ne_110m_admin_0_countries.shp")
		self.countries = countriesShapeReader.shapes()
		
		continentsShapeReader = lib.shapefile.Reader("shapes/110m_land.shp")
		self.continents = continentsShapeReader.shapes()
		
		hiResShapeReader = lib.shapefile.Reader("shapes/10m_land.shp")
		self.hires = hiResShapeReader.shapes()
		
		self.set_shapes(0)
		
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
		
		self.resolution_scale = 25

		self.set_resolution(self.resolution_scale / 2)
		self.set_grid_resolution(self.resolution_scale / 2)
		self.set_paint_grid(True)
		self.set_paint_grid_specials(True)
		self.set_paint_frame(True)
		
		self.zoom = 360
		
		self.posx = 0
		self.posy = 0
		self.posz = 0
		self.x = 0
		self.y = 0
		self.z = 0
		self.lastx = 0
		self.lasty = 0
		self.lastz = 0
		
		self.parallel_degrees = 15
		self.meridian_degrees = 15

				
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)


	def OnMouseDown(self, evt):
		self.CaptureMouse()
		self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
		self.z = self.lastz = self.y

	def OnMouseUp(self, evt):
		self.ReleaseMouse()

	def OnMouseMotion(self, evt):
		if evt.Dragging() and (evt.LeftIsDown() or evt.RightIsDown()):
			self.x, self.y = evt.GetPosition()
			
			if evt.RightIsDown():
				self.z = self.y
				self.posz += self.z - self.lastz
				self.lastz = self.z
			else:
				self.posx -= self.x - self.lastx
				self.posy += self.y - self.lasty
				self.lastx = self.x
				self.lasty = self.y

			self.cartographer.rotationx = self.posx % 360
			self.cartographer.rotationy = self.posy % 360
			self.cartographer.rotationz = self.posz % 360
			self.cartographer.refresh()
			
			self.Refresh(False)

	
		
		
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
			
	def set_paint_grid_specials(self, paint_grid_specials):
		self.paint_grid_specials = paint_grid_specials
	
	def set_paint_grid(self, paint_grid):
		self.paint_grid = paint_grid
	
	def set_paint_frame(self, paint_frame):
		self.paint_frame = paint_frame
	
	def set_resolution(self, resolution):		
		self.resolution = resolution

	def set_grid_resolution(self, grid_resolution):		
		self.grid_resolution = grid_resolution
		
	def set_shapes(self, shape_type):
		
		self.shape_type = shape_type
		
		if shape_type == 0:
			self.shapes = self.continents
		elif shape_type == 1:
			self.shapes = self.countries
		else:
			self.shapes = self.hires


	def refresh_window(self):
		dc = wx.PaintDC(self)
		self.width, self.height = self.GetSizeTuple()
		self.draw_projection(dc, self.width, self.height)

		
	def OnPaint(self, event):
		self.refresh_window()

	def OnSize(self, event):
		
		self.compute_size()
		self.refresh_window()
		
	def compute_size(self):	
		print "calling compute"
		self.width, self.height = self.GetSizeTuple()
		if (self.width != self.lastWidth or self.height != self.lastHeight):
			
			visible_height = self.zoom
			visible_width = self.zoom
			
			if self.width > 2 * self.height:
				self.mf = self.height / float(visible_height)
				self.tx = self.mf * visible_width / 2 + (self.width - self.mf * visible_width) / 2
				self.proj_width = self.width - self.mf * visible_width - 10
				self.proj_height = self.height - 10
				self.ty = self.mf * visible_height / 2
			else:
				self.mf = self.width / float(visible_width)
				self.tx = self.mf * visible_width / 2 
				self.ty = self.mf * visible_height / 2 + (self.height - self.mf * visible_height) / 2
				self.proj_width = self.width
				self.proj_height = self.height - self.mf * visible_height
			
		self.lastWidth = self.width
		self.lastHeight = self.height


	def draw_parallel(self, latitude, width, height, transform_coords, dc):
		
		#dc.SetPen(wx.Pen("green", 1))
		
		# computes the first point
		lat, lon = self.transform_coords(latitude, -180) if transform_coords else tuple(latitude, -180)
		last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
		last_x += self.tx
		last_y += self.ty
		

		for point in range (-89, 89):
	
			if (point % self.resolution_scale >= self.grid_resolution - 1):
			
				lat, lon = self.transform_coords(latitude, point * 2) if transform_coords else tuple(latitude, point * 2)
				x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
				x += self.tx
				y += self.ty
	
				if (math.fabs(y - last_y) < self.proj_height / 3 and math.fabs(x - last_x) < self.proj_width / 3):
					dc.DrawLine(x, y, last_x, last_y)

				last_x, last_y = x, y
		
		# draws the last line
		lat, lon = self.transform_coords(latitude, 180) if transform_coords else tuple(latitude, 180)
		x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
		x += self.tx
		y += self.ty
		dc.DrawLine(x, y, last_x, last_y)

	def draw_meridian(self, longitude, width, height, transform_coords, dc):
		
		#dc.SetPen(wx.Pen("red", 1))
		
		# computes the first point
		lat, lon = self.transform_coords(-180, longitude) if transform_coords else tuple(-180, longitude) 
		last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
		last_x += self.tx
		last_y += self.ty
		
		for point in range (-89, 89):
			if (point % self.resolution_scale >= self.grid_resolution - 1):
				
				lat, lon = self.transform_coords(point * 2, longitude) if transform_coords else tuple(point * 2, longitude)
				x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
				x += self.tx
				y += self.ty
		
				if (math.fabs(y - last_y) < self.proj_height / 3 and math.fabs(x - last_x) < self.proj_width / 3):
					dc.DrawLine(x, y, last_x, last_y)
					
				last_x, last_y = x, y

		# draws the last line
		lat, lon = self.transform_coords(180, longitude) if transform_coords else tuple(180, longitude) 
		x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
		x += self.tx
		y += self.ty
		dc.DrawLine(x, y, last_x, last_y)
		

	def draw_projection(self, dc, width, height):
		dc.BeginDrawing
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.DrawRectangle(0, 0, width, height)
		
		print "x=" + str(self.rotationx) + " y=" + str(self.rotationy) + " z=" + str(self.rotationz) + " tx=" + str(self.tx) + " ty=" + str(self.ty)

		# draws meridian and parallels
		if (self.paint_grid):
			
			dc.SetPen(wx.Pen("light gray", 1))
			meridian_number = 360 / self.meridian_degrees
			for meridian in range (1, int(meridian_number)):
				self.draw_meridian(meridian *  self.meridian_degrees, width, height, True, dc)
			
			parallel_number = 360 / self.parallel_degrees
			for parallel in range (1, int(parallel_number)):
				
				self.draw_parallel(180 - parallel *  self.parallel_degrees, width, height, True, dc)

		# draws special parallels (arctic/antarctic circles and tropics)			
		if (self.paint_grid_specials):
			dc.SetPen(wx.Pen("dark gray", 1))
			for tropics in (-66.5, -23.5, 23.5, 66.5):
	
				self.draw_parallel(tropics, width, height, True, dc)

			dc.SetPen(wx.Pen("black", 1))
			self.draw_parallel(0, width, height, True, dc)
				
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
				start_x, start_y = tuple(val * self.mf for val in self.projection.get_coords(rx1, ry1))
				
				for point in range(startIndex + 1, endIndex):
					
					if (point % self.resolution_scale >= self.resolution - 1):
						
						rx2, ry2 = self.transform_coords(shape.points[point + 1][1], -shape.points[point + 1][0]) 
						end_x, end_y = tuple(val * self.mf for val in self.projection.get_coords(rx2, ry2))
					
						if (math.fabs(start_x - end_x) < width / 10 and math.fabs(start_y - end_y) < height / 10):
							dc.DrawLine(start_x + self.tx, start_y + self.ty, end_x + self.tx, end_y + self.ty)
							
						start_x, start_y = end_x, end_y
				
		# draws the frame 
		if self.paint_frame:
			self.draw_frame(width, height, dc)
			
		dc.EndDrawing
		
		latitude, longitude = self.transform_coords(0, 0)
		lat = str(round(latitude, 4))
		lon = str(round(longitude, 4))
		self.cartographer.SetStatusText("Map is centered on " + lat + "°  -  " + lon + "°")
		
	#	draws a frame of the map 
	def draw_frame(self, width, height, dc):
		
		self.projection.draw_frame(width, height, self, dc)
		
		
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
		return math.degrees(-new_lon), math.degrees(-new_lat) * 90
	
	
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

	
	def set_coordinates(self, rotationx, rotationy, rotationz):
		self.rotationx = rotationx
		self.rotationy = rotationy
		self.rotationz = rotationz
	
	def set_zoom(self, value):
		self.zoom = value
		self.compute_size()
	
	def set_parallel_degrees(self, value):
		self.parallel_degrees = value

	def set_meridian_degrees(self, value):
		self.meridian_degrees = value

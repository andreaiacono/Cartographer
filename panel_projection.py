import lib.shapefile
import math
import proj_mercator
import wx
import proj_generic
import proj_azimuthal_orthographic

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
		self.centerx = 0
		self.centery = 0
		#self.projection = proj_generic.GenericProjection()
		#self.projection = proj_mercator.MercatorProjection()
		self.projection = proj_azimuthal_orthographic.AzimuthalOrthographicProjection()
		self.proj_width = 2000
		self.proj_height = 2000

	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		self.drawProjection(dc)


	def OnSize(self, event):
		self.width, self.height = self.GetSizeTuple()
		if (self.width != self.lastWidth or self.height != self.lastHeight):
			if (self.width > self.height):
				self.mf = self.height / float(180)
				self.tx = self.mf * 180 + (self.width - self.mf * 360)/2
				self.proj_width = self.width - self.mf * 360 -10
				self.proj_height = self.height -10
				self.ty = self.mf * 90
			else:
				self.mf = self.width / float(360)
				self.tx = self.mf * 180 
				self.ty = self.mf * 90 + (self.height - self.mf * 180)/2
				self.proj_width = self.width
				self.proj_height = self.height - self.mf * 180
			dc = wx.PaintDC(self)
			self.drawProjection(dc)
			
			print "prjw= " + str(self.width) + " projh=" + str(self.height)
		self.lastWidth = self.width
		self.lastHeight = self.height


	def drawProjection(self, dc):
		dc.BeginDrawing()
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.DrawRectangle(0,0,self.width, self.height)
		dc.SetPen(wx.Pen("blue", 1))
		for shape in self.shapes:
			for i in range(len(shape.parts)):
				startIndex = shape.parts[i]
				if (i<len(shape.parts)-1):
					endIndex = shape.parts[i+1]-1
				else:
					endIndex = len(shape.points)-1

				for point in range(startIndex,endIndex):
##					print "p=" + str(shape.points[point][0])
					coord_x1 = ((shape.points[point][0] + self.centerx) % 360 - 180) * self.mf
					coord_y1 = ((-shape.points[point][1] + self.centery) % 180 - 90) * self.mf
					
					coord_x2 = ((shape.points[point+1][0] + self.centerx) % 360 - 180 )* self.mf
					coord_y2 = ((-shape.points[point+1][1] + self.centery) % 180 - 90) * self.mf
					
					start_x = self.projection.get_x_coord(coord_x1, self.centerx, coord_y1, self.centery, self.proj_width, self.proj_height)
					start_y = self.projection.get_y_coord(coord_x1, self.centerx, coord_y1, self.centery, self.proj_width, self.proj_height)
					end_x = self.projection.get_x_coord(coord_x2, self.centerx, coord_y2, self.centery, self.proj_width, self.proj_height)
					end_y = self.projection.get_y_coord(coord_x2, self.centerx, coord_y2, self.centery, self.proj_width, self.proj_height)
					
					if (math.fabs(start_x - end_x) < self.proj_width/4 and math.fabs(start_y - end_y) < self.proj_height/4):
						dc.DrawLine(start_x + self.tx, start_y + self.ty, end_x + self.tx, end_y + self.ty)

		dc.EndDrawing


##class ProjectionPanel(wx.Panel):
##
##	def __init__(self, parent, id):
##		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize)
##		self.drawingarea = Projection(self, -1)
##		self.SetAutoLayout(True)
##		gap = 5
##		lc = wx.LayoutConstraints()
##		lc.top.SameAs(self, wx.Top, gap)
##		lc.left.SameAs(self, wx.Left, gap)
##		lc.right.SameAs(self, wx.Width, gap)
##		lc.bottom.SameAs(self, wx.Bottom, gap)
##		self.drawingarea.SetConstraints(lc)

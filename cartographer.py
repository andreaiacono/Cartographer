import panel_position
import panel_projection
import proj_azimuthal_orthographic
import proj_lambert
import proj_mercator
import proj_peters
import wx
import panel_configuration

class CartographerFrame(wx.Frame):


	
	def __init__(self):
		wx.Frame.__init__(self, None, -1, "Cartographer", wx.DefaultPosition, wx.Size(800,600))
		wx.EVT_CLOSE(self, self.OnQuit)
		menu_file = wx.Menu()
		
		ID_INFO = wx.NewId()
		menu_file.Append(ID_INFO, "&Info", "Shows info")
		wx.EVT_MENU(self, ID_INFO, self.OnInfo)
		menu_file.AppendSeparator()
		
		ID_QUIT = wx.NewId()
		menu_file.Append(ID_QUIT, "&Quit", "Quit Cartographer")
		wx.EVT_MENU(self, ID_QUIT, self.OnQuit)
		
		menu_bar = wx.MenuBar()
		menu_bar.Append(menu_file, "&File");
		
		menu_proj = wx.Menu()
		
		ID_PROJ_MERCATOR = wx.NewId()
		menu_proj.Append(ID_PROJ_MERCATOR, "&Mercator", "Shows a Mercator projection")
		wx.EVT_MENU(self, ID_PROJ_MERCATOR, self.SetMercatorProjection)
		
		ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC = wx.NewId()
		menu_proj.Append(ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC, "&Azimuthal Orthographic", "Shows an azimuthal orthographic projection")
		wx.EVT_MENU(self, ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC, self.SetAzimuthalOrtographicProjection)
		
		ID_PROJ_PETERS = wx.NewId()
		menu_proj.Append(ID_PROJ_PETERS, "&Peters", "Shows a Peters projection")
		wx.EVT_MENU(self, ID_PROJ_PETERS, self.SetPetersProjection)
		
		ID_PROJ_LAMBERT = wx.NewId()
		menu_proj.Append(ID_PROJ_LAMBERT, "&Lambert", "Shows a Lambert projection")
		wx.EVT_MENU(self, ID_PROJ_LAMBERT, self.SetLambertProjection)
		
		menu_bar.Append(menu_proj, "&Projections");
		

		self.SetMenuBar(menu_bar)
		self.CreateStatusBar()
		self.SetStatusText("Ready")
		self.rotationx = 0
		self.rotationy = 180
		self.rotationz = 0

		top_splitter = wx.SplitterWindow(self)
		settings_splitter = wx.SplitterWindow(top_splitter)
		
		self.configurationPanel = panel_configuration.ConfigurationPanel(settings_splitter, -1)
		self.positionCanvas = panel_position.PositionCanvas(settings_splitter, self)
		settings_splitter.SplitVertically(self.positionCanvas, self.configurationPanel)
		settings_splitter.SetSashGravity(0.5)

		self.projectionPanel = panel_projection.ProjectionPanel(top_splitter, -1)
		self.projectionPanel.projection = proj_lambert.LambertProjection() 
		top_splitter.SplitHorizontally(settings_splitter, self.projectionPanel)
		top_splitter.SetSashGravity(0.3)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(top_splitter, 1, wx.EXPAND)
		self.SetSizer(sizer)
		
		

	def OnInfo(self, event):
		wx.MessageBox("Cartographer \n\nwritten \n\nby Andrea Iacono\n\nandrea.iacono@gmail.com")

	def OnQuit(self, event):
		self.Destroy()

	def refresh(self):
		self.projectionPanel.rotationx = self.rotationx
		self.projectionPanel.rotationy = self.rotationy
		self.projectionPanel.rotationz = self.rotationz
		self.projectionPanel.Refresh()
		
		
	def SetMercatorProjection(self, event):
		self.projectionPanel.projection = proj_mercator.MercatorProjection()
		self.refresh()
		
	def SetPetersProjection(self, event):
		self.projectionPanel.projection = proj_peters.PetersProjection()
		self.refresh()
	
	def SetLambertProjection(self, event):
		self.projectionPanel.projection = proj_lambert.LambertProjection()
		self.refresh()
		
	def SetAzimuthalOrtographicProjection(self, event):
		self.projectionPanel.projection = proj_azimuthal_orthographic.AzimuthalOrthographicProjection()
		self.refresh()

class CartographerApplication(wx.App):
	
	def OnInit(self):
		frame = CartographerFrame()
		frame.Show(True)
		self.SetTopWindow(frame)
		#self.SetSize(800, 600)
		return True

app = CartographerApplication()
app.MainLoop()

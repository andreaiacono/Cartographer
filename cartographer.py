import panel_position
import panel_projection
import proj_azimuthal_orthographic
import proj_generic
import proj_mercator
import wx

class CartographerFrame(wx.Frame):


	
	def __init__(self):
		wx.Frame.__init__(self, None, -1, "Cartographer")
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
		menu_bar.Append(menu_proj, "&Projections");

		self.SetMenuBar(menu_bar)
		self.CreateStatusBar()
		self.SetStatusText("Ready")
		self.rotationx = 0
		self.rotationy = 0
		self.rotationz = 0

		splitter = wx.SplitterWindow(self, -1)
		self.positionPanel = panel_position.Settings(splitter, self)
		self.positionPanel.SetBackgroundColour(wx.BLACK)
		self.projectionPanel = panel_projection.Projection(splitter, -1)
		self.projectionPanel.projection = proj_generic.GenericProjection() 
		self.projectionPanel.projection = proj_azimuthal_orthographic.AzimuthalOrthographicProjection()
		self.projectionPanel.projection = proj_mercator.MercatorProjection() 
		self.projectionPanel.SetBackgroundColour(wx.LIGHT_GREY)
		splitter.SplitHorizontally(self.positionPanel, self.projectionPanel)
		self.Centre()

	def OnInfo(self, event):
		wx.MessageBox("Cartographer \n\nwritten \n\nby Andrea Iacono")

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

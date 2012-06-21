import wx
import panel_projection
import panel_position

class CartographerFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, -1, "Cartographer")
		wx.EVT_CLOSE(self, self.OnQuit)
		ID_INFO = wx.NewId()
		ID_QUIT = wx.NewId()
		ID_PROJ_MERCATOR = wx.NewId()
		ID_PROJ_LAMBERT = wx.NewId()
		ID_PROJ_PETERS = wx.NewId()
		menu_file = wx.Menu()
		menu_file.Append(ID_INFO, "&Info", "Shows info")
		menu_file.AppendSeparator()
		menu_file.Append(ID_QUIT, "&Quit", "Quit Cartographer")
		wx.EVT_MENU(self, ID_INFO, self.OnInfo)
		wx.EVT_MENU(self, ID_QUIT, self.OnQuit)
		menu_bar = wx.MenuBar()
		menu_bar.Append(menu_file, "&File");
		
		menu_proj = wx.Menu()
		menu_proj.Append(ID_PROJ_MERCATOR, "&Mercator", "Settings for a Mercator projection")
		menu_proj.Append(ID_PROJ_LAMBERT, "&Lambert", "Settings for a Lambert projection")
		menu_proj.AppendSeparator()
		menu_proj.Append(ID_PROJ_PETERS, "&Peters", "Settings for a Peters projection")
		menu_bar.Append(menu_proj, "&Projections");

		self.SetMenuBar(menu_bar)
		self.CreateStatusBar()
		self.SetStatusText("Ready")
		self.centerx = 0
		self.centery = 0

		splitter = wx.SplitterWindow(self, -1)
		self.upperPanel = panel_position.Settings(splitter, self) #wx.Panel(splitter)
		self.upperPanel.SetBackgroundColour(wx.BLACK)
		self.lowerPanel = panel_projection.Projection(splitter, -1)
		self.lowerPanel.SetBackgroundColour(wx.LIGHT_GREY)
		splitter.SplitHorizontally(self.upperPanel, self.lowerPanel)
		self.Centre()

	def OnInfo(self, event):
		wx.MessageBox("Cartographer \n\nwritten \n\nby Andrea Iacono")

	def OnQuit(self, event):
		self.Destroy()

	def refresh(self):
		self.lowerPanel.centerx = self.centerx
		self.lowerPanel.centery = self.centery
		self.lowerPanel.Refresh()
		
class CartographerApplication(wx.App):
	def OnInit(self):
		frame = CartographerFrame()
		frame.Show(True)
		self.SetTopWindow(frame)
		#self.SetSize(800, 600)
		return True

app = CartographerApplication()
app.MainLoop()

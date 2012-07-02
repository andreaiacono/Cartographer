import panel_position
import panel_projection
import proj_azimuthal_orthographic
import proj_empty_configuration
import proj_lambert
import proj_lambert_configuration
import proj_mercator
import proj_mercator_configuration
import proj_peters
import options_window
import wx
import proj_sinusoidal
import proj_eckertIV
import proj_collignon


class CartographerFrame(wx.Frame):


	
	def __init__(self):
		wx.Frame.__init__(self, parent=None, id= -1, title="Cartographer", pos=wx.DefaultPosition, size=wx.Size(320, 200))
		wx.EVT_CLOSE(self, self.OnQuit)
		wx.EVT_KEY_DOWN(self, self.OnKeyDown)
		
		menu_bar = wx.MenuBar()
		
		file_menu = wx.Menu()
		
		ID_EXPORT = wx.NewId()
		file_menu.Append(ID_EXPORT, "&Export projection as Image", "Export the actual projection as an image")
		wx.EVT_MENU(self, ID_EXPORT, self.OnExport)
		
		file_menu.AppendSeparator()
		
		ID_QUIT = wx.NewId()
		file_menu.Append(ID_QUIT, "&Quit", "Quit Cartographer")
		wx.EVT_MENU(self, ID_QUIT, self.OnQuit)
		
		menu_bar.Append(file_menu, "&File");
		
		
		menu_proj = wx.Menu()

		menu_cylindrical = wx.Menu()		
		menu_proj.AppendMenu(wx.ID_ANY, "&Cylindrical Projections", menu_cylindrical)
		
		ID_PROJ_MERCATOR = wx.NewId()
		menu_cylindrical.Append(ID_PROJ_MERCATOR, "&Mercator", "Shows a Mercator projection")
		wx.EVT_MENU(self, ID_PROJ_MERCATOR, self.SetMercatorProjection)
		
		ID_PROJ_PETERS = wx.NewId()
		menu_cylindrical.Append(ID_PROJ_PETERS, "&Peters", "Shows a Peters projection")
		wx.EVT_MENU(self, ID_PROJ_PETERS, self.SetPetersProjection)
		
		menu_pseudocyl = wx.Menu()		
		menu_proj.AppendMenu(wx.ID_ANY, "P&seudo Cylindrical Projections", menu_pseudocyl)
		
		ID_PROJ_SINUSOIDAL = wx.NewId()
		menu_pseudocyl.Append(ID_PROJ_SINUSOIDAL, "&Sinusoidal", "Shows a sinusoidal projection")
		wx.EVT_MENU(self, ID_PROJ_SINUSOIDAL, self.SetSinusoidalProjection)

		ID_PROJ_ECKERTIV = wx.NewId()
		menu_pseudocyl.Append(ID_PROJ_ECKERTIV, "&Eckert IV", "Shows an Eckert IV projection")
		wx.EVT_MENU(self, ID_PROJ_ECKERTIV, self.SetEckertIVProjection)

		ID_PROJ_COLLIGNON = wx.NewId()
		menu_pseudocyl.Append(ID_PROJ_COLLIGNON, "&Collignon", "Shows a Collignon projection")
		wx.EVT_MENU(self, ID_PROJ_COLLIGNON, self.SetCollignonProjection)


		menu_conic = wx.Menu()		
		menu_proj.AppendMenu(wx.ID_ANY, "C&onic Projections", menu_conic)
		
		ID_PROJ_LAMBERT = wx.NewId()
		menu_conic.Append(ID_PROJ_LAMBERT, "&Lambert", "Shows a Lambert projection")
		wx.EVT_MENU(self, ID_PROJ_LAMBERT, self.SetLambertProjection)

		menu_azimuthal = wx.Menu()		
		menu_proj.AppendMenu(wx.ID_ANY, "A&zimuthal Projections", menu_azimuthal)

		ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC = wx.NewId()
		menu_azimuthal.Append(ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC, "&Azimuthal Orthographic", "Shows an azimuthal orthographic projection")
		wx.EVT_MENU(self, ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC, self.SetAzimuthalOrtographicProjection)
		
		menu_bar.Append(menu_proj, "&Projections");

		menu_tools = wx.Menu()
		
		ID_OPTIONS = wx.NewId()
		menu_tools.Append(ID_OPTIONS, "&Option", "Shows the options window")
		wx.EVT_MENU(self, ID_OPTIONS, self.OnOptions)
		
		menu_bar.Append(menu_tools, "&Tools");

		menu_about = wx.Menu()
		
		ID_INFO = wx.NewId()
		menu_about.Append(ID_INFO, "&Info", "Shows info")
		wx.EVT_MENU(self, ID_INFO, self.OnInfo)
		
		menu_bar.Append(menu_about, "&About");


		self.SetMenuBar(menu_bar)
		self.CreateStatusBar()
		self.SetStatusText("Ready")
		self.rotationx = 0
		self.rotationy = 180
		self.rotationz = 0

		top_splitter = wx.SplitterWindow(self)
		self.settings_splitter = wx.SplitterWindow(top_splitter)
		
		self.projectionPanel = panel_projection.ProjectionPanel(top_splitter, -1)
		self.projectionPanel.projection = proj_mercator.MercatorProjection()
		top_splitter.SplitHorizontally(self.settings_splitter, self.projectionPanel)
		top_splitter.SetSashGravity(0.3)
		
		self.configurationPanel = proj_empty_configuration.EmptyPanel(self.settings_splitter, "Mercator")
		self.positionCanvas = panel_position.PositionCanvas(self.settings_splitter, self)
		self.settings_splitter.SplitVertically(self.positionCanvas, self.configurationPanel)
		self.settings_splitter.SetSashGravity(0.5)

		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(top_splitter, 1, wx.EXPAND)
		self.SetSizer(sizer)
		self.options = None
		
	def OnOptions(self, event):
		self.options = options_window.Options(None, self)
		self.options.Show(True)

	def OnQuit(self, event):
		#if self.options != None:
		#	self.options.Destroy()
		self.Destroy()

	def OnKeyDown(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_LEFT or key == wx.WXK_NUMPAD_LEFT:
			self.rotationx -= 5
			self.projectionPanel.rotationx = self.rotationx
			self.projectionPanel.Refresh()
		elif key == wx.WXK_RIGHT or key == wx.WXK_NUMPAD_RIGHT:
			self.rotationx += 5
			self.projectionPanel.rotationx = self.rotationx
			self.projectionPanel.Refresh()
		elif key == wx.WXK_UP or key == wx.WXK_NUMPAD_UP:
			self.rotationy -= 5
			self.projectionPanel.rotationy = self.rotationy
			self.projectionPanel.Refresh()
		elif key == wx.WXK_DOWN or key == wx.WXK_NUMPAD_DOWN:
			self.rotationy += 5
			self.projectionPanel.rotationy = self.rotationy
			self.projectionPanel.Refresh()
		elif key == wx.WXK_PAGEUP or key == wx.WXK_NUMPAD_PAGEUP:
			self.rotationz -= 5
			self.projectionPanel.rotationz = self.rotationz
			self.projectionPanel.Refresh()
		elif key == wx.WXK_PAGEDOWN or key == wx.WXK_NUMPAD_PAGEDOWN:
			self.rotationz += 5
			self.projectionPanel.rotationz = self.rotationz
			self.projectionPanel.Refresh()
				
	def refresh(self):
		self.projectionPanel.rotationx = self.rotationx
		self.projectionPanel.rotationy = self.rotationy
		self.projectionPanel.rotationz = self.rotationz
		self.projectionPanel.Refresh()
		
		
	def SetMercatorProjection(self, event):
		self.projectionPanel.projection = proj_mercator.MercatorProjection()
		self.configurationPanel = proj_mercator_configuration.ConfigurationPanel(self.settings_splitter, -1)
		self.SetTitle("Cartographer - Mercator Projection")
		self.refresh()
		
	def SetPetersProjection(self, event):
		self.projectionPanel.projection = proj_peters.PetersProjection()
		self.configurationPanel = proj_empty_configuration.EmptyPanel(self.settings_splitter, "Peters projection")
		self.SetTitle("Cartographer - Peters Projection")
		self.refresh()
	
	def SetLambertProjection(self, event):
		self.projectionPanel.projection = proj_lambert.LambertProjection()
		self.configurationPanel = proj_lambert_configuration.ConfigurationPanel(self.settings_splitter, -1, self)
		self.SetTitle("Cartographer - Lambert Projection")
		self.refresh()
		
	def SetAzimuthalOrtographicProjection(self, event):
		self.projectionPanel.projection = proj_azimuthal_orthographic.AzimuthalOrthographicProjection()
		self.configurationPanel = proj_empty_configuration.EmptyPanel(self.settings_splitter, "Azimuthal ortographic projection")
		self.SetTitle("Cartographer - Azimuthal Ortographic Projection")
		self.refresh()

	def SetSinusoidalProjection(self, event):
		self.projectionPanel.projection = proj_sinusoidal.SinusoidalProjection()
		self.configurationPanel = proj_empty_configuration.EmptyPanel(self.settings_splitter, "Sinusoidal ortographic projection")
		self.SetTitle("Cartographer - Sinusoidal Projection")
		self.refresh()

	def SetEckertIVProjection(self, event):
		self.projectionPanel.projection = proj_eckertIV.EckertIVProjection()
		self.configurationPanel = proj_empty_configuration.EmptyPanel(self.settings_splitter, "Eckert IV projection")
		self.SetTitle("Cartographer - Eckert IV Projection")
		self.refresh()
		
	def SetCollignonProjection(self, event):
		self.projectionPanel.projection = proj_collignon.CollignonProjection()
		self.configurationPanel = proj_empty_configuration.EmptyPanel(self.settings_splitter, "Collignon projection")
		self.SetTitle("Cartographer - Collignon Projection")
		self.refresh()
	def OnExport(self, event) :
	 	
#	 	dlg = wx.FileDialog(self, "Choose a file name to save the image as a PNG to", defaultDir = "", defaultFile = "", wildcard = "*.png", style = wx.SAVE)
#	 	if dlg.ShowModal() != wx.ID_OK:
#	 		return
	 	height = 2000
	 	width = 4000
		mem = wx.MemoryDC() 
	 	image = wx.EmptyBitmap(width, height) 
		mem.SelectObject(image)
		mem.BeginDrawing() 

		okno = panel_projection.ProjectionPanel(self, -1)
		okno.projection = self.projectionPanel.projection
		okno.set_shapes(2)
		okno.resolution = 1
		okno.grid_resolution = 1
		okno.set_paint_grid(self.projectionPanel.paint_grid)
		okno.set_paint_grid_specials(self.projectionPanel.paint_grid_specials)
		okno.rotationx = self.projectionPanel.rotationx
		okno.rotationy = self.projectionPanel.rotationy
		okno.rotationz = self.projectionPanel.rotationz
		okno.width = width
		okno.height = height
		okno.mf = height / float(180)
		okno.tx = okno.mf * 180 + (width - okno.mf * 360) / 2
		okno.ty = okno.mf * 90
		okno.drawProjection(mem, width, height)

		mem.Blit(0, 0, 2000, 1000, wx.PaintDC(okno), 0, 0) 
		mem.EndDrawing() 
		
		image.SaveFile("/home/andrea/test.png" , wx.BITMAP_TYPE_PNG) 
  		okno.Destroy(
					)
	def OnInfo(self, event):

		description = """Cartographer is a simple cartography application"""

		licence = """Cartographer is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.
Cartographer is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""
		
#		info = wx.AboutDialogInfo()
#		
#		info.SetIcon(wx.Icon('mercator.png', wx.BITMAP_TYPE_PNG))
#		info.SetName('Cartographer')
#		info.SetVersion('1.0')
#		info.SetDescription(description)
#		info.SetCopyright('(C) 2012 Andrea Iacono')
#		info.SetWebSite('http://www.zetcode.com')
#		info.SetLicence(licence)
#		info.AddDeveloper('Andrea Iacono')
#		info.AddDocWriter('Andrea Iacono')
#		
#		wx.AboutBox(info)

class CartographerApplication(wx.App):
	
	def OnInit(self):
		frame = CartographerFrame()
		frame.Show(True)
		self.SetTopWindow(frame)
		#self.SetSize(800, 600)
		return True

app = CartographerApplication()
app.MainLoop()

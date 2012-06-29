import wx

class Settings(wx.Frame):

	def __init__(self, parent, cartographer):
		super(Settings, self).__init__(parent, title="Options", size=(300, 250))
		self.cartographer = cartographer
		panel = wx.Panel(self)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		fgs = wx.FlexGridSizer(3, 2, 9, 25)
		
		label_res = wx.StaticText(panel, label="Projection Resolution")
		empty_label = wx.StaticText(panel, label="")
		label_grid_res = wx.StaticText(panel, label="Grid Resolution")
		
		self.slider_proj_res = wx.Slider(panel)
		self.slider_proj_res.SetMax(15)
		self.slider_proj_res.SetMin(1)
		
		self.slider_grid_res = wx.Slider(panel)
		self.slider_grid_res.SetMax(5)
		self.slider_grid_res.SetMin(1)

		self.check_draw_grid = wx.CheckBox(panel, label='Draw Grid') 
		self.check_draw_specials = wx.CheckBox(panel, label='Draw Special Parallels') 
		self.check_show_countries = wx.CheckBox(panel, label='Draw Countries Borders') 
		self.Bind(wx.EVT_SLIDER, self.on_update)
		self.Bind(wx.EVT_CHECKBOX, self.on_update)
		
		fgs.AddMany([(label_res), (self.slider_proj_res, 1, wx.EXPAND),
					 (self.check_draw_grid, 1, wx.EXPAND), (empty_label), 
					 (label_grid_res, 1, wx.EXPAND), (self.slider_grid_res, 1, wx.EXPAND),
					 (self.check_draw_specials, 1, wx.EXPAND), (empty_label),
					 (self.check_show_countries, 1, wx.EXPAND), (empty_label)])
		
		fgs.AddGrowableCol(1, 1)
		
		hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
		panel.SetSizer(hbox)
		
	def on_update(self, event):
		self.cartographer.projectionPanel.set_resolution(self.slider_proj_res.GetValue())
		self.cartographer.projectionPanel.set_grid_resolution(self.slider_grid_res.GetValue())
		self.cartographer.projectionPanel.set_paint_grid(self.check_draw_grid.GetValue())
		self.cartographer.projectionPanel.set_paint_grid_specials(self.check_draw_specials.GetValue())
		self.cartographer.projectionPanel.set_shapes(self.check_show_countries.GetValue())
		self.cartographer.projectionPanel.Refresh()
		
		
if __name__ == '__main__':

	app = wx.App()
	frame = Settings(None, None)
	frame.Show()
	app.MainLoop()

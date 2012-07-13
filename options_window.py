import wx

class Options(wx.Frame):

	def __init__(self, parent, cartographer):
		super(Options, self).__init__(parent, title="Options", size=(300, 210))
		self.cartographer = cartographer
		panel = wx.Panel(self)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		fgs = wx.FlexGridSizer(5, 2, 10, 20)
		
		label_res = wx.StaticText(panel, label="Projection Resolution")
		empty_label = wx.StaticText(panel, label="")
		label_grid_res = wx.StaticText(panel, label="Grid Resolution")
		
		label_from_mer = wx.StaticText(panel, label="Zoom X") 
		label_from_parallel = wx.StaticText(panel, label="Zoom Y") 
		
		self.slider_proj_res = wx.Slider(panel, minValue=1, maxValue=cartographer.projectionPanel.resolution_scale, style=wx.SL_HORIZONTAL)
		self.slider_grid_res = wx.Slider(panel, minValue=1, maxValue=cartographer.projectionPanel.resolution_scale, style=wx.SL_HORIZONTAL)
		self.slider_from_mer = wx.Slider(panel, minValue=0, maxValue=360, value=360, style=wx.SL_HORIZONTAL)
		self.slider_from_parallel = wx.Slider(panel, minValue=0, maxValue=180, value=180, style=wx.SL_HORIZONTAL)
		self.slider_proj_res.SetValue(cartographer.projectionPanel.resolution)
		self.slider_grid_res.SetValue(cartographer.projectionPanel.grid_resolution)
		 

		self.check_draw_frame = wx.CheckBox(panel, label='Draw Frame') 
		self.check_draw_grid = wx.CheckBox(panel, label='Draw Grid') 
		self.check_draw_specials = wx.CheckBox(panel, label='Draw Special Parallels') 
		self.check_show_countries = wx.CheckBox(panel, label='Draw Countries Borders')
		
		self.check_draw_frame.SetValue(cartographer.projectionPanel.paint_frame)
		self.check_draw_grid.SetValue(cartographer.projectionPanel.paint_grid)
		self.check_draw_specials.SetValue(cartographer.projectionPanel.paint_grid_specials)
		self.check_show_countries.SetValue(cartographer.projectionPanel.shape_type == 1)
 
		self.Bind(wx.EVT_SLIDER, self.on_update)
		self.Bind(wx.EVT_CHECKBOX, self.on_update)
		
		fgs.AddMany([
					 (label_from_mer), (self.slider_from_mer, 1, wx.EXPAND),
					 (label_from_parallel), (self.slider_from_parallel, 1, wx.EXPAND),
					 (label_res), (self.slider_proj_res, 1, wx.EXPAND),
					 (self.check_draw_frame, 1, wx.EXPAND), (empty_label), 
					 (self.check_draw_grid, 1, wx.EXPAND), (empty_label), 
					 (label_grid_res, 1, wx.EXPAND), (self.slider_grid_res, 1, wx.EXPAND),
					 (self.check_draw_specials, 1, wx.EXPAND), (empty_label),
					 (self.check_show_countries, 1, wx.EXPAND), (empty_label)])
		
		fgs.AddGrowableCol(1, 1)
		
		hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
		panel.SetSizer(hbox)
		
	def on_update(self, event):
		
		self.cartographer.projectionPanel.set_from_meridian(self.slider_from_mer.GetValue())
		self.cartographer.projectionPanel.set_from_parallel(self.slider_from_parallel.GetValue())
		
		self.cartographer.projectionPanel.set_resolution(self.slider_proj_res.GetValue())
		self.cartographer.projectionPanel.set_grid_resolution(self.slider_grid_res.GetValue())
		self.cartographer.projectionPanel.set_paint_frame(self.check_draw_frame.GetValue())
		self.cartographer.projectionPanel.set_paint_grid(self.check_draw_grid.GetValue())
		self.cartographer.projectionPanel.set_paint_grid_specials(self.check_draw_specials.GetValue())
		if self.check_show_countries.GetValue():
			self.cartographer.projectionPanel.set_shapes(1)
		else:
			self.cartographer.projectionPanel.set_shapes(0)
		self.cartographer.projectionPanel.Refresh()
		
		
if __name__ == '__main__':

	app = wx.App()
	frame = Options(None, None)
	frame.Show()
	app.MainLoop()

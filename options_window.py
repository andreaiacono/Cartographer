import wx

class Options(wx.Frame):

	def __init__(self, parent, cartographer):
		super(Options, self).__init__(parent, title="Options", size=(500, 320))
		self.cartographer = cartographer
		panel = wx.Panel(self)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		
		fgs = wx.FlexGridSizer(7, 3, 10, 20)
		
		label_res = wx.StaticText(panel, label="Projection Resolution")
		empty_label = wx.StaticText(panel, label="")
		label_grid_res = wx.StaticText(panel, label="Grid Resolution")
		
		label_zoom = wx.StaticText(panel, label="Zoom") 
		
		self.slider_proj_res = wx.Slider(panel, minValue=1, maxValue=cartographer.projection_panel.resolution_scale, style=wx.SL_HORIZONTAL)
		self.slider_grid_res = wx.Slider(panel, minValue=1, maxValue=cartographer.projection_panel.resolution_scale, style=wx.SL_HORIZONTAL)
		self.slider_zoom = wx.Slider(panel, minValue=15, maxValue=360, value=360, style=wx.SL_HORIZONTAL)
		self.slider_proj_res.SetValue(cartographer.projection_panel.resolution)
		self.slider_grid_res.SetValue(cartographer.projection_panel.grid_resolution)
		
		
		label_parallel_number = wx.StaticText(panel, label="\nDraw a parallel every ") 
		label_parallel_number_end = wx.StaticText(panel, label="\ndegrees") 
		label_meridian_number = wx.StaticText(panel, label="\nDraw a meridian every ") 
		label_meridian_number_end = wx.StaticText(panel, label="\ndegrees") 
		
		self.slider_parallel_number = wx.Slider(panel, minValue=1, maxValue=90, value=15, style=wx.SL_HORIZONTAL| wx.SL_LABELS)
		self.slider_meridian_number = wx.Slider(panel, minValue=1, maxValue=180, value=15, style=wx.SL_HORIZONTAL| wx.SL_LABELS)
		

		self.check_draw_frame = wx.CheckBox(panel, label='Draw Frame') 
		self.check_draw_grid = wx.CheckBox(panel, label='Draw Grid') 
		self.check_draw_specials = wx.CheckBox(panel, label='Draw Special Parallels') 
		self.check_show_countries = wx.CheckBox(panel, label='Draw Countries Borders')
		
		self.check_draw_frame.SetValue(cartographer.projection_panel.paint_frame)
		self.check_draw_grid.SetValue(cartographer.projection_panel.paint_grid)
		self.check_draw_specials.SetValue(cartographer.projection_panel.paint_grid_specials)
		self.check_show_countries.SetValue(cartographer.projection_panel.shape_type == 1)

		self.Bind(wx.EVT_SLIDER, self.on_slider_change)
		self.Bind(wx.EVT_CHECKBOX, self.on_slider_change)
		
		fgs.AddMany([
					 (label_zoom), (self.slider_zoom, 1, wx.EXPAND), (empty_label), 
					 (label_res), (self.slider_proj_res, 1, wx.EXPAND), (empty_label), 
					 (self.check_draw_frame, 1, wx.EXPAND), (empty_label),  (empty_label), 
					 (self.check_draw_grid, 1, wx.EXPAND), (empty_label),  (empty_label), 
					 (label_grid_res, 1, wx.EXPAND), (self.slider_grid_res, 1, wx.EXPAND), (empty_label), 
					 (label_meridian_number), (self.slider_meridian_number, 1, wx.EXPAND), (label_meridian_number_end),
					 (label_parallel_number), (self.slider_parallel_number, 1, wx.EXPAND), (label_parallel_number_end),
					 (self.check_draw_specials, 1, wx.EXPAND), (empty_label), (empty_label), 
					 (self.check_show_countries, 1, wx.EXPAND), (empty_label), (empty_label) ])
		
		fgs.AddGrowableCol(1, 1)
		
		hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
		panel.SetSizer(hbox)
		
	def on_slider_change(self, event):
		
		self.cartographer.projection_panel.set_zoom(self.slider_zoom.GetValue())
		self.cartographer.projection_panel.set_resolution(self.slider_proj_res.GetValue())
		self.cartographer.projection_panel.set_grid_resolution(self.slider_grid_res.GetValue())
		self.cartographer.projection_panel.set_paint_frame(self.check_draw_frame.GetValue())
		self.cartographer.projection_panel.set_paint_grid(self.check_draw_grid.GetValue())
		self.cartographer.projection_panel.set_paint_grid_specials(self.check_draw_specials.GetValue())
		self.cartographer.projection_panel.set_meridian_degrees(self.slider_meridian_number.GetValue())
		self.cartographer.projection_panel.set_parallel_degrees(self.slider_parallel_number.GetValue())
		
		if self.check_show_countries.GetValue():
			self.cartographer.projection_panel.set_shapes(1)
		else:
			self.cartographer.projection_panel.set_shapes(0)
		self.cartographer.projection_panel.compute_size()
		self.cartographer.projection_panel.refresh_window()
		
		
if __name__ == '__main__':

	app = wx.App()
	frame = Options(None, None)
	frame.Show()
	app.MainLoop()

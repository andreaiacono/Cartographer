import wx

class ConfigurationPanel(wx.Panel):
    
    def __init__(self, parent, window_id, cartographer, projection):
    
        sty = wx.NO_BORDER
        wx.Window.__init__(self, parent, window_id, style=sty, size=wx.Size(200, 80))
        self.parent = parent
        self.cartographer = cartographer
    
        wx.EVT_SIZE(self, self.OnSize)
        
        self.panel = wx.Panel(self)
                    
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(2, 2, 10, 25)
        
        label_phi1 = wx.StaticText(self.panel, label="Central Latitude")
        label_phi2 = wx.StaticText(self.panel, label="Central Longitude")
        
        self.slider_lat = wx.Slider(self.panel, minValue=-179, maxValue=179, style=wx.SL_HORIZONTAL)
        self.slider_lon = wx.Slider(self.panel, minValue=-89, maxValue=89, style=wx.SL_HORIZONTAL)
        self.slider_lat.SetValue(projection.central_lat)
        self.slider_lon.SetValue(projection.central_lon)
        
        self.Bind(wx.EVT_SLIDER, self.on_update)
        
        fgs.AddMany([(label_phi1), (self.slider_lat, 1, wx.EXPAND),
                     (label_phi2), (self.slider_lon, 1, wx.EXPAND)])
        
        fgs.AddGrowableCol(1, 1)
        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)
        
    def on_update(self, event):
        #print "setting values phi1=" + str(self.slider_lat.GetValue()) + " phi2=" + str(self.slider_lon.GetValue())
        self.cartographer.projection_panel.projection.set_central_coords(self.slider_lat.GetValue(), self.slider_lon.GetValue())
        self.cartographer.projection_panel.Refresh()
        
    def OnSize(self, event):
        self.panel.SetSize(self.GetSizeTuple())
        

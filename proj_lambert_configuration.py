import math
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
        
        label_phi1 = wx.StaticText(self.panel, label="Standard Parallel #1")
        label_phi2 = wx.StaticText(self.panel, label="Standard Parallel #2")
        
        self.slider_phi1 = wx.Slider(self.panel, minValue=0, maxValue=89, style=wx.SL_HORIZONTAL)
        self.slider_phi2 = wx.Slider(self.panel, minValue=0, maxValue=89, style=wx.SL_HORIZONTAL)
        self.slider_phi1.SetValue(30)
        self.slider_phi2.SetValue(60)
        
        self.Bind(wx.EVT_SLIDER, self.on_update)
        
        fgs.AddMany([(label_phi1), (self.slider_phi1, 1, wx.EXPAND),
                     (label_phi2), (self.slider_phi2, 1, wx.EXPAND)])
        
        fgs.AddGrowableCol(1, 1)
        hbox.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)
        
    def on_update(self, event):
        
        #print event.GetSource()
        # TODO: if slider 1 is moving, adjust slider2, else the opposite
        if self.slider_phi1.GetValue() >= self.slider_phi2.GetValue():
            self.slider_phi1.SetValue(self.slider_phi1.GetValue()+1)
        
        elif self.slider_phi2.GetValue() <= self.slider_phi1.GetValue():
            self.slider_phi2.SetValue(self.slider_phi1.GetValue()+1)
        
        #print "setting values phi1=" + str(self.slider_phi1.GetValue()) + " phi2=" + str(self.slider_phi2.GetValue())
        self.cartographer.projection_panel.projection.set_phi(math.radians(self.slider_phi1.GetValue()), math.radians(self.slider_phi2.GetValue()))
        self.cartographer.projection_panel.Refresh()
        self.cartographer.position_canvas.set_standard_parallel1(self.slider_phi1.GetValue())
        self.cartographer.position_canvas.Refresh()
        
    def OnSize(self, event):
        self.panel.SetSize(self.GetSizeTuple())
        

#coding=UTF-8
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
        fgs = wx.FlexGridSizer(rows=7, cols=3, hgap=10, vgap=15)
        
        label_standard = wx.StaticText(self.panel, label="\nStandard Latitude")
        self.label_value = wx.StaticText(self.panel, label="\n 40.0°")
        self.slider_lat = wx.Slider(self.panel, minValue=0, maxValue=8000, value=4000, style=wx.SL_HORIZONTAL)
        fgs.AddMany([(label_standard), (self.label_value), (self.slider_lat, 1, wx.EXPAND)])
        
        self.projections = {}
        self.projections['Balthasart'] = 50.0
        self.projections['Behrmann'] = 30.0
        self.projections['Gall'] = 45.0
        self.projections['Lambert'] = 0.0
        self.projections['Peters'] = 44.138
        self.projections['Trystan Edwards'] = 37.383
        self.radiobuttons = {}
        
        style = wx.RB_GROUP
        self.radiobuttons = []
        for item in self.projections:
            rb = wx.RadioButton(self.panel, wx.NewId(), item, style=style)
            fgs.Add(rb)
            self.radiobuttons.append(rb)
            style = 0
        
        self.Bind(wx.EVT_RADIOBUTTON, self.on_radiobutton_pressed)
        self.Bind(wx.EVT_SLIDER, self.on_slider_change)
        
        fgs.AddGrowableCol(2, 1)
        hbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)
        
    def on_radiobutton_pressed(self, event):
        rb = wx.FindWindowById(event.GetEventObject().GetId())
        val = self.projections[rb.GetLabel()]
        self.slider_lat.SetValue(int(val*100))
        self.update_windows(val)
        
    def on_slider_change(self, val):
        
        for rb in self.radiobuttons:
            rb.SetValue(False)
        self.update_windows(self.slider_lat.GetValue() / float(100))
    
        
    def update_windows(self, val):
        self.label_value.SetLabel("\n" + str(round(val, 3)) + "°")
        self.cartographer.projection_panel.projection.set_standard_latitude(self.slider_lat.GetValue() / 100)
        self.cartographer.projection_panel.Refresh()
        self.Refresh()
        
        
    def OnSize(self, event):
        self.panel.SetSize(self.GetSizeTuple())
        

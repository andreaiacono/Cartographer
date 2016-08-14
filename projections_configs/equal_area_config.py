import math
import wx

class ConfigurationPanel(wx.Panel):

    def __init__(self, parent, window_id, cartographer):
        self.parent = parent
        self.cartographer = cartographer
        self.radiobuttons = []

        sty = wx.SUNKEN_BORDER
        wx.Window.__init__(self, parent, window_id, style=sty)

        wx.EVT_SIZE(self, self.OnSize)
        self.panel = wx.Panel(self)
                    
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        sizer = wx.GridBagSizer(4, 1)

        self.projections = {'Lambert': 0.0, 'Behrmann': 30.0, 'Trystan Edwards': 37.383, 'Peters': 44.138, 'Gall': 45.0, 'Balthasart': 50.0}
        starting_projection = self.projections['Behrmann']

        self.label_standard = wx.StaticText(self.panel, label="\nStandard Latitude: " + str(starting_projection) + "")
        sizer.Add(self.label_standard, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        self.slider_lat = wx.Slider(self.panel, minValue=0, maxValue=6000, value=(starting_projection*100), style=wx.SL_HORIZONTAL)
        sizer.Add(self.slider_lat, pos=(1, 0), span=(1, 2), flag=wx.EXPAND | wx.RIGHT, border=15)

        style = wx.RB_GROUP
        for idx, item in enumerate(self.projections):
            rb = wx.RadioButton(self.panel, wx.NewId(), item, style=style)
            sizer.Add(rb, pos=(idx/2+2, idx % 2), flag=wx.ALIGN_LEFT)
            rb.SetValue(self.projections[item] == starting_projection)
            self.radiobuttons.append(rb)
            style = 0

        self.Bind(wx.EVT_RADIOBUTTON, self.on_radiobutton_pressed)
        self.Bind(wx.EVT_SLIDER, self.on_slider_change)
        sizer.AddGrowableCol(1)

        hbox.Add(sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        self.panel.SetSizer(hbox)
        self.Hide()
        
    def on_radiobutton_pressed(self, event):
        rb = wx.FindWindowById(event.GetEventObject().GetId())
        val = self.projections[rb.GetLabel()]
        self.slider_lat.SetValue(int(val*100))
        self.update_windows(val)
        
    def on_slider_change(self, val):
        for rb in self.radiobuttons:
            rb.SetValue(0)
        self.update_windows(self.slider_lat.GetValue() / float(100))
        
    def update_windows(self, val):
        self.label_standard.SetLabel("\nStandard Latitude: " + str(round(val, 3)) + "")
        self.cartographer.projection_panel.projection.set_standard_latitude(math.radians(val))
        self.cartographer.projection_panel.Refresh()
        self.Refresh()
        
    def OnSize(self, event):
        self.panel.SetSize(self.GetSizeTuple())
        

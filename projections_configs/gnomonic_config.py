import math
import wx

class ConfigurationPanel(wx.Panel):

    def __init__(self, parent, window_id, cartographer):
        self.parent = parent
        self.cartographer = cartographer

        sty = wx.SUNKEN_BORDER
        wx.Window.__init__(self, parent, window_id, style=sty, size=wx.Size(200, 80))
        wx.EVT_SIZE(self, self.OnSize)

        self.panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(2, 2, 10, 25)

        distance = wx.StaticText(self.panel, label="Distance")

        self.depth_id = wx.NewId()
        self.slider_distance = wx.Slider(self.panel, id=self.depth_id, minValue=15, maxValue=120, value=40, style=wx.SL_HORIZONTAL)

        self.Bind(wx.EVT_SLIDER, self.on_update)

        fgs.AddMany([distance, (self.slider_distance, 1, wx.EXPAND)])

        fgs.AddGrowableCol(1, 1)
        hbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(hbox)
        self.Hide()

    def on_update(self, event):
        self.cartographer.projection_panel.projection.set_distance(self.slider_distance.GetValue())
        self.cartographer.projection_panel.Refresh()

    def OnSize(self, event):
        self.panel.SetSize(self.GetSizeTuple())


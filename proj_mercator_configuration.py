import wx
import panel_position

class ConfigurationPanel(wx.Panel):
    
    def __init__(self, parent, window_id):
        sty = wx.NO_BORDER
        wx.Window.__init__(self, parent, window_id, style=sty)
        self.parent = parent
        
#        sizer =wx.GridBagSizer(2, 2)
#        
#        sizer.Add(self.slider_phi_1, (0, 1), (1,1),  wx.EXPAND)
#
#        self.slider_phi_2 = wx.Slider(self)
#        sizer.Add(wx.StaticText(self, label="Phi 2: "), (0,1), wx.DefaultSpan, wx.ALL, 5)
#        sizer.Add(self.slider_phi_2, (1, 1), (1,1),  wx.EXPAND)


        flexG = wx.FlexGridSizer( 3, 3, 0, 0 )
        flexG.SetFlexibleDirection( wx.BOTH )
        flexG.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.slider_phi_1 = wx.Slider(self)
        label_phi_1 = wx.StaticText(self, label="Phi 1: ")
        #sizer.Add(, (0,0), wx.DefaultSpan, wx.ALL, 5)

        flexG.Add(label_phi_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        flexG.Add(self.slider_phi_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizer(flexG)
        
        
        
#        self.slider2 = wx.Slider(self, -1, 50, 0, 100, (330, 10), (50, 250), wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
 #@        sizer.Add(self.slider2)
        # respond to changes in slider position ...
        #self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        #self.SetSizerAndFit(sizer)
        
    def sliderUpdate(self, event):
        self.pos1 = self.slider_phi_1.GetValue()
        self.pos2 = self.slider_phi_2.GetValue()
        str1 = "pos1 = %d   pos2 = %d" % (self.pos1, self.pos2)
        # display current slider positions in the frame's title
        self.SetTitle(str1)
        
        
import wx
import panel_position

class ConfigurationPanel(wx.Panel):
    
    def __init__(self, parent, window_id):
        sty = wx.NO_BORDER
        wx.Window.__init__(self, parent, window_id, style=sty)
        self.parent = parent
        
        
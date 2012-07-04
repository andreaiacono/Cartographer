import wx

class EmptyPanel(wx.Panel):
    
 
    def __init__(self, parent, title):
        wx.Window.__init__(self, parent)
        self.parent = parent
        wx.EVT_SIZE(self, self.OnSize)
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl = wx.StaticText(self.panel, label=title)
        vbox.Add(lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        
    def OnSize(self, event):
        self.panel.SetSize(self.GetSizeTuple())

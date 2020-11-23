import wx

class EmptyPanel(wx.Panel):
    
 
    def __init__(self, parent):
        self.parent = parent
        wx.Window.__init__(self, self.parent, style=wx.SUNKEN_BORDER, size=(1,1))
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self.panel, label="\n   No parameters for this projection")
        vbox.Add(lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=25)
        self.Hide()

    def OnSize(self, event):
        self.panel.SetSize(self.GetSize())

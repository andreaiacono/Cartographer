import wx

class EmptyPanel(wx.Panel):
    
    def __init__(self, parent, title):
        wx.Window.__init__(self, parent)
        self.parent = parent
        
        panel = wx.Window(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        lbl = wx.StaticText(panel, label=title)
        vbox.Add(lbl, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

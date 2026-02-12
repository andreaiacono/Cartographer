import wx

class EmptyPanel(wx.Panel):

    def __init__(self, parent, cartographer=None):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.cartographer = cartographer

        # Set minimum size to ensure visibility
        self.SetMinSize(wx.Size(-1, 150))

        # Create main sizer
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self, label="Projection Parameters")
        title_font = title.GetFont()
        title_font.PointSize += 1
        title_font = title_font.Bold()
        title.SetFont(title_font)
        vbox.Add(title, flag=wx.ALL, border=5)

        # Info label
        info_lbl = wx.StaticText(self, label="No specific parameters for this projection")
        vbox.Add(info_lbl, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)

        # Separator
        vbox.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=5)

        # Resolution slider section
        res_label = wx.StaticText(self, label="Resolution:")
        vbox.Add(res_label, flag=wx.LEFT | wx.TOP, border=5)

        res_sizer = wx.BoxSizer(wx.HORIZONTAL)
        res_sizer.Add(wx.StaticText(self, label="Low"), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=5)

        # Get current resolution value if cartographer is available
        if cartographer:
            current_res = cartographer.projection_panel.resolution
            # Invert for slider: resolution 1 = slider 50, resolution 50 = slider 1
            slider_value = 51 - current_res
        else:
            slider_value = 50  # Default to high resolution (right side)

        self.slider_resolution = wx.Slider(
            self, minValue=1, maxValue=50,
            value=slider_value,
            style=wx.SL_HORIZONTAL
        )
        res_sizer.Add(self.slider_resolution, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        res_sizer.Add(wx.StaticText(self, label="High"), flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        vbox.Add(res_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Bind slider event
        if cartographer:
            self.Bind(wx.EVT_SLIDER, self.on_resolution_change)

        # Set the sizer and force layout
        self.SetSizer(vbox)
        self.Layout()
        self.Fit()

    def on_resolution_change(self, event):
        """Handle resolution slider changes."""
        if self.cartographer:
            value = self.slider_resolution.GetValue()
            # Invert the slider: right = high resolution (1), left = low resolution (50)
            inverted_value = 51 - value
            self.cartographer.projection_panel.set_resolution(inverted_value)
            self.cartographer.projection_panel.compute_size()
            self.cartographer.projection_panel.OnDraw()
            self.cartographer.projection_panel.Refresh()

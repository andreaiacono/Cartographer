import wx


class SliderPanel(wx.Panel):
    def __init__(self, parent, cartographer):
        super(SliderPanel, self).__init__(parent)
        self.cartographer = cartographer

        sizer = wx.FlexGridSizer(3, 3, 5, 10)
        sizer.AddGrowableCol(1, 1)

        label_ray_density = wx.StaticText(self, label="Ray Density")
        self.slider_ray_density = wx.Slider(
            self, minValue=5, maxValue=80,
            value=cartographer.earth_canvas.ray_density,
            style=wx.SL_HORIZONTAL
        )
        label_ray_density_end = wx.StaticText(self, label="")

        label_ray_alpha = wx.StaticText(self, label="Ray Transparency")
        self.slider_ray_alpha = wx.Slider(
            self, minValue=0, maxValue=100,
            value=cartographer.earth_canvas.ray_alpha,
            style=wx.SL_HORIZONTAL
        )
        label_ray_alpha_end = wx.StaticText(self, label="")

        label_unwrap = wx.StaticText(self, label="Cylinder Unwrap")
        self.slider_cylinder_unwrap = wx.Slider(
            self, minValue=0, maxValue=100,
            value=cartographer.earth_canvas.cylinder_unwrap,
            style=wx.SL_HORIZONTAL
        )
        label_unwrap_end = wx.StaticText(self, label="")

        sizer.Add(label_ray_density, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.slider_ray_density, 1, wx.EXPAND)
        sizer.Add(label_ray_density_end, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        sizer.Add(label_ray_alpha, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.slider_ray_alpha, 1, wx.EXPAND)
        sizer.Add(label_ray_alpha_end, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        sizer.Add(label_unwrap, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.slider_cylinder_unwrap, 1, wx.EXPAND)
        sizer.Add(label_unwrap_end, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_SLIDER, self.on_slider_change)

    def on_slider_change(self, event):
        self.cartographer.earth_canvas.ray_density = self.slider_ray_density.GetValue()
        self.cartographer.earth_canvas.ray_alpha = self.slider_ray_alpha.GetValue()
        self.cartographer.earth_canvas.cylinder_unwrap = self.slider_cylinder_unwrap.GetValue()
        self.cartographer.earth_canvas.Refresh()

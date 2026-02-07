import wx


class SliderPanel(wx.Panel):
    def __init__(self, parent, cartographer):
        super(SliderPanel, self).__init__(parent)
        self.cartographer = cartographer

        sizer = wx.FlexGridSizer(3, 3, 5, 10)
        sizer.AddGrowableCol(1, 1)

        label_ray_density = wx.StaticText(self, label="Resolution")
        # Slider: 10 to 50 (41 positions)
        # Value N means "draw N points out of every 50"
        initial_points_per_50 = getattr(cartographer.earth_canvas, 'points_per_50', 30)
        self.slider_ray_density = wx.Slider(
            self, minValue=10, maxValue=50,
            value=initial_points_per_50,
            style=wx.SL_HORIZONTAL
        )
        self.label_ray_density_value = wx.StaticText(self, label=self._format_ray_density(initial_points_per_50))

        label_ray_alpha = wx.StaticText(self, label="Ray Transparency")
        self.slider_ray_alpha = wx.Slider(
            self, minValue=0, maxValue=100,
            value=cartographer.earth_canvas.ray_alpha,
            style=wx.SL_HORIZONTAL
        )
        self.label_ray_alpha_value = wx.StaticText(self, label=f"{cartographer.earth_canvas.ray_alpha}%")

        label_unwrap = wx.StaticText(self, label="Cylinder Unwrap")
        self.slider_cylinder_unwrap = wx.Slider(
            self, minValue=0, maxValue=100,
            value=cartographer.earth_canvas.cylinder_unwrap,
            style=wx.SL_HORIZONTAL
        )
        self.label_unwrap_value = wx.StaticText(self, label=f"{cartographer.earth_canvas.cylinder_unwrap}%")

        sizer.Add(label_ray_density, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.slider_ray_density, 1, wx.EXPAND)
        sizer.Add(self.label_ray_density_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        sizer.Add(label_ray_alpha, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.slider_ray_alpha, 1, wx.EXPAND)
        sizer.Add(self.label_ray_alpha_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        sizer.Add(label_unwrap, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.slider_cylinder_unwrap, 1, wx.EXPAND)
        sizer.Add(self.label_unwrap_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_SLIDER, self.on_slider_change)

    def _format_ray_density(self, points_per_50):
        """Format ray density value for display.
        Value represents 'N out of 50 points'.
        """
        percentage = int(points_per_50 * 100 / 50)
        return f"{percentage}%"

    def on_slider_change(self, event):
        # Get slider values
        points_per_50 = self.slider_ray_density.GetValue()
        ray_alpha = self.slider_ray_alpha.GetValue()
        unwrap_value = self.slider_cylinder_unwrap.GetValue()

        # Update earth canvas values
        self.cartographer.earth_canvas.points_per_50 = points_per_50
        self.cartographer.earth_canvas.ray_alpha = ray_alpha
        self.cartographer.earth_canvas.cylinder_unwrap = unwrap_value

        # Update value labels
        self.label_ray_density_value.SetLabel(self._format_ray_density(points_per_50))
        self.label_ray_alpha_value.SetLabel(f"{ray_alpha}%")
        self.label_unwrap_value.SetLabel(f"{unwrap_value}%")

        # Disable ray sliders when cylinder is unwrapped (rays don't apply when unfolding)
        enable_rays = (unwrap_value == 0)
        # self.slider_ray_density.Enable(enable_rays)
        self.slider_ray_alpha.Enable(enable_rays)

        self.cartographer.earth_canvas.Refresh()

import wx


class EarthCanvasParams(wx.Panel):
    def __init__(self, parent, cartographer):
        super(EarthCanvasParams, self).__init__(parent)
        self.cartographer = cartographer

        # Set minimum size to prevent negative height warnings
        self.SetMinSize(wx.Size(-1, 130))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Resolution slider row
        label_ray_density = wx.StaticText(self, label="Resolution")
        label_ray_density.SetMinSize(wx.Size(80, -1))
        # Slider: 0 to 29 (30 steps)
        # Slider 0 → resolution 0.0 (draws nothing)
        # Slider 1-29 → resolution 1.0 to 7.5 (draws 2% to 15%)
        # Skip values < 1.0 to avoid Bresenham sampling issues
        initial_resolution = getattr(cartographer.earth_canvas, 'resolution', 1.0)
        # Convert resolution to slider value
        if initial_resolution < 0.5:
            initial_slider_value = 0
        else:
            initial_slider_value = int(1 + (initial_resolution - 1.0) * 28.0 / 6.5)
        self.slider_ray_density = wx.Slider(
            self, minValue=0, maxValue=29,
            value=initial_slider_value,
            style=wx.SL_HORIZONTAL
        )
        self.slider_ray_density.SetMinSize(wx.Size(150, 30))

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row1.Add(label_ray_density, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        row1.Add(self.slider_ray_density, 1, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(row1, 0, wx.EXPAND | wx.ALL, 5)

        # Ray transparency slider row
        label_ray_alpha = wx.StaticText(self, label="Ray Transparency")
        label_ray_alpha.SetMinSize(wx.Size(80, -1))
        self.slider_ray_alpha = wx.Slider(
            self, minValue=0, maxValue=100,
            value=cartographer.earth_canvas.ray_alpha,
            style=wx.SL_HORIZONTAL
        )
        self.slider_ray_alpha.SetMinSize(wx.Size(150, 30))
        self.label_ray_alpha_value = wx.StaticText(self, label=f"{cartographer.earth_canvas.ray_alpha}%")
        self.label_ray_alpha_value.SetMinSize(wx.Size(40, -1))

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(label_ray_alpha, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        row2.Add(self.slider_ray_alpha, 1, wx.ALIGN_CENTER_VERTICAL)
        row2.Add(self.label_ray_alpha_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        main_sizer.Add(row2, 0, wx.EXPAND | wx.ALL, 5)

        # Surface unroll slider row. Only cylinders and cones can be unrolled,
        # so this row is hidden for the projections whose surface is already
        # flat, and renamed for whichever surface is on screen.
        self.label_unwrap = label_unwrap = wx.StaticText(self, label="Cylinder Unwrap")
        label_unwrap.SetMinSize(wx.Size(80, -1))
        self.slider_surface_unroll = wx.Slider(
            self, minValue=0, maxValue=100,
            value=cartographer.earth_canvas.surface_unroll,
            style=wx.SL_HORIZONTAL
        )
        self.slider_surface_unroll.SetMinSize(wx.Size(150, 30))
        self.label_unwrap_value = wx.StaticText(self, label=f"{cartographer.earth_canvas.surface_unroll}%")
        self.label_unwrap_value.SetMinSize(wx.Size(40, -1))

        self.row_unroll = row3 = wx.BoxSizer(wx.HORIZONTAL)
        row3.Add(label_unwrap, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        row3.Add(self.slider_surface_unroll, 1, wx.ALIGN_CENTER_VERTICAL)
        row3.Add(self.label_unwrap_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        main_sizer.Add(row3, 0, wx.EXPAND | wx.ALL, 5)

        self.main_sizer = main_sizer
        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_SLIDER, self.on_slider_change)

    def set_projection(self, projection):
        """Show the unroll slider only for surfaces that can actually unroll.

        A cylinder unwraps and a cone unrolls; an azimuthal plane and the
        pseudo-cylindrical surfaces are already flat, so the control would do
        nothing at all for them.
        """
        types = projection.ProjectionType
        kind = projection.projection_type
        label = {types.Cylindrical: "Cylinder Unwrap",
                 types.Conic: "Cone Unroll"}.get(kind)

        if label is None:
            # Nothing to unroll: put the surface back before hiding the control,
            # so a value left over from the last projection cannot strand it.
            if self.slider_surface_unroll.GetValue() != 0:
                self.slider_surface_unroll.SetValue(0)
                self.cartographer.earth_canvas.surface_unroll = 0
                self.label_unwrap_value.SetLabel("0%")
                self.slider_ray_alpha.Enable(True)
            self.main_sizer.Show(self.row_unroll, False, recursive=True)
        else:
            self.label_unwrap.SetLabel(label)
            self.main_sizer.Show(self.row_unroll, True, recursive=True)

        self.Layout()

    def on_slider_change(self, event):
        # Get slider values
        slider_value = self.slider_ray_density.GetValue()
        # Map slider value to resolution, avoiding range < 1.0
        # Slider 0 → 0.0, Slider 1 → 1.0, Slider 29 → 7.5
        if slider_value == 0:
            resolution = 0.0
        else:
            resolution = 1.0 + (slider_value - 1) * 6.5 / 28.0
        ray_alpha = self.slider_ray_alpha.GetValue()
        unwrap_value = self.slider_surface_unroll.GetValue()

        # Update earth canvas values
        self.cartographer.earth_canvas.resolution = resolution
        self.cartographer.earth_canvas.ray_alpha = ray_alpha
        self.cartographer.earth_canvas.surface_unroll = unwrap_value

        # Update value labels
        self.label_ray_alpha_value.SetLabel(f"{ray_alpha}%")
        self.label_unwrap_value.SetLabel(f"{unwrap_value}%")

        # Disable ray sliders when cylinder is unwrapped (rays don't apply when unfolding)
        enable_rays = (unwrap_value == 0)
        self.slider_ray_alpha.Enable(enable_rays)

        self.cartographer.earth_canvas.Refresh()

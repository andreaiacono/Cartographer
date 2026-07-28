import wx
import math
from projections import equal_area, mercator, miller, lambert, albers


class DynamicParamsPanel(wx.Panel):
    """
    Dynamic parameter panel that shows/hides projection-specific controls
    based on the currently selected projection type.
    """

    def __init__(self, parent, cartographer=None):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.cartographer = cartographer

        # Set minimum size to ensure visibility
        self.SetMinSize(wx.Size(-1, 150))

        # Create main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a placeholder sizer for projection-specific controls
        self.projection_controls_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.projection_controls_sizer, flag=wx.EXPAND | wx.ALL, border=0)

        # Create all control groups (hidden initially)
        self._create_equal_area_controls()
        self._create_conic_controls()
        self._create_empty_controls()

        # Start with empty controls visible
        self.projection_controls_sizer.Add(self.empty_sizer, flag=wx.EXPAND)
        self.equal_area_sizer.ShowItems(False)
        self.conic_sizer.ShowItems(False)
        self.empty_sizer.ShowItems(True)

        # Separator (always visible)
        self.main_sizer.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=5)

        # Resolution slider section (always visible)
        self._create_resolution_controls()

        # Set the sizer and force layout
        self.SetSizer(self.main_sizer)
        self.Layout()
        self.Fit()

    def _create_equal_area_controls(self):
        """Create Equal Area projection controls (slider + radio buttons)"""
        self.equal_area_sizer = wx.GridBagSizer(4, 1)

        # Standard latitude slider
        self.projections_presets = {
            'Lambert': 0.0,
            'Behrmann': 30.0,
            'Trystan Edwards': 37.383,
            'Peters': 44.138,
            'Gall': 45.0,
            'Balthasart': 50.0
        }
        starting_projection = self.projections_presets['Peters']  # Default

        self.label_standard = wx.StaticText(self, label="\nStandard Latitude: " + str(round(starting_projection, 3)) + "°")
        self.equal_area_sizer.Add(self.label_standard, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        self.slider_lat = wx.Slider(
            self, minValue=0, maxValue=6000,
            value=int(starting_projection * 100),
            style=wx.SL_HORIZONTAL
        )
        self.equal_area_sizer.Add(self.slider_lat, pos=(1, 0), span=(1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        # Radio button presets
        self.radiobuttons = []
        style = wx.RB_GROUP
        for idx, preset_name in enumerate(self.projections_presets):
            rb = wx.RadioButton(self, wx.Window.NewControlId(), preset_name, style=style)
            self.equal_area_sizer.Add(rb, pos=(idx // 2 + 2, idx % 2), flag=wx.ALIGN_LEFT | wx.LEFT, border=10)
            rb.SetValue(self.projections_presets[preset_name] == starting_projection)
            self.radiobuttons.append(rb)
            self.Bind(wx.EVT_RADIOBUTTON, self._on_radiobutton_pressed, rb)
            style = 0

        # Bind slider event
        self.Bind(wx.EVT_SLIDER, self._on_slider_change, self.slider_lat)

        self.equal_area_sizer.AddGrowableCol(1)

        # Don't add to main sizer yet - we'll manage visibility dynamically

    def _create_conic_controls(self):
        """Create conic projection controls (two standard parallel sliders)"""
        self.conic_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self, label="\nStandard Parallels Configuration")
        font = title.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        self.conic_sizer.Add(title, flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        # Slider 1 (First Standard Parallel)
        self.label_phi1 = wx.StaticText(self, label="First Standard Parallel: 30°")
        self.conic_sizer.Add(self.label_phi1, flag=wx.LEFT | wx.TOP, border=5)

        self.slider_phi1 = wx.Slider(
            self, minValue=0, maxValue=88,
            value=30,
            style=wx.SL_HORIZONTAL
        )
        self.conic_sizer.Add(self.slider_phi1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)

        # Slider 2 (Second Standard Parallel)
        self.label_phi2 = wx.StaticText(self, label="Second Standard Parallel: 60°")
        self.conic_sizer.Add(self.label_phi2, flag=wx.LEFT | wx.TOP, border=5)

        self.slider_phi2 = wx.Slider(
            self, minValue=1, maxValue=89,
            value=60,
            style=wx.SL_HORIZONTAL
        )
        self.conic_sizer.Add(self.slider_phi2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)

        # Info text
        info = wx.StaticText(self, label="Tip: First parallel < Second parallel")
        info.SetForegroundColour(wx.Colour(100, 100, 100))
        self.conic_sizer.Add(info, flag=wx.LEFT | wx.BOTTOM, border=5)

        # Store IDs for event handling
        self.phi1_id = self.slider_phi1.GetId()
        self.phi2_id = self.slider_phi2.GetId()

        # Bind slider events
        self.Bind(wx.EVT_SLIDER, self._on_conic_slider_change, self.slider_phi1)
        self.Bind(wx.EVT_SLIDER, self._on_conic_slider_change, self.slider_phi2)

    def _create_empty_controls(self):
        """Create empty controls for projections without specific parameters"""
        self.empty_sizer = wx.BoxSizer(wx.VERTICAL)
        # No text label - just an empty sizer for spacing

    def _create_resolution_controls(self):
        """Create resolution slider (always visible)"""
        res_label = wx.StaticText(self, label="Resolution:")
        self.main_sizer.Add(res_label, flag=wx.LEFT | wx.TOP, border=5)

        res_sizer = wx.BoxSizer(wx.HORIZONTAL)
        res_sizer.Add(wx.StaticText(self, label="Low"), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=5)

        # Get current resolution value if cartographer is available
        if self.cartographer and hasattr(self.cartographer, 'projection_panel'):
            current_res = self.cartographer.projection_panel.resolution
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
        self.main_sizer.Add(res_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Bind slider event
        if self.cartographer:
            self.Bind(wx.EVT_SLIDER, self._on_resolution_change, self.slider_resolution)

    def _on_radiobutton_pressed(self, event):
        """Handle radio button preset selection"""
        rb = event.GetEventObject()
        val = self.projections_presets[rb.GetLabel()]
        self.slider_lat.SetValue(int(val * 100))
        self._update_equal_area_projection(val)

    def _on_slider_change(self, event):
        """Handle standard latitude slider changes"""
        # Uncheck all radio buttons when slider is moved manually
        for rb in self.radiobuttons:
            rb.SetValue(False)
        val = self.slider_lat.GetValue() / 100.0
        self._update_equal_area_projection(val)

    def _update_equal_area_projection(self, val):
        """Update Equal Area projection with new standard latitude"""
        self.label_standard.SetLabel("\nStandard Latitude: " + str(round(val, 3)) + "°")

        if self.cartographer is not None and hasattr(self.cartographer, 'projection_panel'):
            if hasattr(self.cartographer.projection_panel, 'projection'):
                projection = self.cartographer.projection_panel.projection
                if isinstance(projection, equal_area.EqualAreaProjection):
                    projection.set_standard_latitude(math.radians(val))
                    wx.CallAfter(self.cartographer.projection_panel.Refresh)

                    # Also refresh the earth canvas (3D cylinder visualization)
                    if hasattr(self.cartographer, 'earth_canvas'):
                        wx.CallAfter(self.cartographer.earth_canvas.Refresh)

        self.Layout()

    def _on_resolution_change(self, event):
        """Handle resolution slider changes."""
        if self.cartographer and hasattr(self.cartographer, 'projection_panel'):
            value = self.slider_resolution.GetValue()
            # Invert the slider: right = high resolution (1), left = low resolution (50)
            inverted_value = 51 - value
            self.cartographer.projection_panel.set_resolution(inverted_value)
            self.cartographer.projection_panel.compute_size()
            self.cartographer.projection_panel.OnDraw()
            wx.CallAfter(self.cartographer.projection_panel.Refresh)

    def _on_conic_slider_change(self, event):
        """Handle conic projection standard parallel slider changes."""
        # Ensure phi1 < phi2
        if event.GetEventObject().GetId() == self.phi1_id:
            if self.slider_phi1.GetValue() >= self.slider_phi2.GetValue():
                self.slider_phi2.SetValue(self.slider_phi1.GetValue() + 1)
        elif event.GetEventObject().GetId() == self.phi2_id:
            if self.slider_phi2.GetValue() <= self.slider_phi1.GetValue():
                self.slider_phi1.SetValue(self.slider_phi2.GetValue() - 1)

        phi1_val = self.slider_phi1.GetValue()
        phi2_val = self.slider_phi2.GetValue()

        # Update labels
        self.label_phi1.SetLabel(f"First Standard Parallel: {phi1_val}°")
        self.label_phi2.SetLabel(f"Second Standard Parallel: {phi2_val}°")

        # Update projection
        if self.cartographer and hasattr(self.cartographer, 'projection_panel'):
            projection = self.cartographer.projection_panel.projection
            if isinstance(projection, (lambert.LambertProjection, albers.AlbersProjection)):
                # Lambert expects radians, Albers might too
                if isinstance(projection, lambert.LambertProjection):
                    projection.set_standard_parallels(phi1_val, phi2_val)
                else:  # Albers
                    projection.set_standard_parallels(math.radians(phi1_val), math.radians(phi2_val))

                # Update earth canvas standard parallels (for visualization)
                if hasattr(self.cartographer, 'earth_canvas'):
                    self.cartographer.earth_canvas.set_standard_parallels(phi1_val, phi2_val)

                # Refresh both panels
                wx.CallAfter(self.cartographer.projection_panel.Refresh)
                wx.CallAfter(self.cartographer.earth_canvas.Refresh)

        self.Layout()

    def set_projection(self, projection_obj):
        """
        Update the panel to show controls appropriate for the given projection.

        Args:
            projection_obj: Instance of a projection class (EqualAreaProjection,
                          MercatorProjection, MillerProjection, etc.)
        """
        # Hide all control groups first
        self.projection_controls_sizer.Detach(self.empty_sizer)
        self.projection_controls_sizer.Detach(self.equal_area_sizer)
        self.projection_controls_sizer.Detach(self.conic_sizer)
        self.empty_sizer.ShowItems(False)
        self.equal_area_sizer.ShowItems(False)
        self.conic_sizer.ShowItems(False)

        # Detect projection type and show appropriate controls
        if isinstance(projection_obj, equal_area.EqualAreaProjection):
            # Show Equal Area controls
            self.projection_controls_sizer.Add(self.equal_area_sizer, flag=wx.EXPAND | wx.ALL, border=5)
            self.equal_area_sizer.ShowItems(True)

            # Initialize with current projection's standard latitude if available
            if hasattr(projection_obj, 'standard_latitude'):
                lat_degrees = math.degrees(projection_obj.standard_latitude)
                self.slider_lat.SetValue(int(lat_degrees * 100))
                self.label_standard.SetLabel("\nStandard Latitude: " + str(round(lat_degrees, 3)) + "°")

                # Check appropriate radio button if it matches a preset
                for rb in self.radiobuttons:
                    preset_val = self.projections_presets[rb.GetLabel()]
                    rb.SetValue(abs(preset_val - lat_degrees) < 0.01)

            # Set larger minimum height for Equal Area (needs space for slider + 6 radio buttons)
            required_height = 250

        elif isinstance(projection_obj, (lambert.LambertProjection, albers.AlbersProjection)):
            # Show Conic controls
            self.projection_controls_sizer.Add(self.conic_sizer, flag=wx.EXPAND | wx.ALL, border=5)
            self.conic_sizer.ShowItems(True)

            # Initialize with current projection's standard parallels if available
            if hasattr(projection_obj, 'phi1') and hasattr(projection_obj, 'phi2'):
                phi1_degrees = math.degrees(projection_obj.phi1)
                phi2_degrees = math.degrees(projection_obj.phi2)
                self.slider_phi1.SetValue(int(phi1_degrees))
                self.slider_phi2.SetValue(int(phi2_degrees))
                self.label_phi1.SetLabel(f"First Standard Parallel: {int(phi1_degrees)}°")
                self.label_phi2.SetLabel(f"Second Standard Parallel: {int(phi2_degrees)}°")

            # Set medium height for Conic controls
            required_height = 220

        else:
            # Show empty controls (Mercator, Miller, or other projections)
            self.projection_controls_sizer.Add(self.empty_sizer, flag=wx.EXPAND | wx.ALL, border=5)
            self.empty_sizer.ShowItems(True)

            # Set smaller minimum height for empty controls
            required_height = 150

        # Update panel minimum size
        self.SetMinSize(wx.Size(-1, required_height))

        # Force layout update
        self.Layout()
        self.Fit()

        # Update parent splitter to accommodate new height
        parent = self.GetParent()
        if parent and isinstance(parent, wx.SplitterWindow):
            parent.Layout()
            # Adjust sash position to show the required height from bottom
            wx.CallAfter(lambda: parent.SetSashPosition(-required_height - 20))

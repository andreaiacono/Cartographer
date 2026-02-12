import wx
import math


class ProjectionPanel(wx.Panel):
    """Panel that draws map projections with grid and shapes"""

    def __init__(self, parent, window_id, cartographer):
        wx.Panel.__init__(self, parent, window_id, style=wx.SUNKEN_BORDER)
        self.cartographer = cartographer

        # Add attributes needed by other panels
        self.resolution = 1
        self.width = 0
        self.height = 0
        self.zoom = 360  # Default zoom level
        self.mf = 1  # Multiplication factor
        self.tx = 0  # Translation X
        self.ty = 0  # Translation Y
        self.shapes = []  # Will hold shapefile data

        # Rotation attributes
        self.rotationx = 0.0
        self.rotationy = 0.0
        self.rotationz = 0.0
        self.posx = 0
        self.posy = 0
        self.posz = 0

        # Mouse tracking
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.is_dragging = False
        self.is_right_dragging = False

        # Grid drawing
        self.paint_grid = True  # Enable grid by default for testing
        self.paint_grid_specials = True  # Enable special lines (equator, tropics, etc.)
        self.parallel_number = 3  # Number of latitude lines (default: 3 = 45°N, 0°, 45°S)
        self.meridian_number = 6  # Number of longitude lines (default: 6)
        self.paint_frame = False  # Draw frame around projection
        self.draw_tissot = False  # Draw Tissot's indicatrix (distortion circles)
        self.resolution_scale = 50  # Maximum resolution value

        # Colors
        self.shapes_color = wx.Colour(140, 140, 220)  # Light blue for coastlines
        self.grid_color = wx.Colour(211, 211, 211)  # Light gray for grid

        # Cached rotation matrix elements (9 values from 3x3 rotation)
        self._rot_a = 1.0
        self._rot_b = 0.0
        self._rot_c = 0.0
        self._rot_d = 0.0
        self._rot_e = 1.0
        self._rot_f = 0.0
        self._rot_g = 0.0
        self._rot_h = 0.0
        self._rot_i = 1.0

        # Add dummy projection for EarthCanvas
        class DummyProjection:
            class ProjectionType:
                Cylindrical = 1
                PseudoCylindrical = 2
                Conic = 3
                Azimuthal = 4

            def __init__(self):
                self.projection_type = self.ProjectionType.Cylindrical

        self.projection = DummyProjection()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # TEST: Add mouse event bindings like the real panel
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def setShape(self, shapes):
        """Load shapes from shapefile"""
        self.shapes = shapes
        self.Refresh()

    def set_resolution(self, value):
        """Called by params panel slider"""
        self.resolution = value
        self.Refresh()

    def compute_size(self):
        """Real compute_size logic from ProjectionPanel"""
        self.width, self.height = self.GetSize()
        visible_height = self.zoom
        visible_width = self.zoom

        if self.width >= self.height:
            self.mf = self.height / float(visible_height)
            self.tx = self.mf * visible_width / 2 + (self.width - self.mf * visible_width) / 2
            self.ty = self.mf * visible_height / 2
        else:
            self.mf = self.width / float(visible_width)
            self.tx = self.mf * visible_width / 2
            self.ty = self.mf * visible_height / 2 + (self.height - self.mf * visible_height) / 2

    def _cache_rotation_matrix(self):
        """Precompute the 3x3 rotation matrix from rotation angles"""
        _radians = math.radians
        _cos = math.cos
        _sin = math.sin

        ch = _cos(_radians(self.rotationz))
        sh = _sin(_radians(self.rotationz))
        ca = _cos(_radians(self.rotationx))
        sa = _sin(_radians(self.rotationx))
        cb = _cos(_radians(self.rotationy))
        sb = _sin(_radians(self.rotationy))

        self._rot_a = ch * ca
        self._rot_b = sh * sb - ch * sa * cb
        self._rot_c = ch * sa * sb + sh * cb
        self._rot_d = sa
        self._rot_e = ca * cb
        self._rot_f = -ca * sb
        self._rot_g = -sh * ca
        self._rot_h = sh * sa * cb + ch * sb
        self._rot_i = -sh * sa * sb + ch * cb

    def OnDraw(self):
        """Called by params panel"""
        pass

    def set_paint_grid(self, value):
        self.paint_grid = value

    def set_paint_grid_specials(self, value):
        self.paint_grid_specials = value

    def set_paint_frame(self, value):
        self.paint_frame = value

    def set_draw_tissot(self, value):
        self.draw_tissot = value

    def set_parallel_number(self, value):
        self.parallel_number = value

    def set_meridian_number(self, value):
        self.meridian_number = value

    def set_shapes_color(self, color):
        self.shapes_color = color

    def set_grid_color(self, color):
        self.grid_color = color

    def draw_grid(self, dc):
        """Draw latitude and longitude grid lines"""
        if not self.projection:
            return

        # Calculate grid spacing
        meridian_spacing = 180 / (self.meridian_number + 1)
        parallel_spacing = 180 / (self.parallel_number + 1)

        # Build list of longitudes (meridians)
        longitudes = [0]
        for meridian in range(1, int(self.meridian_number) + 1):
            longitude = 180 - int(meridian_spacing * meridian)
            longitudes.append(longitude)

        # Build list of latitudes (parallels) starting from equator
        latitudes = []
        n = self.parallel_number

        if n == 1:
            # Only equator
            latitudes = [0]
        elif n == 2:
            # One at 30N and one at 30S
            latitudes = [30, -30]
        elif n % 2 == 1:  # Odd number: include equator
            # Divide hemisphere into equal parts
            count_per_hemisphere = (n - 1) // 2
            spacing = 90 / (count_per_hemisphere + 1)
            latitudes = [0]
            for i in range(1, count_per_hemisphere + 1):
                lat = spacing * i
                latitudes.extend([lat, -lat])
        else:  # Even number: exclude equator
            # Divide hemisphere into equal parts
            count_per_hemisphere = n // 2
            spacing = 90 / (count_per_hemisphere + 1)
            for i in range(1, count_per_hemisphere + 1):
                lat = spacing * i
                latitudes.extend([lat, -lat])

        # Draw regular grid
        if self.paint_grid:
            dc.SetPen(wx.Pen(self.grid_color, 1))
            for lon in longitudes:
                self.draw_meridian(lon, dc)
            for lat in latitudes:
                self.draw_parallel(lat, dc)

        # Draw special parallels (equator, tropics, arctic circles)
        if self.paint_grid_specials:
            # Tropics (±23.5°)
            dc.SetPen(wx.Pen((105, 255, 82), 1))
            for tropics in (-23.5, 23.5):
                self.draw_parallel(tropics, dc)

            # Arctic circles (±66.5°)
            dc.SetPen(wx.Pen((64, 245, 255), 1))
            for circles in (-66.5, 66.5):
                self.draw_parallel(circles, dc)

            # Equator (0°)
            dc.SetPen(wx.Pen((255, 150, 150), 1))
            self.draw_parallel(0, dc)

    def draw_parallel(self, latitude, dc):
        """Draw a latitude line (parallel)"""
        w_limit = self.width / 10
        h_limit = self.height / 10

        # Start at longitude -180
        points = []
        for lon_deg in range(-180, 181, 2):  # Every 2 degrees
            try:
                # Convert to radians
                lat_rad = math.radians(latitude)
                lon_rad = math.radians(-lon_deg)  # Negate for proper orientation

                # Apply rotation transformation (unit sphere)
                cos_lat = math.cos(lat_rad)
                sx = cos_lat * math.cos(lon_rad)
                sy = cos_lat * math.sin(lon_rad)
                sz = math.sin(lat_rad)

                # Apply rotation matrix
                px = self._rot_a * sx + self._rot_b * sy + self._rot_c * sz
                py = self._rot_d * sx + self._rot_e * sy + self._rot_f * sz
                pz = self._rot_g * sx + self._rot_h * sy + self._rot_i * sz

                # Convert back to lat/lon
                # px, py, pz are already normalized coordinates on unit sphere
                lat_eff = math.asin(pz)  # NO math.radians - pz is already normalized!
                lon_eff = math.atan2(py, px)  # Standard spherical coordinates

                # Project
                proj_x, proj_y = self.projection.get_coords(lon_eff, lat_eff)

                # To screen coordinates
                # Negate proj_x for correct east-west orientation
                # Negate proj_y because screen y increases downward
                x = int(-proj_x * self.mf + self.tx)
                y = int(-proj_y * self.mf + self.ty)

                # Check if point is too far from previous (discontinuity)
                if points and (abs(points[-1][0] - x) > w_limit or abs(points[-1][1] - y) > h_limit):
                    # Draw current segment and start new one
                    if len(points) > 1:
                        dc.DrawLines(points)
                    points = [(x, y)]
                else:
                    points.append((x, y))

            except:
                # Skip points that can't be projected
                if len(points) > 1:
                    dc.DrawLines(points)
                points = []

        # Draw final segment
        if len(points) > 1:
            dc.DrawLines(points)

    def draw_meridian(self, longitude, dc):
        """Draw a longitude line (meridian)"""
        w_limit = self.width / 10
        h_limit = self.height / 10

        # Start at latitude -180 and go to +180
        points = []
        for lat_deg in range(-180, 181, 2):  # Every 2 degrees
            try:
                # Convert to radians
                lat_rad = math.radians(lat_deg)
                lon_rad = math.radians(-longitude)  # Negate for proper orientation

                # Apply rotation transformation (unit sphere)
                cos_lat = math.cos(lat_rad)
                sx = cos_lat * math.cos(lon_rad)
                sy = cos_lat * math.sin(lon_rad)
                sz = math.sin(lat_rad)

                # Apply rotation matrix
                px = self._rot_a * sx + self._rot_b * sy + self._rot_c * sz
                py = self._rot_d * sx + self._rot_e * sy + self._rot_f * sz
                pz = self._rot_g * sx + self._rot_h * sy + self._rot_i * sz

                # Convert back to lat/lon
                # px, py, pz are already normalized coordinates on unit sphere
                lat_eff = math.asin(pz)  # NO math.radians - pz is already normalized!
                lon_eff = math.atan2(py, px)  # Standard spherical coordinates

                # Project
                proj_x, proj_y = self.projection.get_coords(lon_eff, lat_eff)

                # To screen coordinates
                # Negate proj_x for correct east-west orientation
                # Negate proj_y because screen y increases downward
                x = int(-proj_x * self.mf + self.tx)
                y = int(-proj_y * self.mf + self.ty)

                # Check if point is too far from previous (discontinuity)
                if points and (abs(points[-1][0] - x) > w_limit or abs(points[-1][1] - y) > h_limit):
                    # Draw current segment and start new one
                    if len(points) > 1:
                        dc.DrawLines(points)
                    points = [(x, y)]
                else:
                    points.append((x, y))

            except:
                # Skip points that can't be projected
                if len(points) > 1:
                    dc.DrawLines(points)
                points = []

        # Draw final segment
        if len(points) > 1:
            dc.DrawLines(points)

    # Mouse event handlers with drag rotation
    def OnMouseDown(self, event):
        self.last_mouse_x = event.GetX()
        self.last_mouse_y = event.GetY()

        if event.RightDown():
            self.is_right_dragging = True
        else:
            self.is_dragging = True

        self.CaptureMouse()

    def OnMouseUp(self, event):
        self.is_dragging = False
        self.is_right_dragging = False
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMouseMotion(self, event):
        if self.is_dragging or self.is_right_dragging:
            # Get mouse delta
            x = event.GetX()
            y = event.GetY()
            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y
            self.last_mouse_x = x
            self.last_mouse_y = y

            if self.is_dragging:
                # Left button: rotate X and Y axes
                self.rotationx -= dx * 0.5  # horizontal drag affects X (left/right)
                self.rotationy += dy * 0.5  # vertical drag affects Y (up/down)
                # Keep angles in reasonable range
                self.rotationy = self.rotationy % 360
                self.rotationx = max(-90, min(90, self.rotationx))

            elif self.is_right_dragging:
                # Right button: rotate Z axis (roll)
                self.rotationz -= dx * 0.5  # Match left drag sign
                self.rotationz = self.rotationz % 360

            # Update cartographer's rotation values (syncs with earth panel)
            if self.cartographer:
                self.cartographer.set_earth_coordinates(
                    self.rotationx, self.rotationy, self.rotationz
                )
                # Also update earth canvas using its set_earth_coordinates method
                # (it handles the axis mapping internally)
                if hasattr(self.cartographer, 'earth_canvas'):
                    self.cartographer.earth_canvas.set_earth_coordinates(
                        self.rotationx, self.rotationy, self.rotationz
                    )
                    self.cartographer.earth_canvas.Refresh()

            # Redraw
            self.Refresh()

    def OnMouseWheel(self, event):
        # Zoom in/out with mouse wheel
        rotation = event.GetWheelRotation()
        delta = rotation / 120.0  # Standard wheel delta

        # Adjust zoom (increase/decrease visible area)
        self.zoom *= (1.0 - delta * 0.1)
        self.zoom = max(50, min(500, self.zoom))  # Clamp zoom range

        # Recompute size with new zoom
        self.compute_size()
        self.Refresh()

    def OnSize(self, event):
        # Use the real compute_size logic
        self.compute_size()
        event.Skip()  # CRITICAL: propagate event
        self.Refresh()  # Trigger repaint

    def OnPaint(self, event):
        # Cache rotation matrix once per frame
        self._cache_rotation_matrix()

        # Create paint DC
        dc = wx.PaintDC(self)

        # Clear background
        dc.SetBackground(wx.Brush("white"))
        dc.Clear()

        # Draw grid if enabled
        if self.paint_grid or self.paint_grid_specials:
            self.draw_grid(dc)

        # Draw shapes if loaded (WITH Mercator projection)
        if self.shapes and self.projection:
            # Use the configured color for coastlines
            dc.SetPen(wx.Pen(self.shapes_color, 1))

            # Set central point for projection
            self.projection.set_central_point(self.rotationx, self.rotationy)

            for shape in self.shapes:
                points = shape.points
                if len(points) < 2:
                    continue

                # Draw every Nth point based on resolution
                step = max(1, int(self.resolution))

                # Calculate dynamic discontinuity threshold
                # Based on: zoom level, resolution/step, and screen size
                #
                # Logic:
                # - Smaller zoom (more zoomed in) = stricter threshold
                # - Larger step (skip more points) = more lenient threshold
                # - Account for the multiplication factor (mf) that scales to screen
                #
                # Expected point spacing in projection coordinates:
                # Points in shapefiles are roughly 1-2 degrees apart
                # With step=N, consecutive drawn points are N times farther
                point_spacing_deg = 1.5 * step  # Estimated degrees between drawn points

                # Convert to screen pixels and allow 3x margin for safety
                base_threshold = point_spacing_deg * self.mf * 3.0

                # Adjust based on zoom: smaller zoom = more zoomed in = stricter
                # zoom=360 is full world, zoom=180 is 2x zoomed in
                zoom_factor = self.zoom / 360.0

                # Final threshold: stricter when zoomed in, more lenient when zoomed out
                threshold = base_threshold * zoom_factor

                # Clamp to reasonable bounds (at least 10px, at most 1/4 of screen)
                min_threshold = 10.0
                max_threshold = min(self.width, self.height) / 4.0
                threshold = max(min_threshold, min(threshold, max_threshold))

                # Track multiple line segments (break on discontinuities)
                lines = []
                current_line = []
                prev_x = None
                prev_y = None

                for i in range(0, len(points), step):
                    lon, lat = points[i]

                    # Apply rotation and Mercator projection
                    try:
                        # Convert to radians
                        lon_rad = math.radians(-lon)  # Negate for proper orientation
                        lat_rad = math.radians(lat)

                        # Convert lat/lon to 3D Cartesian (unit sphere, radius = 1)
                        cos_lat = math.cos(lat_rad)
                        sx = cos_lat * math.cos(lon_rad)
                        sy = cos_lat * math.sin(lon_rad)
                        sz = math.sin(lat_rad)

                        # Apply rotation matrix (cached from _cache_rotation_matrix)
                        px = self._rot_a * sx + self._rot_b * sy + self._rot_c * sz
                        py = self._rot_d * sx + self._rot_e * sy + self._rot_f * sz
                        pz = self._rot_g * sx + self._rot_h * sy + self._rot_i * sz

                        # Convert back to effective lat/lon after rotation
                        # px, py, pz are already normalized coordinates on unit sphere (range -1 to 1)
                        lat_eff = math.asin(pz)  # NO math.radians - pz is already normalized!
                        lon_eff = math.atan2(py, px)  # Standard spherical coordinates

                        # Get projected coordinates using effective lat/lon
                        proj_x, proj_y = self.projection.get_coords(lon_eff, lat_eff)

                        # Transform to screen coordinates
                        # Negate proj_x for correct east-west orientation
                        # Negate proj_y because screen y increases downward
                        x = int(-proj_x * self.mf + self.tx)
                        y = int(-proj_y * self.mf + self.ty)

                        # Check for large jumps (edge wrapping/discontinuity)
                        if prev_x is not None:
                            dx = x - prev_x
                            dy = y - prev_y
                            # Use Euclidean distance for more accurate discontinuity detection
                            distance = math.sqrt(dx*dx + dy*dy)
                            if distance < threshold:
                                # Points are close, continue current line
                                current_line.append((x, y))
                            else:
                                # Large jump detected, start new line segment
                                if len(current_line) > 1:
                                    lines.append(current_line)
                                current_line = [(x, y)]
                        else:
                            # First point
                            current_line.append((x, y))

                        prev_x = x
                        prev_y = y

                    except:
                        # Skip points that can't be projected
                        # Start new line segment after error
                        if len(current_line) > 1:
                            lines.append(current_line)
                        current_line = []
                        prev_x = None
                        prev_y = None

                # Add final line segment
                if len(current_line) > 1:
                    lines.append(current_line)

                # Draw all line segments
                for line in lines:
                    if len(line) > 1:
                        dc.DrawLines(line)

        # Text drawing removed - no longer needed
        # REMOVED: SetStatusText breaks sliders!
        # self.cartographer.SetStatusText("Test status text - does this break sliders?")

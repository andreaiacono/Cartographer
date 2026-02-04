import math
import lib.euclid
import lib.shapefile
import wx


class ProjectionPanel(wx.Panel):

    def __init__(self, parent, window_id, cartographer):
        wx.Window.__init__(self, parent, window_id, style=wx.SUNKEN_BORDER)
        self.parent = parent
        self.cartographer = cartographer
        self.shapes = self.cartographer.getShape()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.rotationx = 0.0
        self.rotationy = 0.0
        self.rotationz = 0.0
        self.projection = None
        self.width = 0
        self.height = 0
        self.mf = 1
        self.tx = 0
        self.ty = 0

        self.resolution_scale = 50
        self.resolution = 2

        self.paint_grid = True
        self.paint_grid_specials = False
        self.paint_frame = False
        self.draw_tissot = False

        self.zoom = 360

        self.posx = 0
        self.posy = 0
        self.posz = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.lastx = 0
        self.lasty = 0
        self.lastz = 0

        self.parallel_number = 6
        self.meridian_number = 8

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

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def setShape(self, shape):
        self.shapes = shape

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
        self.z = self.lastz = self.y

    def OnMouseUp(self, evt):
        self.ReleaseMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and (evt.LeftIsDown() or evt.RightIsDown()):
            self.x, self.y = evt.GetPosition()

            if evt.RightIsDown():
                self.z = self.y
                self.posz += (self.z - self.lastz) / 3
                self.lastz = self.z
            else:
                self.posx -= (self.x - self.lastx) / 3
                self.posy += (self.y - self.lasty) / 3
                self.lastx = self.x
                self.lasty = self.y

            self.cartographer.rotationx = self.posx % 360
            self.cartographer.rotationy = self.posy % 360
            self.cartographer.rotationz = self.posz % 360
            self.cartographer.refresh()

            self.Refresh(False)

    def OnMouseWheel(self, evt):

        if evt.GetWheelRotation() < 0 and self.zoom < 360:
            self.zoom += self.zoom / 10
            self.compute_size()

        elif evt.GetWheelRotation() > 0 and self.zoom > 10:
            self.zoom -= self.zoom / 10
            self.compute_size()

        self.OnDraw()
        self.Refresh()

    def OnSize(self, event):
        self.compute_size()

    def OnPaint(self, event):
        self.dc = wx.PaintDC(self)
        self.OnDraw()

    def compute_size(self):
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
        """Precompute the 3x3 rotation matrix elements from current rotation angles.

        Matches euclid.Matrix4.new_rotate_euler(heading=rz, attitude=rx, bank=ry).
        Matrix layout: a,b,c / e,f,g / i,j,k maps to _rot_a.._rot_i.
        """
        _radians = math.radians
        _cos = math.cos
        _sin = math.sin
        # new_rotate_euler is called as (rz, rx, ry) -> heading, attitude, bank
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
        # Cache rotation matrix once per frame
        self._cache_rotation_matrix()

        dc = self.dc
        dc.DrawRectangle(0, 0, self.width, self.height)

        if self.projection is None:
            return
        meridian_spacing = 180 / (self.meridian_number + 1)
        parallel_spacing = 180 / (self.parallel_number + 1)

        longitudes = [0]
        for meridian in range(1, int(self.meridian_number) + 1):
            longitude = 180 - int(meridian_spacing * meridian)
            longitudes.append(longitude)

        latitudes = []
        for parallel in range(1, self.parallel_number + 1):
            latitude = 90 - int(parallel_spacing * parallel)
            latitudes.append(latitude)

        # draws the tissot indicatrix
        if self.draw_tissot:
            dc.SetPen(wx.Pen((255, 162, 162), 1))
            radius = self.zoom / 60
            for lon in longitudes:
                for lat in latitudes:
                    self.draw_circle(lat, lon, radius, 25, dc)
                    self.draw_circle(lat, -lon, radius, 25, dc)
            self.draw_circle(lat, 180, radius, 25, dc)

        # draws meridian and parallels
        if self.paint_grid:
            dc.SetPen(wx.Pen("light gray", 1))
            for lon in longitudes:
                self.draw_meridian(lon, True, dc)

            for lat in latitudes:
                self.draw_parallel(lat, True, dc)

        # draws special parallels (equator, tropics and arctic/antarctic circles)
        if self.paint_grid_specials:
            dc.SetPen(wx.Pen((105, 255, 82), 1))
            for tropics in (-23.5, 23.5):
                self.draw_parallel(tropics, True, dc)

            dc.SetPen(wx.Pen((64, 245, 255), 1))
            for circles in (-66.5, 66.5):
                self.draw_parallel(circles, True, dc)

            dc.SetPen(wx.Pen((255, 150, 150), 1))
            self.draw_parallel(0, True, dc)

        # draws the shapes of lands
        self.draw_projection(dc, self.width, self.height)

        # draws the frame
        if self.paint_frame:
            self.draw_frame(self.width, self.height, dc)

        latitude, longitude = self.transform_coords(0, 0)
        lat = str(round(latitude, 4))
        lon = str(round(longitude, 4))
        self.cartographer.SetStatusText("Map is centered on " + lat + "  -  " + lon + "")

    def draw_projection(self, dc, width, height):
        self.projection.set_central_point(self.rotationx, self.rotationy)
        dc.SetPen(wx.Pen((110, 110, 255), 1))

        # Cache attribute lookups in local variables
        mf = self.mf
        tx = self.tx
        ty = self.ty
        resolution = self.resolution
        projection_get_coords = self.projection.get_coords
        width_third = width / 3
        height_third = height / 3

        # Cache rotation matrix values locally
        ra, rb, rc = self._rot_a, self._rot_b, self._rot_c
        rd, re, rf = self._rot_d, self._rot_e, self._rot_f
        rg, rh, ri = self._rot_g, self._rot_h, self._rot_i

        # Cache math functions locally
        _radians = math.radians
        _cos = math.cos
        _sin = math.sin
        _asin = math.asin
        _atan2 = math.atan2

        # Inline transform function for speed
        def fast_transform(lat, lon):
            lat_r = _radians(lat)
            lon_r = _radians(lon)
            cos_lat = _cos(lat_r)
            x = cos_lat * _cos(lon_r)
            y = cos_lat * _sin(lon_r)
            z = _sin(lat_r)
            nx = ra * x + rb * y + rc * z
            ny = rd * x + re * y + rf * z
            nz = rg * x + rh * y + ri * z
            new_lat = _asin(_radians(nz))
            new_lon = _atan2(_radians(ny), _radians(nx))
            return -new_lon, -new_lat * 90

        for shape in self.shapes:
            parts = shape.parts
            points = shape.points
            num_parts = len(parts)
            num_points = len(points)

            for i in range(num_parts):
                start_index = parts[i]
                end_index = parts[i + 1] - 1 if i < num_parts - 1 else num_points - 1

                if end_index - start_index < resolution:
                    continue

                p = points[start_index]
                rx1, ry1 = fast_transform(p[1], -p[0])
                cx, cy = projection_get_coords(rx1, ry1)
                prev_x = int(cx * mf + tx)
                prev_y = int(cy * mf + ty)
                current_line = [(prev_x, prev_y)]
                lines = [current_line]

                for point in range(start_index + resolution, end_index, resolution):
                    p = points[point]
                    rx2, ry2 = fast_transform(p[1], -p[0])
                    cx, cy = projection_get_coords(rx2, ry2)
                    curr_x = int(cx * mf + tx)
                    curr_y = int(cy * mf + ty)

                    # Check for large jumps (edge wrapping)
                    dx = curr_x - prev_x
                    dy = curr_y - prev_y
                    if dx < width_third and dx > -width_third and dy < height_third and dy > -height_third:
                        current_line.append((curr_x, curr_y))
                    else:
                        current_line = [(curr_x, curr_y)]
                        lines.append(current_line)

                    prev_x, prev_y = curr_x, curr_y

                for data in lines:
                    if len(data) > 1:
                        dc.DrawLines(data)

    def draw_parallel(self, latitude, transform_coords, dc):
        # Cache locals
        mf = self.mf
        tx = self.tx
        ty = self.ty
        w_limit = self.width / 10
        h_limit = self.height / 10
        projection_get_coords = self.projection.get_coords
        transform = self.transform_coords
        _fabs = math.fabs
        _radians = math.radians

        # computes the first point
        lat, lon = transform(latitude, -180) if transform_coords else (_radians(latitude), _radians(-180))
        cx, cy = projection_get_coords(lat, lon)
        current_x = int(cx * mf + tx)
        current_y = int(cy * mf + ty)
        index = 0
        lines_list = [[(current_x, current_y)]]

        for point in range(-89, 89):
            lat, lon = transform(latitude, point * 2) if transform_coords else (_radians(latitude), _radians(point * 2))
            cx, cy = projection_get_coords(lat, lon)
            current_x = int(cx * mf + tx)
            current_y = int(cy * mf + ty)

            if _fabs(lines_list[index][-1][0] - current_x) < w_limit and _fabs(lines_list[index][-1][1] - current_y) < h_limit:
                lines_list[index].append((current_x, current_y))
            else:
                lines_list.append([(current_x, current_y)])
                index = index + 1

        for lines in lines_list:
            if len(lines) > 1:
                dc.DrawLines(lines)

    def draw_meridian(self, longitude, transform_coords, dc):
        # Cache locals
        mf = self.mf
        tx = self.tx
        ty = self.ty
        w_limit = self.width / 10
        h_limit = self.height / 10
        projection_get_coords = self.projection.get_coords
        transform = self.transform_coords
        _fabs = math.fabs
        _radians = math.radians

        # computes the first point
        lat, lon = transform(-180, longitude) if transform_coords else (_radians(-180), _radians(longitude))
        cx, cy = projection_get_coords(lat, lon)
        current_x = int(cx * mf + tx)
        current_y = int(cy * mf + ty)
        index = 0
        lines_list = [[(current_x, current_y)]]

        for point in range(-89, 89):
            lat, lon = transform(point * 2, longitude) if transform_coords else (_radians(point * 2), _radians(longitude))
            cx, cy = projection_get_coords(lat, lon)
            current_x = int(cx * mf + tx)
            current_y = int(cy * mf + ty)

            if _fabs(lines_list[index][-1][0] - current_x) < w_limit and _fabs(lines_list[index][-1][1] - current_y) < h_limit:
                lines_list[index].append((current_x, current_y))
            else:
                lines_list.append([(current_x, current_y)])
                index = index + 1

        for lines in lines_list:
            if len(lines) > 1:
                dc.DrawLines(lines)

    def draw_circle(self, center_x, center_y, radius, smoothness, dc):
        # Cache locals
        mf = self.mf
        tx = self.tx
        ty = self.ty
        w_limit = self.width / 10
        h_limit = self.height / 10
        projection_get_coords = self.projection.get_coords
        transform = self.transform_coords
        _fabs = math.fabs
        _sin = math.sin
        _cos = math.cos

        mp = 2 * math.pi / smoothness
        rx, ry = transform(center_x + _sin(mp) * radius, center_y + _cos(mp) * radius)
        cx, cy = projection_get_coords(rx, ry)
        current_x = int(cx * mf + tx)
        current_y = int(cy * mf + ty)

        index = 0
        lines_list = [[(current_x, current_y)]]

        for i in range(2, smoothness + 2):
            angle = i * mp
            rx, ry = transform(center_x + _sin(angle) * radius, center_y + _cos(angle) * radius)
            cx, cy = projection_get_coords(rx, ry)
            current_x = int(cx * mf + tx)
            current_y = int(cy * mf + ty)

            if _fabs(lines_list[index][-1][0] - current_x) < w_limit and _fabs(lines_list[index][-1][1] - current_y) < h_limit:
                lines_list[index].append((current_x, current_y))
            else:
                lines_list.append([(current_x, current_y)])
                index = index + 1

        for lines in lines_list:
            if len(lines) > 1:
                dc.DrawLines(lines)

    # draws a frame of the map
    def draw_frame(self, width, height, dc):
        self.projection.draw_frame(self, dc)

    def transform_coords(self, lat, lon):
        """Inlined transform: latlong->cartesian->rotation->cartesian->latlong with no intermediate objects."""
        _radians = math.radians
        lat_r = _radians(lat)
        lon_r = _radians(lon)

        # latlong_to_cartesian (inlined)
        cos_lat = math.cos(lat_r)
        x = cos_lat * math.cos(lon_r)
        y = cos_lat * math.sin(lon_r)
        z = math.sin(lat_r)

        # apply_rotation using cached matrix (inlined)
        ra = self._rot_a
        rb = self._rot_b
        rc = self._rot_c
        rd = self._rot_d
        re = self._rot_e
        rf = self._rot_f
        rg = self._rot_g
        rh = self._rot_h
        ri = self._rot_i
        nx = ra * x + rb * y + rc * z
        ny = rd * x + re * y + rf * z
        nz = rg * x + rh * y + ri * z

        # cartesian_to_latlong (inlined)
        new_lat = math.asin(_radians(nz))
        new_lon = math.atan2(_radians(ny), _radians(nx))
        return -new_lon, -new_lat * 90

    def latlong_to_cartesian(self, lat, lon):
        x = math.cos(math.radians(lat)) * math.cos(math.radians(lon))
        y = math.cos(math.radians(lat)) * math.sin(math.radians(lon))
        z = math.sin(math.radians(lat))
        return x, y, z

    def cartesian_to_latlong(self, x, y, z):
        lat = math.asin(math.radians(z))
        lon = math.atan2(math.radians(y), math.radians(x))
        return lat, lon

    def apply_rotation(self, rx, ry, rz, x, y, z):
        m = lib.euclid.Matrix4().new_rotate_euler(math.radians(rz), math.radians(rx), math.radians(ry))
        v = lib.euclid.Vector3(x, y, z)
        rv = m * v
        return rv.x, rv.y, rv.z

    def set_coordinates(self, rotationx, rotationy, rotationz):
        self.posx = self.rotationx = rotationx
        self.posy = self.rotationy = rotationy
        self.posz = self.rotationz = rotationz

    def set_zoom(self, value):
        self.zoom = value
        self.compute_size()

    def set_parallel_number(self, value):
        self.parallel_number = value

    def set_meridian_number(self, value):
        self.meridian_number = value

    def set_paint_grid_specials(self, paint_grid_specials):
        self.paint_grid_specials = paint_grid_specials

    def set_paint_grid(self, paint_grid):
        self.paint_grid = paint_grid

    def set_draw_tissot(self, draw_tissot):
        self.draw_tissot = draw_tissot

    def set_paint_frame(self, paint_frame):
        self.paint_frame = paint_frame

    def set_resolution(self, resolution):
        self.resolution = resolution

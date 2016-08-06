# coding=UTF-8
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

        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_SIZE(self, self.OnSize)
        self.rotationx = 0.0
        self.rotationy = 0.0
        self.rotationz = 0.0
        self.projection = None
        self.width = 0
        self.height = 0
        self.mf = 1

        self.resolution_scale = 40
        self.resolution = self.resolution_scale / 20

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

        self.parallel_degrees = 30
        self.meridian_degrees = 30

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
            self.refresh_window()

        elif evt.GetWheelRotation() > 0 and self.zoom > 10:
            self.zoom -= self.zoom / 10
            self.compute_size()
            self.refresh_window()

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

    def refresh_window(self):
        dc = wx.PaintDC(self)
        self.width, self.height = self.GetSizeTuple()
        self.draw_projection(dc, self.width, self.height)

    def OnPaint(self, event):
        self.refresh_window()

    def OnSize(self, event):
        self.compute_size()
        self.refresh_window()

    def compute_size(self):
        self.width, self.height = self.GetSizeTuple()
        visible_height = self.zoom
        visible_width = self.zoom

        if self.width >= self.height:
            self.mf = self.height / float(visible_height)
            self.tx = self.mf * visible_width / 2 + (self.width - self.mf * visible_width) / 2
            self.ty = self.mf * visible_height / 2
            # self.proj_width = self.width - self.mf * visible_width - 10
            # self.proj_height = self.height - 10
        else:
            self.mf = self.width / float(visible_width)
            self.tx = self.mf * visible_width / 2
            self.ty = self.mf * visible_height / 2 + (self.height - self.mf * visible_height) / 2
            # self.proj_width = self.width - 10
            # self.proj_height = self.height - self.mf * visible_height - 10

    def draw_parallel(self, latitude, transform_coords, dc):

        # computes the first point
        lat, lon = self.transform_coords(latitude, -180) if transform_coords else (math.radians(latitude), math.radians(-180))
        last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
        last_x += self.tx
        last_y += self.ty
        first_x = last_x
        first_y = last_y

        for point in range(-89, 89):
            # if point % self.grid_resolution == 0:
            lat, lon = self.transform_coords(latitude, point * 2) if transform_coords else (math.radians(latitude), math.radians(point * 2))
            x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
            x += self.tx
            y += self.ty

            if math.fabs(y - last_y) < self.height / 10 and math.fabs(x - last_x) < self.width / 10:
                dc.DrawLine(x, y, last_x, last_y)

            last_x, last_y = x, y

        # draws the last line
        dc.DrawLine(x, y, first_x, first_y)

    def draw_meridian(self, longitude, transform_coords, dc):

        # computes the first point
        lat, lon = self.transform_coords(-180, longitude) if transform_coords else (math.radians(-180), math.radians(longitude))
        last_x, last_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
        last_x += self.tx
        last_y += self.ty
        first_x = last_x
        first_y = last_y

        for point in range(-89, 89):
            # if point % self.grid_resolution == 0:
            #     pts.append(point)
            lat, lon = self.transform_coords(point * 2, longitude) if transform_coords else (math.radians(point * 2), math.radians(longitude))
            x, y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
            x += self.tx
            y += self.ty

            if math.fabs(y - last_y) < self.height / 10 and math.fabs(x - last_x) < self.width / 10:
                dc.DrawLine(x, y, last_x, last_y)
                # wr_pts.append(point)

            last_x, last_y = x, y

        # draws the last line
        dc.DrawLine(x, y, first_x, first_y)

    def draw_projection(self, dc, width, height):
        dc.BeginDrawing
        dc.SetBrush(wx.Brush((255, 255, 255)))
        dc.DrawRectangle(-1, -1, width, height)
        dc.SetBrush(wx.Brush((255, 210, 210)))

        # draws the tissot indicatrix
        if self.draw_tissot:
            dc.SetPen(wx.Pen((255, 162, 162), 1))
            meridian_number = 360 / self.meridian_degrees
            parallel_number = 360 / self.parallel_degrees
            for meridian in range(1, int(meridian_number)):
                for parallel in range(1, int(parallel_number)):
                    self.draw_circle(meridian * self.meridian_degrees, 180 - parallel * self.parallel_degrees,
                                     self.zoom / 40, 25, dc)

        # draws meridian and parallels
        if self.paint_grid:
            dc.SetPen(wx.Pen("light gray", 1))
            meridian_number = 360 / self.meridian_degrees
            for meridian in range(1, int(meridian_number)):
                self.draw_meridian(meridian * self.meridian_degrees, True, dc)

            parallel_number = 360 / self.parallel_degrees
            for parallel in range(1, int(parallel_number)):
                self.draw_parallel(180 - parallel * self.parallel_degrees, True, dc)

        # draws special parallels (equator, tropics and arctic/antarctic circles)
        if self.paint_grid_specials:
            dc.SetPen(wx.Pen("light green", 1))
            for tropics in (-23.5, 23.5):
                self.draw_parallel(tropics, True, dc)

            dc.SetPen(wx.Pen("light blue", 1))
            for circles in (-66.5, 66.5):
                self.draw_parallel(circles, True, dc)

            dc.SetPen(wx.Pen("dark red", 1))
            self.draw_parallel(0, True, dc)

        # draws the shapes of lands
        dc.SetPen(wx.Pen("dark blue", 1))
        for shape in self.shapes:
            for i in range(len(shape.parts)):
                start_index = shape.parts[i]
                if i < len(shape.parts) - 1:
                    end_index = shape.parts[i + 1] - 1
                else:
                    end_index = len(shape.points) - 1

                rx1, ry1 = self.transform_coords(shape.points[start_index][1], -shape.points[start_index][0])
                start_x, start_y = tuple(val * self.mf for val in self.projection.get_coords(rx1, ry1))

                for point in range(start_index + 1, end_index):

                    if point % self.resolution == 0:

                        rx2, ry2 = self.transform_coords(shape.points[point + 1][1], -shape.points[point + 1][0])
                        end_x, end_y = tuple(val * self.mf for val in self.projection.get_coords(rx2, ry2))

                        if math.fabs(start_x - end_x) < width / 10 and math.fabs(start_y - end_y) < height / 10:
                            dc.DrawLine(start_x + self.tx, start_y + self.ty, end_x + self.tx, end_y + self.ty)

                        start_x, start_y = end_x, end_y

        # draws the frame
        if self.paint_frame:
            self.draw_frame(width, height, dc)

        dc.EndDrawing

        latitude, longitude = self.transform_coords(0, 0)
        lat = str(round(latitude, 4))
        lon = str(round(longitude, 4))
        self.cartographer.SetStatusText("Map is centered on " + lat + "°  -  " + lon + "°")

    def draw_circle(self, center_x, center_y, radius, smoothness, dc):

        mp = 2 * math.pi / smoothness
        rx, ry = self.transform_coords(center_x + math.sin(mp) * radius, center_y + math.cos(mp) * radius)
        old_x, old_y = tuple(val * self.mf for val in self.projection.get_coords(rx, ry))
        old_x += self.tx
        old_y += self.ty
        first_x = old_x
        first_y = old_y
        fill = True

        rx, ry = self.transform_coords(center_x, center_y)
        transformed_center_x, transformed_center_y = tuple(val * self.mf for val in self.projection.get_coords(rx, ry))
        transformed_center_x += self.tx
        transformed_center_y += self.ty

        for i in range(2, smoothness):
            rx, ry = self.transform_coords(center_x + math.sin(i * mp) * radius, center_y + math.cos(i * mp) * radius)
            x, y = tuple(val * self.mf for val in self.projection.get_coords(rx, ry))
            x += self.tx
            y += self.ty
            if math.fabs(x - old_x) < self.width / 10 and math.fabs(y - old_y) < self.height / 10:
                dc.DrawLine(old_x, old_y, x, y)
            else:
                fill = False
                pass
            old_x = x
            old_y = y

        if math.fabs(x - first_x) < self.width / 10 and math.fabs(y - first_y) < self.height / 10:
            dc.DrawLine(x, y, first_x, first_y)
            if fill:
                pass
                dc.FloodFill(transformed_center_x, transformed_center_y, (255, 162, 162), wx.FLOOD_BORDER)
        if not fill:
            pass

    # draws a frame of the map
    def draw_frame(self, width, height, dc):
        self.projection.draw_frame(self, dc)

    def transform_coords(self, lat, lon):
        x, y, z = self.latlong_to_cartesian(lat, lon)
        x, y, z = self.apply_rotation(self.rotationx, self.rotationy, self.rotationz, x, y, z)
        new_lat, new_lon = self.cartesian_to_latlong(x, y, z)
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

    def set_parallel_degrees(self, value):
        self.parallel_degrees = value

    def set_meridian_degrees(self, value):
        self.meridian_degrees = value

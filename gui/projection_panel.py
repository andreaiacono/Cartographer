# coding=UTF-8
import math

import lib.euclid
import lib.shapefile
import wx

from PIL.Image import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx import glcanvas
from wx.glcanvas import GLCanvas

class ProjectionPanel(wx.Panel):
    def __init__(self, parent, window_id, cartographer):
        # GLCanvas.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, attribList=[wx.glcanvas.WX_GL_DOUBLEBUFFER])
        # self.context = glcanvas.GLContext(self)
        #
        # self.init = False

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

        self.resolution_scale = 50
        self.resolution = self.resolution_scale / 5

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

        self.refresh_window()
        self.Refresh()

    def InitGL(self):
        glClearColor(1, 1, 1, 1)
        self.init = True

    def OnPaint(self, event):
        # self.SetCurrent(self.context)
        # if not self.init:
        #     self.InitGL()
        # self.OnDraw()

        self.dc = wx.PaintDC(self)
        # self.dc = wx.GraphicsContext.Create(wx.PaintDC(self))
        self.refresh_window()

    # def OnDraw(self, *args, **kwargs):
    #     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #
    #     glLineWidth(0.8)
    #     glColor4f(0.0, 0.0, 0.8, 0.3)
    #
    #     # lines = [0.0, 0.0, 0.5, 0.5]
    #     # glEnableClientState(GL_VERTEX_ARRAY)
    #     # glVertexPointer(4, GL_FLOAT, 0, len(lines))
    #     # glDrawArrays(GL_LINES, 0, len(lines))
    #     # glDisableClientState(GL_VERTEX_ARRAY)
    #
    #     lines = [0.0, 0.0, 0.5, 0.5, -1.0, -1.0]
    #     glEnableClientState(GL_VERTEX_ARRAY)
    #     glVertexPointer(4, GL_FLOAT, 0, len(lines))
    #     glDrawArrays(GL_LINES, 0, len(lines))
    #     glDisableClientState(GL_VERTEX_ARRAY)
    #
    #     self.SwapBuffers()

    def OnSize(self, event):
        self.compute_size()
        # size = self.GetClientSize()
        # if not size == (0, 0):
        #     glViewport(0, 0, size[0], size[1])
        #     glMatrixMode(GL_PROJECTION)
        #     glLoadIdentity()
        #     gluPerspective(45.0, float(size[0]) / float(size[1]), 0.1, 100.0)
        #     glMatrixMode(GL_MODELVIEW)

        # glViewport(0, 0, self.width, self.height)

    def refresh_window(self):
        self.width, self.height = self.GetSize()
        self.draw_projection(self.dc, self.width, self.height)

    def compute_size(self):
        self.width, self.height = self.GetSize()
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

    def draw_projection(self, dc, width, height):
        dc.DrawRectangle(0, 0, width, height)
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

            # dc.SetPen(wx.Pen("dark grey", 1))
            dc.SetPen(wx.Pen((64, 245, 255), 1))
            for circles in (-66.5, 66.5):
                self.draw_parallel(circles, True, dc)

        # draws the shapes of lands
        self.projection.set_central_point(self.rotationx, self.rotationy)
        dc.SetPen(wx.Pen((110, 110, 255), 1))
        for shape in self.shapes:
            for i in range(len(shape.parts)):
                start_index = shape.parts[i]
                if i < len(shape.parts) - 1:
                    end_index = shape.parts[i + 1] - 1
                else:
                    end_index = len(shape.points) - 1

                if end_index - start_index < self.resolution:
                    continue
                rx1, ry1 = self.transform_coords(shape.points[start_index][1], -shape.points[start_index][0])
                current_x, current_y = tuple(int(val * self.mf) for val in self.projection.get_coords(rx1, ry1))
                current_x += self.tx
                current_y += self.ty
                index = 0
                lines = [[(current_x, current_y)]]

                for point in range(start_index + 1, end_index):
                    if point % self.resolution == 0:
                        rx2, ry2 = self.transform_coords(shape.points[point + 1][1], -shape.points[point + 1][0])
                        current_x, current_y = tuple(int(val * self.mf) for val in self.projection.get_coords(rx2, ry2))
                        current_x += self.tx
                        current_y += self.ty
                        if math.fabs(lines[index][-1][0] - current_x) < width / 3 and math.fabs(lines[index][-1][1] - current_y) < height / 3:
                            lines[index].append((current_x, current_y))
                        else:
                            lines.append([(current_x, current_y)])
                            index = index + 1

                for data in lines:
                    if len(data) > 1:
                        dc.DrawLines(data)

        # draws the frame
        if self.paint_frame:
            self.draw_frame(width, height, dc)

        latitude, longitude = self.transform_coords(0, 0)
        lat = str(round(latitude, 4))
        lon = str(round(longitude, 4))
        self.cartographer.SetStatusText("Map is centered on " + lat + "  -  " + lon + "")

    def draw_parallel(self, latitude, transform_coords, dc):
        # computes the first point
        lat, lon = self.transform_coords(latitude, -180) if transform_coords else (math.radians(latitude), math.radians(-180))
        current_x, current_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
        current_x = int(current_x + self.tx)
        current_y = int(current_y + self.ty)
        index = 0
        lines_list = [[(current_x, current_y)]]

        for point in range(-89, 89):
            # if point % self.grid_resolution == 0:
            lat, lon = self.transform_coords(latitude, point * 2) if transform_coords else (math.radians(latitude), math.radians(point * 2))
            current_x, current_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
            current_x = int(current_x + self.tx)
            current_y = int(current_y + self.ty)

            if math.fabs(lines_list[index][-1][0] - current_x) < self.width / 10 and math.fabs(lines_list[index][-1][1] - current_y) < self.height / 10:
                lines_list[index].append((current_x, current_y))
            else:
                lines_list.append([(current_x, current_y)])
                index = index + 1

        for lines in lines_list:
            if len(lines) > 1:
                dc.DrawLines(lines)

    def draw_meridian(self, longitude, transform_coords, gc):
        # computes the first point
        lat, lon = self.transform_coords(-180, longitude) if transform_coords else (math.radians(-180), math.radians(longitude))
        current_x, current_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
        current_x = int(current_x + self.tx)
        current_y = int(current_y + self.ty)
        index = 0
        lines_list = [[(current_x, current_y)]]

        for point in range(-89, 89):
            lat, lon = self.transform_coords(point * 2, longitude) if transform_coords else (math.radians(point * 2), math.radians(longitude))
            current_x, current_y = tuple(val * self.mf for val in self.projection.get_coords(lat, lon))
            current_x = int(current_x + self.tx)
            current_y = int(current_y + self.ty)

            if math.fabs(lines_list[index][-1][0] - current_x) < self.width / 10 and math.fabs(lines_list[index][-1][1] - current_y) < self.height / 10:
                lines_list[index].append((current_x, current_y))
            else:
                lines_list.append([(current_x, current_y)])
                index = index + 1

        for lines in lines_list:
            if len(lines) > 1:
                gc.DrawLines(lines)

    def draw_circle(self, center_x, center_y, radius, smoothness, dc):
        mp = 2 * math.pi / smoothness
        rx, ry = self.transform_coords(center_x  + math.sin(mp) * radius, center_y + math.cos(mp) * radius)
        current_x, current_y = tuple(val * self.mf for val in self.projection.get_coords(rx, ry))
        current_x = int(current_x + self.tx)
        current_y = int(current_y + self.ty)

        index = 0
        lines_list = [[(current_x, current_y)]]

        for i in range(2, smoothness + 2):
            rx, ry = self.transform_coords(center_x + math.sin(i * mp) * radius, center_y + math.cos(i * mp) * radius)
            current_x, current_y = tuple(val * self.mf for val in self.projection.get_coords(rx, ry))
            current_x = int(current_x + self.tx)
            current_y = int(current_y + self.ty)

            if math.fabs(lines_list[index][-1][0] - current_x) < self.width / 10 and math.fabs(lines_list[index][-1][1] - current_y) < self.height / 10:
                lines_list[index].append((current_x, current_y))
            else:
                lines_list.append([(current_x, current_y)])
                index = index + 1

        for lines in lines_list:
            if len(lines) > 1:
                dc.DrawLines(lines)

        # TO FIX
        # rx, ry = self.transform_coords(center_x, center_y)
        # transformed_center_x, transformed_center_y = tuple(val * self.mf for val in self.projection.get_coords(rx, ry))
        # transformed_center_x += self.tx
        # transformed_center_y += self.ty
        # dc.FloodFill(transformed_center_x, transformed_center_y, (255, 162, 162), wx.FLOOD_SURFACE)

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

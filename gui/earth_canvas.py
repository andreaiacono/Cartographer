import wx

from PIL.Image import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx import glcanvas
from wx.glcanvas import GLCanvas


class EarthCanvas(GLCanvas):

    def __init__(self, parent, cartographer):
        GLCanvas.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, attribList=[wx.glcanvas.WX_GL_DOUBLEBUFFER])
        self.context = glcanvas.GLContext(self)
        self.cartographer = cartographer
        self.init = False

        self.posx = 0
        self.posy = 0
        self.posz = 0
        self.earthx = 0
        self.earthy = 0
        self.earthz = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.lastx = 0
        self.lasty = 0
        self.lastz = 0

        self.size = None
        self.view_distance = -15.0
        self.earth_radius = 2.0
        self.standard_parallel1 = 15
        self.standard_parallel2 = 15
        self.earth_texture = None
        self.earth_quad = None
        self.plain_texture = None
        self.plain_quad = None
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def InitGL(self):
        # the earth texture
        image = open("textures/earth_grid.jpg")
        ix = image.size[0]
        iy = image.size[1]
        image = image.tobytes("raw", "RGBX", 0, -1)
        self.earth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        self.earth_quad = gluNewQuadric()
        gluQuadricNormals(self.earth_quad, GLU_SMOOTH)
        gluQuadricTexture(self.earth_quad, GL_TRUE)

        # the texture of the solid enclosing the earth
        image2 = open("textures/plain_texture.png")
        ix = image2.size[0]
        iy = image2.size[1]
        image2 = image2.tobytes("raw", "RGBX", 0, -1)
        self.plain_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.plain_texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image2)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        self.plain_quad = gluNewQuadric()
        gluQuadricNormals(self.plain_quad, GLU_SMOOTH)
        gluQuadricTexture(self.plain_quad, GL_TRUE)

    def OnSize(self, event):
        size = self.size = self.GetClientSize()
        if not size == (0, 0):
            glViewport(0, 0, size[0], size[1])
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, float(size[0]) / float(size[1]), 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)

    def OnPaint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0.0, 0.0, self.view_distance)
        glRotatef(self.posy, 1.0, 0.0, 0.0)
        glRotatef(self.posx, 0.0, 0.0, 1.0)
        glRotatef(self.posz, 0.0, 1.0, 0.0)

        if self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Cylindrical or \
                        self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.PseudoCylindrical:
            cyl_size = 6
            glPushMatrix()
            glTranslatef(0.0, 0.0, -self.earth_radius * cyl_size / 2)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.2)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            gluCylinder(self.plain_quad, self.earth_radius * 1.01, self.earth_radius * 1.01, self.earth_radius * cyl_size, 32, 64)
            glPopMatrix()
            self.draw_projection_cylindric_lines()
            glDisable(GL_BLEND)
        elif self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Conic:
            glPushMatrix()
            glTranslatef(0.0, 0.0, -self.earth_radius)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.5)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            gluCylinder(self.plain_quad, self.earth_radius * self.standard_parallel1 / 10, 0, self.earth_radius * 3, 32, 64)
            glDisable(GL_BLEND)
            glPopMatrix()
        elif self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Azimuthal:
            glPushMatrix()
            disk_size = 3
            glTranslatef(0.0, 0.0, -self.earth_radius)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.5)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            gluDisk(self.plain_quad, 0, self.earth_radius * disk_size, 32, 64)
            self.draw_circle(0, 0.01, 6)
            glPopMatrix()
            glDisable(GL_BLEND)
            self.draw_projection_azimuthal_lines()

        # draws the earth sphere
        glPushMatrix()
        glRotatef(self.earthy, 1.0, 0.0, 0.0)
        glRotatef(self.earthx, 0.0, 0.0, 1.0)
        glRotatef(self.earthz, 0.0, 1.0, 0.0)
        glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        gluSphere(self.earth_quad, self.earth_radius, 32, 32)
        glEnable(GL_TEXTURE_2D)
        glPopMatrix()

        self.SwapBuffers()

    def draw_projection_cylindric_lines(self):
        # draws lines from earth to projection solid
        glLineWidth(1.0)
        glBegin(GL_LINES)
        glColor4f(0.0, 0.0, 1.0, 0.3)
        num = 9
        r = self.earth_radius
        if self.earthx == 0:
            self.earthx = 0.0001
        phi = math.atan(math.radians(self.earthy / math.radians(self.earthx)))
        den = math.radians(self.earthz / r)
        if den < -1:
            den = -1
        elif den > 1:
            den = 1
        theta = math.acos(den)
        angle = 2 * math.pi / num
        for i in range (0, num):
            for j in range (0, num):
                x = 0   # r * math.sin((theta + i) * angle) * math.cos((phi + j) * angle)
                y = 0   # r * math.sin((theta + i) * angle) * math.sin((phi + j) * angle)
                z = 0   # r * math.cos((theta + i) * angle)
                x2 = r * math.cos(phi + j * angle)
                y2 = r * math.sin(phi + j * angle)
                z2 = r * math.tan(theta + i * angle)
                glVertex3f(x, y, z)
                glVertex3f(x2, y2, z2)
        glEnd()

    def draw_projection_azimuthal_lines(self):
        # draws lines from earth to projection solid
        glLineWidth(1.0)
        glBegin(GL_LINES)
        glColor3f(0.0, 0.0, 1.0)
        num = 9
        r = self.earth_radius
        if self.earthx == 0:
            self.earthx = 0.0001
        phi = math.atan(math.radians(self.earthy / math.radians(self.earthx)))
        den = math.radians(self.earthz / r)
        if den < -1:
            den = -1
        elif den > 1:
            den = 1
        theta = math.acos(den)
        angle = 2 * math.pi / num
        for i in range (0, num):
            for j in range (0, num // 2):
                x = 0   # r * math.sin((theta + i) * angle) * math.cos((phi + j) * angle)
                y = 0   # r * math.sin((theta + i) * angle) * math.sin((phi + j) * angle)
                z = 0   # r * math.cos((theta + i) * angle)
                x2 = r * j * math.cos(phi + i * angle)
                y2 = r * j * math.sin(phi + i * angle)
                z2 = -self.earth_radius
                glVertex3f(x, y, z)
                glVertex3f(x2, y2, z2)
        glEnd()

    def set_earth_coordinates(self, x, y, z):
        self.earthx = x
        self.earthy = y
        self.earthz = z

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
        self.z = self.lastz = self.y

    def OnMouseUp(self, evt):
        self.ReleaseMouse()

    def OnMouseWheel(self, evt):
        if evt.GetWheelRotation() < 0 and self.view_distance > -50:
            self.view_distance += self.view_distance / 10
        elif evt.GetWheelRotation() > 0 and self.view_distance < -4:
            self.view_distance -= self.view_distance / 10
        self.Refresh()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and (evt.LeftIsDown() or evt.RightIsDown()):
            self.x, self.y = evt.GetPosition()

            if evt.RightIsDown():
                self.z = self.y
                self.posz += self.z - self.lastz
                self.lastz = self.z
            else:
                self.posx -= self.x - self.lastx
                self.posy += self.y - self.lasty
                self.lastx = self.x
                self.lasty = self.y

            self.Refresh()

    def set_standard_parallels(self, value1, value2):
        self.standard_parallel1 = value1
        self.standard_parallel2 = value2

    def draw_circle(self, y, radius, smoothness):
        mp = 2 * math.pi / smoothness
        glPushMatrix()
        glDisable(GL_TEXTURE_2D)
        glLineWidth(1.0)
        glTranslatef(0.0, 0.0, y)
        glColor4f(1.0, 0.0, 0.0, 1)

        old_x = math.sin(mp) * radius
        old_z = math.cos(mp) * radius

        glBegin(GL_LINES)
        for i in range(2, smoothness):
            x = math.sin(i * mp) * radius
            z = math.cos(i * mp) * radius

            glVertex3f(old_x, old_z, 0)
            glVertex3f(x, z, 0)
            old_x = x
            old_z = z

        glVertex3f(old_x, old_z, 0)
        glVertex3f(math.sin(mp) * radius, math.cos(mp) * radius, 0)
        glEnd()

        glEnable(GL_TEXTURE_2D)
        glPopMatrix()

            
# if __name__ == '__main__':
#
#     app = wx.App()
#     frame = wx.Frame(None, -1, 'test', wx.DefaultPosition, wx.Size(400, 400))
#     panel = EarthCanvas(frame, None)
#
#     frame.Show()
#     app.MainLoop()

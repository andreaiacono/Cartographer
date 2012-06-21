#Uncomment if you have multiple wxWidgets versions
#import wxversion
#wxversion.select('2.8')

import math, wx

from wx.glcanvas import GLCanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Image import *


class Settings(GLCanvas):

	def __init__(self, parent, cartographer):
		GLCanvas.__init__(self, parent, -1)
		self.init = False
		glutInit(sys.argv)
		self.cartographer = cartographer
		self.posx = 0
		self.posy = 0
		self.x = 0
		self.y = 0
		self.lastx = 0
		self.lasty = 0
		self.size = None
		#self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

	
	def InitGL(self):
		self.init = True
		self.load_textures()
		glEnable(GL_TEXTURE_2D)
		glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
		glClearDepth(1.0)                   # Enables Clearing Of The Depth Buffer
		glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
		glEnable(GL_DEPTH_TEST)             # Enables Depth Testing
		glShadeModel(GL_SMOOTH)             # Enables Smooth Color Shading
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()                    # Reset The Projection Matrix
		width, height = self.GetClientSize()
		gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)
		glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
		glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
		glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 0.0, 2.0, 1.0))
		glEnable(GL_LIGHT0)


	def load_textures(self):

		image = open("textures/earth_low.jpg")
		ix = image.size[0]
		iy = image.size[1]
		image = image.tostring("raw", "RGBX", 0, -1)
		self.textures = glGenTextures(2)
		glBindTexture(GL_TEXTURE_2D, int(self.textures[0]))
##		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
##		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
##		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
##		
		glPixelStorei(GL_UNPACK_ALIGNMENT,1)
		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
	
		self.quadratic = gluNewQuadric()
		gluQuadricNormals(self.quadratic, GLU_SMOOTH)
		gluQuadricTexture(self.quadratic, GL_TRUE)


	def OnSize(self, event):
		size = self.size = self.GetClientSize()
		glViewport(0, 0, size[0], size[1])
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, float(size[0])/float(size[1]), 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)


	def OnPaint(self, event):
		self.SetCurrent()
		if not self.init:
			self.InitGL()

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()
		glTranslatef(0.0,0.0,-5.0)
		glRotatef(self.posy, 1.0, 0.0, 0.0);
		glRotatef(self.posx, 0.0, 0.0, 1.0);
		glBindTexture(GL_TEXTURE_2D, int(self.textures[0]))
		gluSphere(self.quadratic,1.8,32,32)
		self.SwapBuffers()
		
	def OnMouseDown(self, evt):
		self.CaptureMouse()
		self.x, self.y = self.lastx, self.lasty = evt.GetPosition()

	def OnMouseUp(self, evt):
		self.ReleaseMouse()

	def OnMouseMotion(self, evt):
		if evt.Dragging() and evt.LeftIsDown():
			self.x, self.y = evt.GetPosition()
			self.posx += self.x - self.lastx
			self.posy += self.y - self.lasty
			self.lastx = self.x
			self.lasty = self.y
			self.cartographer.centerx = self.posx
			self.cartographer.centery = self.posy
			self.cartographer.refresh()
			print "x=" + str(self.posx) + " y=" + str(self.posy)
			self.Refresh(False)



if __name__ == '__main__':

	app = wx.App()
	frame = wx.Frame(None, -1, 'test', wx.DefaultPosition, wx.Size(400,400))
	panel = Settings(frame, None)

	frame.Show()
	app.MainLoop()

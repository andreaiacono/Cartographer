import sys
from random import choice
from OpenGL.GL import *

import pygame
from pygame.locals import *


rot = 0
direction = 1
# these vertex arrays hold info for 2 squares, one flat shaded, the other textured
square1Colors = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 1, 1, 1]]
square1Vertices = [[-64, -64], [64, -64], [64, 64], [-64, 64]]
square2TexCoords = [[0, 0], [1, 0], [1, 1], [0, 1]]
square2Vertices = [[-128, -128], [128, -128], [128, 128], [-128, 128]]

#--- start of draw() loop ---
def draw():
    global rot, direction
    global square1Colors, square1Vertices, square2TexCoords, square2Vertices
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glTranslatef(200, 200, 0)

    #first square is flat shaded with different colors interpolated along the four corners 
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    glColorPointerf(square1Colors)
    glVertexPointerf(square1Vertices)
    glBegin(GL_QUADS)
    glArrayElement(0)
    glArrayElement(1)
    glArrayElement(2)
    glArrayElement(3)
    glEnd()
    glDisableClientState(GL_COLOR_ARRAY)

    #2nd square is a translucent texture
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glTexCoordPointerf(square2TexCoords)
    glVertexPointerf(square2Vertices)
    glRotatef(rot, 0, 0, 1)
    rot = (rot + direction) % 360
    glBegin(GL_QUADS)
    glArrayElement(0)
    glArrayElement(1)
    glArrayElement(2)
    glArrayElement(3)
    glEnd()
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)

    glFlush()
    glPopMatrix()
    pygame.display.flip()
    #---- end of draw() loop ----
    # this is actually indented all the way up to under def draw():


#---- start of main program body ----
# just 2 lines to initialize a 768x768 OpenGL window,
# the sound system, and everything else!
pygame.init()
pygame.display.set_mode((768, 768), OPENGL | DOUBLEBUF)

#create striped transparent texture 
tex = ""
for i in xrange(512):
    tex += "\xff\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\x7f"
    tex += "\xff\xff\xff\x3f\xff\xff\xff\x3f\xff\xff\xff\x3f\xff\xff\xff\x3f"
glTexImage2D(GL_TEXTURE_2D, 0, 4, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
glDisable(GL_DEPTH_TEST)

#reset projection matrix for orthographic
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, 512, 0, 512, -1, 1)

#draw first frame
draw()
move = 0

# put the choice of sounds to play in a list
soundList = []
soundList.append(pygame.mixer.Sound("sound1.wav"))
soundList.append(pygame.mixer.Sound("sound2.wav"))
soundList.append(pygame.mixer.Sound("sound3.wav"))

# the event loop
while 1:
    event = pygame.event.poll()
    if event.type is QUIT:
        sys.exit(0)
    if (move == 1):
        draw()
    if event.type is KEYDOWN:
        if event.key is K_ESCAPE:
            sys.exit(0)
        if event.key is K_SPACE:
            move = 0
        else:
            move = 1
    direction = direction * -1
    # choice(soundList).play()
    #---- end of main program body ----
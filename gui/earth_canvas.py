import math
import wx

from PIL.Image import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx import glcanvas
from wx.glcanvas import GLCanvas
import lib.shapefile


class EarthCanvas(GLCanvas):

    def __init__(self, parent, cartographer):
        GLCanvas.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, attribList=[
            wx.glcanvas.WX_GL_DOUBLEBUFFER,
            wx.glcanvas.WX_GL_DEPTH_SIZE, 24,
        ])
        self.context = glcanvas.GLContext(self)
        self.cartographer = cartographer
        self.init = False

        self.posx = -10
        self.posy = -90
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
        self.draw_rays = True
        self.resolution = 1.0  # Default: low resolution (ranges from 0 to 7.5)
        self.ray_alpha = 50  # 0-100, will be converted to 0.0-1.0
        self.cylinder_unwrap = 0
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

        # Shapes will be loaded by main.py setShape() to match the menu selection
        self.opengl_shapes = []

    def InitGL(self):
        # Initialize GLUT for text rendering
        try:
            glutInit()
        except:
            pass  # Already initialized

        # the earth texture
        image = open("textures/earth_mid.jpg")
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

        glEnable(GL_DEPTH_TEST)

    def OnSize(self, event):
        size = self.size = self.GetClientSize()
        if self.IsShownOnScreen() and size != (0, 0):
            self.SetCurrent(self.context)
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

        # Draw opaque earth sphere first with back-face culling
        # so depth buffer is established and inner surface is never visible
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glPushMatrix()
        glRotatef(self.earthy, 1.0, 0.0, 0.0)
        glRotatef(self.earthx, 0.0, 0.0, 1.0)
        glRotatef(self.earthz, 0.0, 1.0, 0.0)
        glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        gluSphere(self.earth_quad, self.earth_radius, 32, 32)
        glPopMatrix()
        glDisable(GL_CULL_FACE)

        # Draw transparent projection surfaces with depth read but no depth write
        # so they appear in front of the sphere where appropriate but don't
        # occlude each other
        glDepthMask(GL_FALSE)

        if self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Cylindrical or \
                        self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.PseudoCylindrical:
            # Check if it's an Equal Area projection - adjust cylinder height based on standard latitude
            from projections import equal_area
            if isinstance(self.cartographer.projection_panel.projection, equal_area.EqualAreaProjection):
                # Cylinder height depends on standard latitude
                # Increased from 3.0 to 4.0 for more clearance at top/bottom
                projection = self.cartographer.projection_panel.projection
                if hasattr(projection, 'cos_standard_latitude'):
                    cos_std_lat = projection.cos_standard_latitude
                    cyl_size = 4.0 / cos_std_lat  # Dynamic height based on standard latitude
                else:
                    cyl_size = 6.0  # Fallback
            else:
                cyl_size = 8  # Increased from 6 to 8 for more clearance for Mercator, Miller, etc.
            glPushMatrix()
            # Keep cylinder fixed (vertical) - Earth rotates inside it
            # This shows what happens when different great circles become tangent to the cylinder
            glTranslatef(0.0, 0.0, -self.earth_radius * cyl_size / 2)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.14)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            if self.cylinder_unwrap == 0:
                gluCylinder(self.plain_quad, self.earth_radius * 1.01, self.earth_radius * 1.01, self.earth_radius * cyl_size, 32, 64)
            else:
                self.draw_cylinder_surface(cyl_size)
            glPopMatrix()
            # Draw "Projection" text at bottom of cylinder
            if self.cylinder_unwrap == 0:
                self.draw_cylinder_label(cyl_size)
            if self.draw_rays:
                self.draw_shape_rays()
            glDisable(GL_BLEND)
        elif self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Conic:
            glPushMatrix()
            glTranslatef(0.0, 0.0, -self.earth_radius)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.5)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            gluCylinder(self.plain_quad, self.earth_radius * self.standard_parallel1 / 10, 0, self.earth_radius * 3, 32, 64)
            glPopMatrix()
            if self.draw_rays:
                self.draw_shape_rays()
            glDisable(GL_BLEND)
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
            if self.draw_rays:
                self.draw_shape_rays()
            glDisable(GL_BLEND)

        glDepthMask(GL_TRUE)

        self.SwapBuffers()

    def _unwrap_point(self, x, y, z):
        """Transform a point on the circular cylinder to its unwrapped position.

        As unwrap increases from 0 to 100:
        - The cylinder stays wrapped around the earth
        - The front (touching earth at +y) stays fixed at (0, r)
        - A cut opens at the back
        - The surface unfolds as an arc that flattens
        - Finally becomes a flat horizontal line at y = r
        - The front point remains in contact with the earth throughout
        """
        if self.cylinder_unwrap == 0:
            return (x, y, z)

        f = self.cylinder_unwrap / 100.0
        # Use the actual input point's radius for start position
        input_r = math.sqrt(x * x + y * y)
        # Use earth_radius for the final unfolded width (circumference)
        arc_r = self.earth_radius

        # phi = angle from back (-y), with cut at phi = ±pi (front, +y)
        # atan2(-x, -y) rotates by 180 degrees so cut opens from behind the earth
        # This naturally has the discontinuity at +y (the cut location)
        phi = math.atan2(-x, -y)

        # Arc length based on earth's actual circumference
        arc_length = -arc_r * phi  # ranges from -pi*arc_r to pi*arc_r

        # Start position: matches the input point
        start_x = x
        start_y = y

        # End position: horizontal line at y = -arc_r (behind the earth)
        end_x = arc_length
        end_y = -arc_r

        # Easing function: smoothstep for smooth animation
        smooth_f = f * f * (3 - 2 * f)

        # Use the same interpolation factor for both x and y
        # so the surface expands and flattens at the same rate
        new_x = (1 - smooth_f) * start_x + smooth_f * end_x
        new_y = (1 - smooth_f) * start_y + smooth_f * end_y

        # Ensure point stays outside the earth sphere during animation
        # Linear interpolation can cause points to "cut through" the sphere
        min_radius = self.earth_radius * 1.01
        dist = math.sqrt(new_x * new_x + new_y * new_y)
        if dist < min_radius:
            # Push point outward radially to maintain minimum distance
            scale = min_radius / dist
            new_x *= scale
            new_y *= scale

        return (new_x, new_y, z)

    def draw_cylinder_surface(self, cyl_size):
        """Draw the cylinder surface manually with unwrap interpolation.

        The cylinder is drawn with the cut at the front (positive y, theta = pi/2).
        We draw two separate halves that don't connect at the cut.
        """
        r = self.earth_radius * 1.01
        n_slices = 64  # More slices for smoother curve
        n_stacks = 64
        height = self.earth_radius * cyl_size

        # Gap at the cut edges - increases as the cylinder unwraps
        unwrap_factor = self.cylinder_unwrap / 100.0
        eps = 0.001 + unwrap_factor * 0.5

        for j in range(n_stacks):
            z0 = (j / float(n_stacks)) * height
            z1 = ((j + 1) / float(n_stacks)) * height
            t0 = j / float(n_stacks)
            t1 = (j + 1) / float(n_stacks)

            # Draw right half: from back (-pi/2) to just before cut (pi/2 - eps)
            glBegin(GL_QUAD_STRIP)
            half_slices = n_slices // 2
            for i in range(half_slices + 1):
                frac = i / float(half_slices)
                theta = (-math.pi / 2) + frac * (math.pi - eps)  # -pi/2 to pi/2 - eps
                cx = r * math.cos(theta)
                cy = r * math.sin(theta)
                s = frac * 0.5  # texture from 0.0 to 0.5
                x0, y0, zz0 = self._unwrap_point(cx, cy, z0)
                x1, y1, zz1 = self._unwrap_point(cx, cy, z1)
                glTexCoord2f(s, t0)
                glVertex3f(x0, y0, zz0)
                glTexCoord2f(s, t1)
                glVertex3f(x1, y1, zz1)
            glEnd()

            # Draw left half: from just after cut (pi/2 + eps) to back (3*pi/2)
            glBegin(GL_QUAD_STRIP)
            for i in range(half_slices + 1):
                frac = i / float(half_slices)
                theta = (math.pi / 2 + eps) + frac * (math.pi - eps)  # pi/2 + eps to 3*pi/2
                cx = r * math.cos(theta)
                cy = r * math.sin(theta)
                s = 0.5 + frac * 0.5  # texture from 0.5 to 1.0
                x0, y0, zz0 = self._unwrap_point(cx, cy, z0)
                x1, y1, zz1 = self._unwrap_point(cx, cy, z1)
                glTexCoord2f(s, t0)
                glVertex3f(x0, y0, zz0)
                glTexCoord2f(s, t1)
                glVertex3f(x1, y1, zz1)
            glEnd()

    def draw_cylinder_label(self, cyl_size):
        """Draw short vertical lines at top and bottom of cylinder to show it's stationary."""
        r = self.earth_radius * 1.01
        height = self.earth_radius * cyl_size

        glPushMatrix()
        glTranslatef(0.0, 0.0, -height / 2)

        # Disable textures
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)

        # Draw 8 short vertical lines evenly spaced around the cylinder
        glColor4f(0.7, 0.7, 0.7, 0.4)  # Gray with less opacity
        glLineWidth(2.0)

        line_length = 0.3  # Length of the short lines
        n_lines = 8  # Number of lines around the cylinder

        for i in range(n_lines):
            angle = 2 * math.pi * i / n_lines  # Every 45 degrees
            x = r * math.cos(angle)
            y = r * math.sin(angle)

            # Line at bottom
            glBegin(GL_LINES)
            glVertex3f(x, y, 0)
            glVertex3f(x, y, line_length)
            glEnd()

            # Line at top
            glBegin(GL_LINES)
            glVertex3f(x, y, height - line_length)
            glVertex3f(x, y, height)
            glEnd()

        glLineWidth(1.0)

        # Draw longitude labels (0, 90, 180, 270) as if printed on cylinder surface
        # Using the coordinate system: x = r*sin(lon), y = -r*cos(lon)
        glColor4f(0.3, 0.3, 0.3, 0.9)  # Dark gray for better contrast
        glLineWidth(2.0)

        # Longitude positions: rotate by 270° from standard to put 0° at front
        longitudes = [
            (0, 0, -r),      # 0° at front (negative y) - Prime Meridian
            (90, r, 0),      # 90°E at right (positive x)
            (180, 0, r),     # 180° at back (positive y) - Date Line
            (270, -r, 0)     # 270° (or -90°W) at left (negative x)
        ]

        text_scale = 0.004  # Scale for stroke text (increased for larger font size)
        text_z_offset_bottom = 0.6  # Distance from bottom base
        text_z_offset_top = 0.9     # Distance from top base (larger to avoid bars)

        for lon_deg, x, y in longitudes:
            label = str(lon_deg)

            # Calculate angle for this position (to orient text tangent to cylinder)
            angle = math.atan2(y, x)

            # Position directly on cylinder surface (no offset)
            text_x = x
            text_y = y

            # Draw at bottom
            glPushMatrix()
            glTranslatef(text_x, text_y, text_z_offset_bottom)
            glRotatef(math.degrees(angle) + 90, 0, 0, 1)  # Rotate around cylinder
            glRotatef(90, 1, 0, 0)  # Tilt to lie flat on cylinder surface
            glScalef(text_scale, text_scale, text_scale)
            # Center the text
            text_width = len(label) * 104.76  # Approximate width for GLUT_STROKE_ROMAN
            glTranslatef(-text_width / 2, 0, 0)
            for c in label:
                glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))
            glPopMatrix()

            # Draw at top (further from base to avoid vertical bars)
            glPushMatrix()
            glTranslatef(text_x, text_y, height - text_z_offset_top)
            glRotatef(math.degrees(angle) + 90, 0, 0, 1)  # Rotate around cylinder
            glRotatef(90, 1, 0, 0)  # Tilt to lie flat on cylinder surface
            glScalef(text_scale, text_scale, text_scale)
            # Center the text
            glTranslatef(-text_width / 2, 0, 0)
            for c in label:
                glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(c))
            glPopMatrix()

        glLineWidth(1.0)

        glPopMatrix()

        # Re-enable textures
        glEnable(GL_TEXTURE_2D)

    def _intersect_ray(self, dx, dy, dz, proj_type, ProjectionType):
        """Compute intersection of a ray from origin with the projection surface.
        Returns (ix, iy, iz) or None."""
        r = self.earth_radius

        if proj_type == ProjectionType.Cylindrical or proj_type == ProjectionType.PseudoCylindrical:
            cyl_r = r * 1.01  # Same as draw_cylinder_surface
            dxy2 = dx * dx + dy * dy
            if dxy2 < 1e-9:
                return None
            t = cyl_r / math.sqrt(dxy2)
            ix, iy, iz = dx * t, dy * t, dz * t
            if abs(iz) > r * 3:
                return None
            return self._unwrap_point(ix, iy, iz)

        elif proj_type == ProjectionType.Conic:
            base_r = r * self.standard_parallel1 / 10.0
            h = r * 3.0
            apex_z = -r + h
            k = base_r / h
            a_coeff = dx * dx + dy * dy - k * k * dz * dz
            b_coeff = 2.0 * k * k * apex_z * dz
            c_coeff = -(k * k * apex_z * apex_z)
            disc = b_coeff * b_coeff - 4.0 * a_coeff * c_coeff
            if disc < 0:
                return None
            sqrt_disc = math.sqrt(disc)
            if abs(a_coeff) < 1e-12:
                return None
            t1 = (-b_coeff + sqrt_disc) / (2.0 * a_coeff)
            t2 = (-b_coeff - sqrt_disc) / (2.0 * a_coeff)
            t = None
            for tc in sorted([t1, t2]):
                if tc > 0:
                    iz = dz * tc
                    if -r <= iz <= apex_z:
                        t = tc
                        break
            if t is None:
                return None
            return (dx * t, dy * t, dz * t)

        elif proj_type == ProjectionType.Azimuthal:
            if abs(dz) < 1e-9:
                return None
            t = -r / dz
            if t < 0:
                return None
            ix, iy, iz = dx * t, dy * t, dz * t
            if ix * ix + iy * iy > (r * 3) ** 2:
                return None
            return (ix, iy, iz)

        return None

    def _interpolate_on_surface(self, p1, p2, proj_type, ProjectionType, steps=8):
        """Interpolate between two surface points along the projection surface.
        Returns list of 3D points on the surface."""
        r = self.earth_radius

        if proj_type == ProjectionType.Cylindrical or proj_type == ProjectionType.PseudoCylindrical:
            cyl_r = r * 1.01  # Same as draw_cylinder_surface
            # When unwrapped, work backwards from unwrapped coords to get phi
            # phi is the angle from back (phi=0 at back/-y, phi=±pi at front/+y)
            if self.cylinder_unwrap > 0:
                # p1 and p2 are already unwrapped (from _intersect_ray)
                # Recover phi using Newton's method
                f = self.cylinder_unwrap / 100.0
                # Must use the same smoothstep easing as _unwrap_point
                smooth_f = f * f * (3 - 2 * f)
                ur = r * 1.01

                def recover_phi(px, py):
                    # new_x = -ur * ((1-smooth_f)*sin(phi) + smooth_f*phi)
                    # So: (1-smooth_f)*sin(phi) + smooth_f*phi = -px / ur
                    # Solve for phi given px
                    # Use atan2 as initial guess (exact at f=0, good approximation for small f)
                    phi_guess = math.atan2(-px, -py)
                    target = -px / ur
                    for _ in range(15):
                        val = (1 - smooth_f) * math.sin(phi_guess) + smooth_f * phi_guess
                        dval = (1 - smooth_f) * math.cos(phi_guess) + smooth_f
                        if abs(dval) < 1e-12:
                            break
                        phi_guess -= (val - target) / dval
                        phi_guess = max(-math.pi, min(math.pi, phi_guess))
                    return phi_guess

                phi1 = recover_phi(p1[0], p1[1])
                phi2 = recover_phi(p2[0], p2[1])
            else:
                # phi = angle from back (-y), with cut at ±pi (front, +y)
                phi1 = math.atan2(-p1[0], -p1[1])
                phi2 = math.atan2(-p2[0], -p2[1])

            z1 = p1[2]
            z2 = p2[2]

            # Skip if points are on opposite sides of the cut (phi near ±pi)
            # The cut is at phi = ±pi, so if one point has phi > threshold
            # and the other has phi < -threshold, they're across the cut
            cut_threshold = math.pi * 0.7
            if (phi1 > cut_threshold and phi2 < -cut_threshold) or \
               (phi2 > cut_threshold and phi1 < -cut_threshold):
                return []

            # Choose shortest angular path
            dphi = phi2 - phi1
            if dphi > math.pi:
                dphi -= 2 * math.pi
            elif dphi < -math.pi:
                dphi += 2 * math.pi
            # Skip if wrapping around the front (cut at phi = ±pi)
            if abs(dphi) > math.pi * 0.8:
                return []
            pts = []
            for s in range(steps + 1):
                frac = s / float(steps)
                phi = phi1 + dphi * frac
                z = z1 + (z2 - z1) * frac
                # Convert phi to cylinder coordinates
                # phi = atan2(-x, -y), so x = -r*sin(phi), y = -r*cos(phi)
                cx = -cyl_r * math.sin(phi)
                cy = -cyl_r * math.cos(phi)
                pts.append(self._unwrap_point(cx, cy, z))
            return pts

        elif proj_type == ProjectionType.Conic:
            base_r = r * self.standard_parallel1 / 10.0
            h = r * 3.0
            apex_z = -r + h
            k = base_r / h
            # Convert to conical coordinates: angle around axis and height z
            theta1 = math.atan2(p1[1], p1[0])
            z1 = p1[2]
            theta2 = math.atan2(p2[1], p2[0])
            z2 = p2[2]
            dtheta = theta2 - theta1
            if dtheta > math.pi:
                dtheta -= 2 * math.pi
            elif dtheta < -math.pi:
                dtheta += 2 * math.pi
            if abs(dtheta) > math.pi * 0.8:
                return []
            pts = []
            for s in range(steps + 1):
                frac = s / float(steps)
                theta = theta1 + dtheta * frac
                z = z1 + (z2 - z1) * frac
                cone_r = k * (apex_z - z)
                pts.append((cone_r * math.cos(theta), cone_r * math.sin(theta), z))
            return pts

        elif proj_type == ProjectionType.Azimuthal:
            # Flat plane, straight lines are fine
            return [p1, p2]

        return []

    def _get_mercator_cylinder_point(self, lon_deg, lat_deg):
        """Calculate where a point at given lat/lon should appear on the cylinder using Mercator formula.

        Returns (x, y, z) on the cylinder surface where:
        - x, y define the position around the cylinder (from longitude)
        - z is the height using Mercator formula: r * asinh(tan(lat))
        """
        r = self.earth_radius
        cyl_r = r * 1.01  # Same radius as cylinder

        lon = math.radians(lon_deg)
        lat = math.radians(lat_deg)

        # Position around cylinder (from longitude)
        # Match the coordinate system: negative sin for x, negative cos for y
        x = cyl_r * math.sin(lon)
        y = -cyl_r * math.cos(lon)

        # Height using Mercator formula: z = r * asinh(tan(lat))
        # This naturally scales to fill the cylinder which extends from -r*3 to +r*3
        # asinh(tan(lat)) ranges from about -3 to +3 for latitudes up to ±85°
        if abs(lat) < math.pi/2 - 0.01:  # Avoid poles
            z = r * math.asinh(math.tan(lat))
        else:
            # At poles, use a large value with appropriate sign
            z = math.copysign(r * 2.5, lat)

        return (x, y, z)

    def _get_equal_area_cylinder_point(self, lon_deg, lat_deg):
        """Calculate where a point at given lat/lon should appear on the cylinder using Equal Area formula.

        Returns (x, y, z) on the cylinder surface where:
        - x, y define the position around the cylinder (from longitude)
        - z is the height using Equal Area formula: r * sin(lat) / cos(standard_latitude)
        """
        r = self.earth_radius
        cyl_r = r * 1.01  # Same radius as cylinder

        lon = math.radians(lon_deg)
        lat = math.radians(lat_deg)

        # Position around cylinder (from longitude)
        # Match the coordinate system: negative sin for x, negative cos for y
        x = cyl_r * math.sin(lon)
        y = -cyl_r * math.cos(lon)

        # Get the standard latitude from the Equal Area projection
        projection = self.cartographer.projection_panel.projection
        if hasattr(projection, 'cos_standard_latitude'):
            cos_std_lat = projection.cos_standard_latitude
        else:
            cos_std_lat = 1.0  # Fallback if not available

        # Height using Equal Area formula: z = r * sin(lat) / cos(standard_latitude)
        # Scale to match the 2D projection's vertical extent
        # The 2D uses 90 * sin(lat) / cos(std_lat), so we scale proportionally
        z = r * 1.5 * math.sin(lat) / cos_std_lat

        return (x, y, z)

    def _generate_mercator_ray(self, sphere_pt, mercator_pt, lat_deg, steps=20):
        """Generate a ray from Earth's center through surface, curving to Mercator point.

        The ray shows:
        - Center to surface: straight radial line (hidden inside Earth)
        - Surface to cylinder: smooth curve to Mercator-corrected position

        The curvature amount visualizes Mercator distortion:
        - Equator: nearly straight (minimal distortion)
        - Higher latitudes: more curve (more distortion)
        """
        sx, sy, sz = sphere_pt
        mx, my, mz = mercator_pt

        points = [(0, 0, 0)]  # Start from Earth's center

        for i in range(1, steps + 1):
            t = i / float(steps)

            if t <= 0.5:
                # From center to sphere surface: straight radial line (INSIDE Earth)
                # This portion is hidden by depth buffer
                scale = t * 2.0
                x, y, z = scale * sx, scale * sy, scale * sz
            else:
                # From surface to Mercator point: smooth curve (VISIBLE)
                t_curve = (t - 0.5) * 2.0  # 0 to 1 for curve segment

                # Smooth easing using smoothstep
                smooth = t_curve * t_curve * (3 - 2 * t_curve)

                x = sx + smooth * (mx - sx)
                y = sy + smooth * (my - sy)
                z = sz + smooth * (mz - sz)

            points.append((x, y, z))

        return points

    def _generate_equal_area_ray(self, sphere_pt, equal_area_pt, lat_deg, steps=20):
        """Generate a ray from Earth's center through surface, curving to Equal Area point.

        The ray shows:
        - Center to surface: straight radial line (hidden inside Earth)
        - Surface to cylinder: smooth curve to Equal Area-corrected position

        Equal Area has less vertical distortion than Mercator:
        - Height adjustment is proportional to sin(lat) rather than asinh(tan(lat))
        - Less extreme curvature at high latitudes
        """
        sx, sy, sz = sphere_pt
        ex, ey, ez = equal_area_pt

        points = [(0, 0, 0)]  # Start from Earth's center

        for i in range(1, steps + 1):
            t = i / float(steps)

            if t <= 0.5:
                # From center to sphere surface: straight radial line (INSIDE Earth)
                # This portion is hidden by depth buffer
                scale = t * 2.0
                x, y, z = scale * sx, scale * sy, scale * sz
            else:
                # From surface to Equal Area point: smooth curve (VISIBLE)
                t_curve = (t - 0.5) * 2.0  # 0 to 1 for curve segment

                # Smooth easing using smoothstep
                smooth = t_curve * t_curve * (3 - 2 * t_curve)

                x = sx + smooth * (ex - sx)
                y = sy + smooth * (ey - sy)
                z = sz + smooth * (ez - sz)

            points.append((x, y, z))

        return points

    def draw_shape_rays(self):
        r = self.earth_radius
        projection = self.cartographer.projection_panel.projection
        proj_type = projection.projection_type
        ProjectionType = projection.ProjectionType

        # Use shapes selected from Resolution menu (synced with 2D panel)
        shapes = self.opengl_shapes

        # Build rotation matrix matching glRotatef order: Rx(earthy) Rz(earthx) Ry(earthz)
        ax = math.radians(self.earthy)
        az = math.radians(self.earthx)
        ay = math.radians(self.earthz)
        cx, sx = math.cos(ax), math.sin(ax)
        cz, sz = math.cos(az), math.sin(az)
        cy, sy = math.cos(ay), math.sin(ay)

        # Rx * Rz * Ry combined rotation matrix
        def rotate(x, y, z):
            # Ry first
            x1 = cy * x + sy * z
            y1 = y
            z1 = -sy * x + cy * z
            # Rz
            x2 = cz * x1 - sz * y1
            y2 = sz * x1 + cz * y1
            z2 = z1
            # Rx
            x3 = x2
            y3 = cx * y2 - sx * z2
            z3 = sx * y2 + cx * z2
            return x3, y3, z3

        def sphere_point(lon_deg, lat_deg):
            lon = math.radians(lon_deg)
            lat = math.radians(lat_deg)
            px = r * math.cos(lat) * math.sin(lon)
            py = -r * math.cos(lat) * math.cos(lon)
            pz = r * math.sin(lat)
            return rotate(px, py, pz)

        def ray_intersect(px, py, pz):
            length = math.sqrt(px * px + py * py + pz * pz)
            if length < 1e-9:
                return None
            dx, dy, dz = px / length, py / length, pz / length
            return self._intersect_ray(dx, dy, dz, proj_type, ProjectionType)

        # Check if this is a Mercator-type cylindrical projection
        is_mercator = (proj_type == ProjectionType.Cylindrical and
                      hasattr(projection, '__class__') and
                      'Mercator' in projection.__class__.__name__)

        # Check if this is an Equal Area cylindrical projection
        is_equal_area = (proj_type == ProjectionType.Cylindrical and
                        hasattr(projection, '__class__') and
                        'EqualArea' in projection.__class__.__name__)

        # Collect sampled points (flat list for rays/dots) and
        # part-aware intersection lists (for outlines)
        all_intersections = []
        all_sphere_points = []
        all_latlon = []  # Store original lat/lon for Mercator calculation
        part_intersections = []  # list of lists, one per contiguous part

        count = 0
        for shape in shapes:
            points = shape.points
            # Determine part boundaries
            parts = list(shape.parts) if hasattr(shape, 'parts') and shape.parts else [0]
            for pi in range(len(parts)):
                start = parts[pi]
                end = parts[pi + 1] if pi + 1 < len(parts) else len(points)
                part_hits = []
                for i in range(start, end):
                    count += 1

                    # Sample points based on resolution
                    # resolution=0: draws nothing
                    # resolution=1.0 to 7.5: draws 2% to 15% of points
                    # Linear relationship: resolution/50 = fraction of points drawn
                    count_in_window = count % 50
                    if not ((count_in_window * self.resolution) % 50 < self.resolution):
                        continue

                    p = points[i]
                    lon_deg, lat_deg = p[0], p[1]
                    px, py, pz = sphere_point(lon_deg, lat_deg)

                    # Calculate cylinder intersection point
                    if is_mercator or is_equal_area:
                        # Calculate effective lat/lon with respect to the FIXED vertical cylinder
                        # After Earth rotation, we need the coordinates in world space
                        sphere_radius = math.sqrt(px*px + py*py + pz*pz)
                        if sphere_radius > 1e-9:
                            # Effective latitude: angle from xy-plane (cylinder equator)
                            lat_eff = math.asin(pz / sphere_radius)
                            # Effective longitude: angle around z-axis
                            # Must match coordinate system: x = r*sin(lon), y = -r*cos(lon)
                            lon_eff = math.atan2(px, -py)

                            # Convert to degrees for projection calculation
                            lat_eff_deg = math.degrees(lat_eff)
                            lon_eff_deg = math.degrees(lon_eff)

                            # Use effective lat/lon for the appropriate projection
                            if is_mercator:
                                mx, my, mz = self._get_mercator_cylinder_point(lon_eff_deg, lat_eff_deg)
                            else:  # is_equal_area
                                mx, my, mz = self._get_equal_area_cylinder_point(lon_eff_deg, lat_eff_deg)
                            # Apply cylinder unwrap transformation
                            hit = self._unwrap_point(mx, my, mz)

                            if hit is not None:
                                all_intersections.append(hit)
                                all_sphere_points.append((px, py, pz))
                                # Store effective lat/lon for ray curvature calculation
                                all_latlon.append((lon_eff_deg, lat_eff_deg))
                                part_hits.append(hit)
                        else:
                            hit = None
                    else:
                        # Use geometric projection for other types
                        hit = ray_intersect(px, py, pz)

                        if hit is not None:
                            all_intersections.append(hit)
                            all_sphere_points.append((px, py, pz))
                            all_latlon.append((lon_deg, lat_deg))
                            part_hits.append(hit)
                if len(part_hits) >= 2:
                    part_intersections.append(part_hits)

        if not all_intersections:
            return

        # Disable texture for drawing lines (rays and outlines)
        glDisable(GL_TEXTURE_2D)

        # Only draw rays and dots when cylinder is fully closed (not unfolding)
        # During unfolding, the 3D projection concept doesn't apply
        if self.cylinder_unwrap == 0:
            # Draw rays showing how projection works
            # Depth testing is enabled, so Earth will hide the interior portions
            glLineWidth(1.0)
            ray_alpha = self.ray_alpha / 100.0  # Convert 0-100 slider to 0.0-1.0
            glColor4f(0.0, 0.0, 0.7, ray_alpha)

            for i, (ix, iy, iz) in enumerate(all_intersections):
                sphere_pt = all_sphere_points[i]

                if is_mercator:
                    # Draw ray from center through surface to Mercator cylinder point
                    # Curvature depends on latitude (straight at equator, curved at poles)
                    lon_deg, lat_deg = all_latlon[i]
                    ray_points = self._generate_mercator_ray(sphere_pt, (ix, iy, iz), lat_deg, steps=20)
                    glBegin(GL_LINE_STRIP)
                    for px, py, pz in ray_points:
                        glVertex3f(px, py, pz)
                    glEnd()
                elif is_equal_area:
                    # Draw ray from center through surface to Equal Area cylinder point
                    # Less curvature than Mercator (sin vs asinh(tan))
                    lon_deg, lat_deg = all_latlon[i]
                    ray_points = self._generate_equal_area_ray(sphere_pt, (ix, iy, iz), lat_deg, steps=20)
                    glBegin(GL_LINE_STRIP)
                    for px, py, pz in ray_points:
                        glVertex3f(px, py, pz)
                    glEnd()
                else:
                    # Draw straight ray from center for other projections (geometric projection)
                    glBegin(GL_LINES)
                    glVertex3f(0, 0, 0)
                    glVertex3f(ix, iy, iz)
                    glEnd()

        # Draw continent outlines on projection surface
        # Vary alpha based on facing toward light/camera
        # Account for both view rotation (posx/y/z) to simulate fixed light source
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)

        # Precompute view rotation matrix (posy=X, posx=Z, posz=Y)
        import math as m
        _cos, _sin, _rad = m.cos, m.sin, m.radians

        cy, sy = _cos(_rad(self.posy)), _sin(_rad(self.posy))  # X rotation
        cx, sx = _cos(_rad(self.posx)), _sin(_rad(self.posx))  # Z rotation
        cz, sz = _cos(_rad(self.posz)), _sin(_rad(self.posz))  # Y rotation

        # Apply view rotations in order: Y (posy), Z (posx), Y (posz)
        def rotate_to_view(x, y, z):
            # Apply posy (X rotation)
            x1 = x
            y1 = cy * y - sy * z
            z1 = sy * y + cy * z
            # Apply posx (Z rotation)
            x2 = cx * x1 - sx * y1
            y2 = sx * x1 + cx * y1
            z2 = z1
            # Apply posz (Y rotation)
            x3 = cz * x2 + sz * z2
            y3 = y2
            z3 = -sz * x2 + cz * z2
            return x3, y3, z3

        cyl_radius = r * 1.01

        for part_hits in part_intersections:
            for j in range(len(part_hits) - 1):
                # Check if we're unfolding and if points are on opposite sides of the gap
                if self.cylinder_unwrap > 0:
                    p1 = part_hits[j]
                    p2 = part_hits[j + 1]
                    # Calculate angles around cylinder for both points
                    theta1 = m.atan2(p1[1], p1[0])
                    theta2 = m.atan2(p2[1], p2[0])
                    # Calculate angular distance (accounting for wraparound)
                    angle_diff = abs(theta2 - theta1)
                    if angle_diff > m.pi:
                        angle_diff = 2 * m.pi - angle_diff
                    # If points are far apart angularly (> 90°), they're on opposite sides of gap
                    # Skip drawing this segment to avoid lines crossing the gap
                    if angle_diff > m.pi / 2:
                        continue

                seg = self._interpolate_on_surface(
                    part_hits[j], part_hits[j + 1], proj_type, ProjectionType)
                if len(seg) >= 2:
                    glBegin(GL_LINE_STRIP)
                    for sx, sy, sz in seg:
                        # Calculate surface normal for cylinder (radial direction)
                        # Normal is perpendicular to Z axis, pointing outward
                        norm_len = m.sqrt(sx*sx + sy*sy)
                        if norm_len > 0.01:
                            nx, ny = sx / norm_len, sy / norm_len
                        else:
                            nx, ny = 0, 0

                        # Transform normal to view space
                        nvx, nvy, nvz = rotate_to_view(nx, ny, 0)

                        # Camera looks along -Z in view space
                        # Dot product with camera direction (0, 0, -1) is just -nvz
                        # But for cylinder normal (radial), we care about Y component
                        # Use constant alpha - no brightness variation
                        alpha = 0.8
                        glColor4f(0.0, 1.0, 1.0, alpha)
                        glVertex3f(sx, sy, sz)
                    glEnd()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_TEXTURE_2D)


    def set_earth_coordinates(self, x, y, z):
        self.earthx = -x  # left/right -> Z axis rotation (spin in place)
        self.earthy = z   # pageup/pagedown -> X axis rotation (tilt)
        self.earthz = y   # up/down -> Y axis rotation (spin globe)

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

            # Scale rotation speed based on zoom level
            # When zoomed in (view_distance closer to 0), rotate slower
            # When zoomed out (view_distance more negative), rotate faster
            base_distance = -30.0
            rotation_scale = self.view_distance / base_distance

            if evt.RightIsDown():
                self.z = self.y
                self.posz += (self.z - self.lastz) * rotation_scale
                self.lastz = self.z
            else:
                self.posx += (self.x - self.lastx) * rotation_scale
                self.posy += (self.y - self.lasty) * rotation_scale
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

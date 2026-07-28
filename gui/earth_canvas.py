import math
import os
import wx

from PIL.Image import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx import glcanvas
from wx.glcanvas import GLCanvas
import lib.shapefile

# Get project root directory for absolute paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import projection classes to identify specific types
from projections import gnomonic, stereographic, orthographic, equidistant
from projections import sinusoidal, mollweide, eckertIV, collignon
from projections import lambert, albers


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
        # degrees; same defaults as the conic sliders and the conic projections
        self.standard_parallel1 = 30
        self.standard_parallel2 = 60
        self.draw_rays = True
        self.earth_alpha = 70  # 0-100; below 100 the rays inside the earth show through
        # 0.0-1.0, how much the furthest lines recede. Applied twice, once to
        # colour via fog and once to alpha, so the strength that actually
        # reaches the screen at the back is (1 - depth_cue) squared.
        self.depth_cue = 0.85
        self.resolution = 1.0  # Default: low resolution (ranges from 0 to 7.5)
        self.ray_alpha = 50  # 0-100, will be converted to 0.0-1.0
        self.surface_unroll = 0
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
        image = open(os.path.join(PROJECT_ROOT, "textures/earth_mid.jpg"))
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
        image2 = open(os.path.join(PROJECT_ROOT, "textures/plain_texture.png"))
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

    def get_azimuthal_ray_type(self):
        """Determine the ray origin type for the current azimuthal projection.
        Returns: 'gnomonic', 'stereographic', 'orthographic', 'equidistant', or 'generic'
        """
        projection = self.cartographer.projection_panel.projection
        if isinstance(projection, gnomonic.GnomonicProjection):
            return 'gnomonic'
        elif isinstance(projection, stereographic.StereographicProjection):
            return 'stereographic'
        elif isinstance(projection, orthographic.AzimuthalOrthographicProjection):
            return 'orthographic'
        elif isinstance(projection, equidistant.AzimuthalEquidistantProjection):
            return 'equidistant'
        else:
            return 'generic'

    def get_pseudocylindrical_type(self):
        """Determine which pseudo-cylindrical projection is active.
        Returns: 'sinusoidal', 'mollweide', 'eckert4', 'collignon', or 'generic'
        """
        projection = self.cartographer.projection_panel.projection
        if isinstance(projection, sinusoidal.SinusoidalProjection):
            return 'sinusoidal'
        elif isinstance(projection, mollweide.MollweideProjection):
            return 'mollweide'
        elif isinstance(projection, eckertIV.EckertIVProjection):
            return 'eckert4'
        elif isinstance(projection, collignon.CollignonProjection):
            return 'collignon'
        else:
            return 'generic'

    def get_conic_type(self):
        """Determine which conic projection is active.
        Returns: 'lambert', 'albers', or 'generic'
        """
        projection = self.cartographer.projection_panel.projection
        if isinstance(projection, lambert.LambertProjection):
            return 'lambert'
        elif isinstance(projection, albers.AlbersProjection):
            return 'albers'
        else:
            return 'generic'

    def _conic_cone_geometry(self):
        """Geometry of the cone drawn for conic projections.

        The cone is tangent to the sphere along the first standard parallel:
        its apex sits at r / sin(phi) on the axis and it widens going down,
        touching the sphere exactly on that parallel. Very high parallels give
        an almost flat cone, so the cone is cut off before it grows wide
        enough to swallow the whole view.

        Returns (base_r, h, apex_z) in world coordinates.
        """
        r = self.earth_radius
        phi = math.radians(max(5.0, min(85.0, self.standard_parallel1)))
        apex_z = r / math.sin(phi)
        # radius the cone surface gains per unit of descent below the apex
        slope = (r * math.cos(phi)) / (apex_z - r * math.sin(phi))
        h = min(apex_z + r, (r * 2.5) / slope)
        return slope * h, h, apex_z

    def _earth_rotate(self, x, y, z):
        """Apply the earth's own rotation (earthx/y/z) to a point.

        Matches the glRotatef order used to draw the sphere: Rx(earthy)
        Rz(earthx) Ry(earthz). Shared by the ray/coastline sampling and the
        pseudo-cylindrical graticule so they turn together.
        """
        ax = math.radians(self.earthy)
        az = math.radians(self.earthx)
        ay = math.radians(self.earthz)
        cx, sx = math.cos(ax), math.sin(ax)
        cz, sz = math.cos(az), math.sin(az)
        cy, sy = math.cos(ay), math.sin(ay)
        # Ry
        x1 = cy * x + sy * z
        y1 = y
        z1 = -sy * x + cy * z
        # Rz
        x2 = cz * x1 - sz * y1
        y2 = sz * x1 + cz * y1
        z2 = z1
        # Rx
        return x2, cx * y2 - sx * z2, sx * y2 + cx * z2

    def _pseudocyl_surface_point_geo(self, lon_deg, lat_deg):
        """Flat-map point for a geographic lon/lat, after the earth's rotation.

        Turns the geographic coordinate into the effective (world-space)
        lon/lat the projection is actually evaluated at, exactly as the
        coastline sampling and the 2D panel do, so the graticule drawn with
        this deforms into the oblique aspect in step with the continents.
        """
        lon = math.radians(lon_deg)
        lat = math.radians(lat_deg)
        x, y, z = self._earth_rotate(math.cos(lat) * math.sin(lon),
                                     -math.cos(lat) * math.cos(lon),
                                     math.sin(lat))
        lon_eff = math.degrees(math.atan2(x, -y))
        lat_eff = math.degrees(math.asin(max(-1.0, min(1.0, z))))
        return self._compute_pseudocylindrical_surface_point(lon_eff, lat_eff)

    def _compute_pseudocylindrical_surface_point(self, lon_deg, lat_deg):
        """Compute the 3D position on the projection surface for pseudo-cylindrical projections.

        For pseudo-cylindrical projections, we show the projection as a shaped surface
        positioned in front of the Earth. The surface shape (ellipse, pointed poles, etc.)
        is determined by the projection formula.

        Args:
            lon_deg, lat_deg: Geographic coordinates in degrees

        Returns:
            (x, y, z) on the projection surface, or None if outside bounds
        """
        r = self.earth_radius
        projection = self.cartographer.projection_panel.projection

        # Get 2D projection coordinates
        lon_rad = math.radians(lon_deg)
        lat_rad = math.radians(lat_deg)

        try:
            x_2d, y_2d = projection.get_coords(lon_rad, lat_rad)
        except:
            return None

        # Scale the 2D coordinates to fit nicely around the sphere
        # The projection formulas return coordinates in their own scale
        scale_factor = r / 120.0  # Adjust to make it visible and proportional to Earth

        x_proj = x_2d * scale_factor
        y_proj = y_2d * scale_factor

        # Position the projection surface as a "billboard" in front of the Earth
        # We'll place it at a fixed distance in front (along the -y axis in our coordinate system)
        # This shows the projection shape clearly

        # The surface is positioned at y = -(r + offset)
        # This places it in front of the Earth (since camera typically views from -y direction)
        # Pushed well clear of the sphere so it reads as a separate flat map the
        # globe projects onto, rather than a net wrapped around it.
        offset = r * 1.6
        z_depth = -(r + offset)

        # Map the 2D projection coordinates to this surface
        # x_proj → x (horizontal on projection surface)
        # y_proj → z (vertical on projection surface)
        # Fixed depth → y (distance from Earth)

        x = x_proj
        z = y_proj
        y = z_depth

        # Check bounds - don't draw if too far outside reasonable area
        if abs(x) > r * 4 or abs(z) > r * 4:
            return None

        return (x, y, z)

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

        # The earth is drawn last (see draw_earth), as translucent glass over
        # the rays, so the rays reaching the centre stay visible through it.
        glEnable(GL_TEXTURE_2D)

        # Draw transparent projection surfaces with depth read but no depth write
        # so they appear in front of the sphere where appropriate but don't
        # occlude each other
        glDepthMask(GL_FALSE)

        if self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Cylindrical:
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
            cyl_size *= 0.9  # trimmed 10%: there was more headroom than the map needs
            glPushMatrix()
            # Keep cylinder fixed (vertical) - Earth rotates inside it
            # This shows what happens when different great circles become tangent to the cylinder
            glTranslatef(0.0, 0.0, -self.earth_radius * cyl_size / 2)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.14)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            if self.surface_unroll == 0:
                gluCylinder(self.plain_quad, self.earth_radius * 1.01, self.earth_radius * 1.01, self.earth_radius * cyl_size, 32, 64)
            else:
                self.draw_cylinder_surface(cyl_size)
            glPopMatrix()
            # Draw "Projection" text at bottom of cylinder
            if self.surface_unroll == 0:
                self.draw_cylinder_label(cyl_size)
            if self.draw_rays:
                self.draw_shape_rays()
            glDisable(GL_BLEND)
        elif self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.PseudoCylindrical:
            # Draw shaped projection surface for pseudo-cylindrical projections
            # The surface shape reveals the projection's characteristic (ellipse, pointed, etc.)
            self.draw_pseudocylindrical_surface()
            if self.draw_rays:
                self.draw_shape_rays()
            glDisable(GL_BLEND)
        elif self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Conic:
            # Draw cone for conic projections
            r = self.earth_radius
            base_r, h, apex_z = self._conic_cone_geometry()

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.5)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            if self.surface_unroll == 0:
                glPushMatrix()
                glTranslatef(0.0, 0.0, apex_z - h)
                gluCylinder(self.plain_quad, base_r, 0, h, 32, 64)
                glPopMatrix()
            else:
                self.draw_cone_surface()

            # Draw standard parallels circles on the cone surface
            glDisable(GL_TEXTURE_2D)
            glLineWidth(2.0)
            glColor4f(1.0, 0.8, 0.2, 0.9)  # Orange/yellow for standard parallels

            # Draw each standard parallel where the cone surface crosses that
            # latitude. On the first one the cone is tangent, so the circle
            # sits exactly on the sphere. Drawn in world coordinates and put
            # through the unroll, so they follow the cone as it flattens.
            projection = self.cartographer.projection_panel.projection
            if hasattr(projection, 'phi1') and hasattr(projection, 'phi2'):
                slope = base_r / h
                for phi in (projection.phi1, projection.phi2):
                    world_z = r * math.sin(phi)
                    circle_r = slope * (apex_z - world_z)
                    if circle_r <= 0 or not (apex_z - h <= world_z <= apex_z):
                        continue
                    # a strip rather than a loop, so the cut stays open
                    glBegin(GL_LINE_STRIP)
                    for i in range(65):
                        theta = -math.pi + 2.0 * math.pi * i / 64
                        glVertex3f(*self._unroll_cone_point(
                            circle_r * math.sin(theta),
                            -circle_r * math.cos(theta), world_z))
                    glEnd()

            # Draw apex point marker
            glColor4f(1.0, 1.0, 0.0, 1.0)
            glPointSize(8.0)
            glBegin(GL_POINTS)
            glVertex3f(*self._unroll_cone_point(0.0, 0.0, apex_z))
            glEnd()
            glPointSize(1.0)

            glEnable(GL_TEXTURE_2D)
            glLineWidth(1.0)

            if self.draw_rays:
                self.draw_shape_rays()
            glDisable(GL_BLEND)
        elif self.cartographer.projection_panel.projection.projection_type == self.cartographer.projection_panel.projection.ProjectionType.Azimuthal:
            # Draw the projection plane, tangent at the front of the globe (the
            # equatorial/oblique aspect the 2D panel draws). The disk is built
            # in its own xy-plane, then rotated to face -y and pushed out front.
            self._az_scale = self._azimuthal_scale()
            glPushMatrix()
            disk_size = 3
            glTranslatef(0.0, -self.earth_radius * self.AZ_PLANE_DIST, 0.0)
            glRotatef(90, 1, 0, 0)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glColor4f(1.0, 1.0, 1.0, 0.5)
            glBindTexture(GL_TEXTURE_2D, self.plain_texture)
            gluDisk(self.plain_quad, 0, self.earth_radius * disk_size, 32, 64)

            # Draw center point marker
            self.draw_circle(0, 0.01, 6)

            # Draw distance rings for azimuthal equidistant
            ray_type = self.get_azimuthal_ray_type()
            if ray_type == 'equidistant':
                projection = self.cartographer.projection_panel.projection
                glDisable(GL_TEXTURE_2D)
                glColor4f(0.8, 0.8, 1.0, 0.3)  # Light blue for distance rings
                glLineWidth(1.0)
                # Rings at fixed angular distances from the centre, sized with
                # the same scale as the map so they line up with the continents.
                for angle_deg in [30, 60, 90, 120, 150]:
                    try:
                        px, py = projection.get_coords(math.radians(angle_deg), 0.0)
                    except (ValueError, ZeroDivisionError, OverflowError):
                        continue
                    ring_radius = math.hypot(px, py) * self._az_scale
                    glBegin(GL_LINE_LOOP)
                    for i in range(64):
                        theta = 2.0 * math.pi * i / 64
                        x = ring_radius * math.cos(theta)
                        y = ring_radius * math.sin(theta)
                        glVertex3f(x, y, 0)
                    glEnd()
                glEnable(GL_TEXTURE_2D)

            glPopMatrix()
            if self.draw_rays:
                self.draw_shape_rays()
            glDisable(GL_BLEND)

        self.draw_earth()

        glDepthMask(GL_TRUE)

        self.SwapBuffers()

    def draw_earth(self):
        """Draw the earth sphere as translucent glass, on top of everything else.

        It goes last and semi-transparent on purpose: the rays converge at the
        centre of the earth, so drawing an opaque sphere first (or letting it
        write depth) hides exactly the part of the picture that shows where the
        projection starts. Back-face culling keeps it to a single layer.
        """
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        glColor4f(1.0, 1.0, 1.0, self.earth_alpha / 100.0)

        glPushMatrix()
        glRotatef(self.earthy, 1.0, 0.0, 0.0)
        glRotatef(self.earthx, 0.0, 0.0, 1.0)
        glRotatef(self.earthz, 0.0, 1.0, 0.0)
        glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        gluSphere(self.earth_quad, self.earth_radius, 32, 32)
        glPopMatrix()

        glDisable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        glColor4f(1.0, 1.0, 1.0, 1.0)

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
        if self.surface_unroll == 0:
            return (x, y, z)

        f = self.surface_unroll / 100.0
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
        unwrap_factor = self.surface_unroll / 100.0
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

        # Shade the markers and degree labels by distance, exactly as the rays
        # and coastlines are: they ring the whole cylinder, so without it the
        # ones on the far side read as brightly as the ones facing the viewer.
        cue_axis = zx, zy, zz = self._eye_depth_axis()
        cue_extent = r * math.hypot(zx, zy) + (height / 2.0) * abs(zz)
        fogged = self._begin_depth_cue(cue_extent)

        def fade(x, y, local_z):
            """Depth fade for something drawn at this spot on the cylinder."""
            return self._depth_fade((x, y, local_z - height / 2.0),
                                    cue_axis, cue_extent)

        glPushMatrix()
        glTranslatef(0.0, 0.0, -height / 2)

        # Disable textures
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)

        # Draw 8 short vertical lines evenly spaced around the cylinder
        glLineWidth(2.0)

        line_length = 0.3  # Length of the short lines
        n_lines = 8  # Number of lines around the cylinder

        for i in range(n_lines):
            angle = 2 * math.pi * i / n_lines  # Every 45 degrees
            x = r * math.cos(angle)
            y = r * math.sin(angle)

            # Line at bottom
            glColor4f(0.7, 0.7, 0.7, 0.4 * fade(x, y, line_length / 2))
            glBegin(GL_LINES)
            glVertex3f(x, y, 0)
            glVertex3f(x, y, line_length)
            glEnd()

            # Line at top
            glColor4f(0.7, 0.7, 0.7,
                      0.4 * fade(x, y, height - line_length / 2))
            glBegin(GL_LINES)
            glVertex3f(x, y, height - line_length)
            glVertex3f(x, y, height)
            glEnd()

        glLineWidth(1.0)

        # Draw longitude labels (0, 90, 180, 270) as if printed on cylinder surface
        # Using the coordinate system: x = r*sin(lon), y = -r*cos(lon)
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
            glColor4f(0.3, 0.3, 0.3, 0.9 * fade(text_x, text_y, text_z_offset_bottom))
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
            glColor4f(0.3, 0.3, 0.3,
                      0.9 * fade(text_x, text_y, height - text_z_offset_top))
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

        if fogged:
            glDisable(GL_FOG)

        # Re-enable textures
        glEnable(GL_TEXTURE_2D)

    # How far in front of the globe the azimuthal projection plane sits, in
    # earth radii. The plane is tangent to the front (equator point facing the
    # viewer), giving the same equatorial/oblique aspect the 2D panel draws.
    AZ_PLANE_DIST = 2.5

    def _azimuthal_scale(self):
        """Fixed scale mapping a projection's formula output onto the plane.

        A single scale, like the 2D panel's fixed zoom, keeps every projection
        at its own natural relative size, so the 3D map shows the same extent as
        the 2D panel. The formula constants all top out near 170, which this
        maps to about 2.5 earth radii (the disc that holds the map).
        """
        return self.earth_radius / 68.0

    def _azimuthal_formula_xy(self, lon_deg, lat_deg):
        """Where a point lands on the plane, from the projection's own 2D formula.

        Uses the panel's exact convention - screen-x from -proj_x, up from
        +proj_y, longitude taken the same way round - so the flat map is
        identical to the 2D panel for every azimuthal projection, symmetric or
        not (Weichel, unlike the others, is not symmetric in longitude).
        """
        projection = self.cartographer.projection_panel.projection
        try:
            proj_x, proj_y = projection.get_coords(math.radians(lon_deg),
                                                   math.radians(lat_deg))
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
        if abs(proj_x) > 5000 or abs(proj_y) > 5000:
            return None  # sentinel a formula returns for points it cannot show
        s = self._az_scale
        return (-proj_x * s, proj_y * s)

    def _compute_azimuthal_intersection(self, px, py, pz):
        """Where a sphere point lands on the azimuthal projection plane.

        Placed straight from the projection's own 2D formula, in the panel's
        convention, so the flat map matches the 2D panel for every azimuthal
        projection and for the whole world - both hemispheres, not just the
        front. The plane is tangent at the front of the globe (the equatorial
        aspect the 2D panel draws).

        px, py, pz: rotated point on the sphere surface (radius = earth_radius).
        Returns (ix, iy, iz) on the plane (y = -D) or None.
        """
        r = self.earth_radius
        plane_y = -r * self.AZ_PLANE_DIST

        radius = math.sqrt(px * px + py * py + pz * pz)
        if radius < 1e-9:
            return None
        lon_eff = math.degrees(math.atan2(-px, -py))
        lat_eff = math.degrees(math.asin(max(-1.0, min(1.0, pz / radius))))
        proj = self._azimuthal_formula_xy(lon_eff, lat_eff)
        if proj is None:
            return None
        ix, iz = proj

        # Keep the map on the plane (matches the 2D panel clipping at its edge)
        if ix * ix + iz * iz > (r * 3.0) ** 2:
            return None

        return (ix, plane_y, iz)

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
            base_r, h, apex_z = self._conic_cone_geometry()
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

        if proj_type == ProjectionType.PseudoCylindrical:
            # The pseudo-cylindrical map is a flat sheet, so two neighbouring
            # points on it are joined by a straight segment. These points used
            # to be forced through the cylinder path below, which bent the
            # coastline onto a cylinder wrapped round the globe instead of
            # leaving it lying flat on the map.
            return [p1, p2]

        if proj_type == ProjectionType.Cylindrical:
            cyl_r = r * 1.01  # Same as draw_cylinder_surface
            # When unwrapped, work backwards from unwrapped coords to get phi
            # phi is the angle from back (phi=0 at back/-y, phi=±pi at front/+y)
            if self.surface_unroll > 0:
                # p1 and p2 are already unwrapped (from _intersect_ray)
                # Recover phi using Newton's method
                f = self.surface_unroll / 100.0
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
            # Skip segments that jump a long way round the cylinder: adjacent
            # coastline samples never span this much longitude unless they wrap
            # across the seam or round the pole, where the line would be spurious.
            if abs(dphi) > math.pi * 0.5:
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
            if self.surface_unroll > 0:
                # Once the cone is opening out the points are already unrolled,
                # and the flattening surface is close enough to flat between two
                # neighbouring samples that a straight segment sits on it.
                return [p1, p2]

            base_r, h, apex_z = self._conic_cone_geometry()
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
            # Skip segments that jump a long way round the cone (see cylinder).
            if abs(dtheta) > math.pi * 0.5:
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

    def _get_cylinder_point(self, lon_deg, lat_deg):
        """Where a lat/lon lands on the cylinder, using the projection's own formula.

        The height comes from the 2D projection object itself, divided by that
        projection's own longitude scale and multiplied by the cylinder radius.
        One radian of longitude is exactly one radius around the circumference,
        so that reproduces whatever aspect ratio the projection panel draws,
        for any cylindrical projection.

        Asking the projection rather than reimplementing its formula here is
        what stops the two panels drifting apart. Miller had no case of its own
        and fell through to a plain geometric ray/cylinder hit, which is the
        central cylindrical projection: it runs away as tan(lat) and came out
        far taller than the Miller map next to it.
        """
        r = self.earth_radius
        cyl_r = r * 1.01  # Same radius as cylinder

        lon = math.radians(lon_deg)

        # Position around cylinder (from longitude)
        # Match the coordinate system: negative sin for x, negative cos for y
        x = cyl_r * math.sin(lon)
        y = -cyl_r * math.cos(lon)

        # Stay off the poles, where every cylindrical formula runs to infinity
        lat = math.radians(max(-89.0, min(89.0, lat_deg)))

        projection = self.cartographer.projection_panel.projection
        try:
            lon_scale = projection.get_coords(1.0, 0.0)[0]  # units per radian
            height = projection.get_coords(0.0, lat)[1]
        except (ValueError, OverflowError, ZeroDivisionError):
            return (x, y, 0.0)

        if not lon_scale:
            return (x, y, 0.0)

        z = cyl_r * height / lon_scale
        # Keep the map on the cylinder even if a formula still runs away
        limit = r * 3.5
        return (x, y, max(-limit, min(limit, z)))

    def draw_cone_surface(self):
        """Draw the cone as a mesh, so it can be shown part way through unrolling.

        gluCylinder can only draw the closed cone; once the cut opens the
        surface has to be built by hand, the same way the cylinder does it.
        """
        base_r, h, apex_z = self._conic_cone_geometry()
        alpha = math.atan2(base_r, h)
        sin_a, cos_a = math.sin(alpha), math.cos(alpha)
        if cos_a < 1e-9:
            return

        s_max = h / cos_a  # slant distance from apex to the rim
        n_slices = 64
        n_stacks = 24
        # gap at the cut edges, widening as the cone opens
        eps = 0.001 + (self.surface_unroll / 100.0) * 0.02
        span = 2.0 * math.pi - 2.0 * eps

        def vertex(s, theta, tex_s, tex_t):
            axis_r = s * sin_a
            glTexCoord2f(tex_s, tex_t)
            glVertex3f(*self._unroll_cone_point(axis_r * math.sin(theta),
                                                -axis_r * math.cos(theta),
                                                apex_z - s * cos_a))

        for j in range(n_stacks):
            s0 = s_max * j / float(n_stacks)
            s1 = s_max * (j + 1) / float(n_stacks)
            glBegin(GL_QUAD_STRIP)
            for i in range(n_slices + 1):
                frac = i / float(n_slices)
                theta = -math.pi + eps + frac * span
                vertex(s0, theta, frac, j / float(n_stacks))
                vertex(s1, theta, frac, (j + 1) / float(n_stacks))
            glEnd()

    def _unroll_cone_point(self, x, y, z):
        """Transform a point on the cone to its unrolled position.

        A cone flattens isometrically into a circular sector. A point at slant
        distance s from the apex stays at distance s from the sector's apex,
        but its angle round the axis shrinks by sin(half angle): the circle of
        circumference 2*pi*s*sin(a) has to open out into an arc of radius s,
        which only spans 2*pi*sin(a). That factor is what makes the flattened
        cone a fan rather than a full disc, and it is the whole reason a conic
        map has a wedge missing.

        Like the cylinder, the cut opens at the front, the back stays put, and
        the flattened surface finishes behind the earth. Unlike the cylinder,
        z moves too: the cone's slant becomes radius in the flat sector.
        """
        if self.surface_unroll == 0:
            return (x, y, z)

        base_r, h, apex_z = self._conic_cone_geometry()
        alpha = math.atan2(base_r, h)
        sin_a, cos_a = math.sin(alpha), math.cos(alpha)
        if cos_a < 1e-9:
            return (x, y, z)

        # slant distance from the apex, and angle round the axis measured from
        # the back so the cut lands at the front, as the cylinder does
        s = (apex_z - z) / cos_a
        phi = math.atan2(-x, -y)

        # the sector: same distance from the apex, angle scaled by sin(alpha)
        theta = phi * sin_a
        end_x = -s * math.sin(theta)
        end_y = -self.earth_radius
        end_z = apex_z - s * math.cos(theta)

        f = self.surface_unroll / 100.0
        smooth_f = f * f * (3 - 2 * f)
        return ((1 - smooth_f) * x + smooth_f * end_x,
                (1 - smooth_f) * y + smooth_f * end_y,
                (1 - smooth_f) * z + smooth_f * end_z)

    def _get_cone_point(self, lon_deg, lat_deg):
        """Where a lat/lon lands on the cone, using the projection's own formula.

        A conic projection is polar about the cone's apex: it puts a point at
        some radius from the apex, at an angle proportional to longitude.
        Wrapping that back onto the drawn cone means reading that radius and
        turning it into a slant distance from the apex. Only the scale is
        unknown, and the standard parallel fixes it: there the cone touches the
        sphere, so that one distance has to come out exactly right.

        This replaces a geometric ray/cone intersection that had two problems.
        It produced an identical picture for Lambert and Albers, since it never
        consulted either formula; and a ray from the centre of a sphere misses
        a finite cone entirely for much of the globe, so everything below about
        35S was silently dropped.

        Returns None past the end of the drawn cone, where conic projections
        run away towards the far pole.
        """
        projection = self.cartographer.projection_panel.projection
        n = getattr(projection, 'n', None)
        if not n:
            return None

        base_r, h, apex_z = self._conic_cone_geometry()
        alpha = math.atan2(base_r, h)  # half angle of the cone as drawn
        sin_a, cos_a = math.sin(alpha), math.cos(alpha)
        if cos_a < 1e-9:
            return None

        r = self.earth_radius
        phi_c = math.radians(max(5.0, min(85.0, self.standard_parallel1)))
        # slant distance from apex to the parallel where the cone touches
        s_tangent = (apex_z - r * math.sin(phi_c)) / cos_a

        def apex_radius(lat_rad):
            # Sample a quarter turn around the cone. There the projection's own
            # radius appears undiluted in x, and any constant offset it adds to
            # y (Albers has one, for centring) drops out.
            return abs(projection.get_coords(math.pi / (2.0 * n), lat_rad)[0])

        try:
            rho_ref = apex_radius(phi_c)
            rho = apex_radius(math.radians(max(-89.0, min(89.0, lat_deg))))
        except (ValueError, OverflowError, ZeroDivisionError):
            return None
        if rho_ref <= 1e-9:
            return None

        s = s_tangent * rho / rho_ref
        if s < 0.0 or s > h / cos_a:
            return None  # beyond the drawn cone

        axis_r = s * sin_a
        lon = math.radians(lon_deg)
        return self._unroll_cone_point(axis_r * math.sin(lon),
                                       -axis_r * math.cos(lon),
                                       apex_z - s * cos_a)

    def _generate_ray(self, sphere_pt, target_pt, steps=20):
        """Generate a ray from the earth's centre to a point on a projection surface.

        The ray is radial and straight from the centre out to the sphere
        surface, and from there a quadratic Bezier bends towards the target.
        The Bezier's control point sits on the radial line, so the curve leaves
        the surface travelling in exactly the direction the radial part arrived
        in: the two meet smoothly instead of at a visible angle.

        The bend is not decoration. Projections like Mercator are not
        geometric: a straight ray out of the centre reaches the cylinder at
        r*tan(lat), while Mercator puts the point at r*asinh(tan(lat)). Past
        60 degrees those differ by more than an earth radius, so the ray has to
        turn to land in the right place, and how hard it turns is exactly how
        far the projection departs from a straight-line one.
        """
        sx, sy, sz = sphere_pt
        tx, ty, tz = target_pt

        s_len = math.sqrt(sx * sx + sy * sy + sz * sz)
        if s_len < 1e-9:
            return [(0.0, 0.0, 0.0), (tx, ty, tz)]
        ux, uy, uz = sx / s_len, sy / s_len, sz / s_len

        # Control point: keep going radially for half of however far the target
        # lies outwards. Using the outward part only keeps the curve from
        # bulging back out past the surface when the target sits below it.
        radial_gap = (tx - sx) * ux + (ty - sy) * uy + (tz - sz) * uz
        k = max(0.0, radial_gap) * 0.5
        cx, cy, cz = sx + k * ux, sy + k * uy, sz + k * uz

        inner = max(1, steps // 2)
        outer = max(1, steps - inner)

        points = [(0.0, 0.0, 0.0)]
        for i in range(1, inner + 1):  # centre -> surface, straight and radial
            f = i / float(inner)
            points.append((f * sx, f * sy, f * sz))
        for i in range(1, outer + 1):  # surface -> target, quadratic Bezier
            t = i / float(outer)
            a = (1.0 - t) * (1.0 - t)
            b = 2.0 * (1.0 - t) * t
            c = t * t
            points.append((a * sx + b * cx + c * tx,
                           a * sy + b * cy + c * ty,
                           a * sz + b * cz + c * tz))
        return points

    def _begin_depth_cue(self, extent):
        """Fade rays and projected coastlines towards the background with distance.

        Rays and coastlines wrap all the way around the sphere, so the far half
        of the picture lands on top of the near half on screen. With every line
        drawn at the same brightness the two are impossible to separate and the
        shape of the projection is lost. Linear fog in the background colour
        dims by eye distance, which reads as depth.

        Args:
            extent: how far the drawn geometry reaches towards and away from
                the viewer, in world units. The fog ramp is fitted to exactly
                this span; making it wider leaves every line bunched in the
                middle of the ramp and the effect barely shows.

        The ramp is placed so the nearest geometry keeps its full brightness
        and the furthest loses `depth_cue` of it, and it is rebuilt from the
        current view distance each frame so the cue survives zooming.
        """
        if self.depth_cue <= 0.0 or extent <= 1e-6:
            return False

        dist = abs(self.view_distance)
        d = min(0.99, self.depth_cue)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, [0.0, 0.0, 0.0, 1.0])
        glFogf(GL_FOG_START, dist - extent)
        glFogf(GL_FOG_END, dist + extent * (2.0 - d) / d)
        glEnable(GL_FOG)
        return True

    def _eye_depth_axis(self):
        """The world-space direction that becomes eye-space depth, from the modelview.

        The depth cue has to know how far the geometry really reaches towards
        and away from the viewer, and that depends on how the view is turned:
        the cylinder spans only its radius in depth seen from the side, but its
        whole length seen end-on. Reading the axis off the matrix keeps the cue
        correct at any rotation instead of assuming one particular view.
        """
        mv = glGetFloatv(GL_MODELVIEW_MATRIX)
        # eye z of a world point is zx*x + zy*y + zz*z + constant (column-major)
        return float(mv[0][2]), float(mv[1][2]), float(mv[2][2])

    def _points_depth_extent(self, points):
        """How far world-space points reach either side of the centre, in depth."""
        zx, zy, zz = self._eye_depth_axis()
        extent = 0.0
        for px, py, pz in points:
            extent = max(extent, abs(zx * px + zy * py + zz * pz))
        return extent

    def _depth_fade(self, point, axis, extent):
        """How much of its strength a line at this point keeps, 1 nearest to 1-depth_cue furthest.

        Fog on its own only darkens, and a darkened line drawn over the pale
        cylinder just turns into a dark line: still high contrast, so the far
        side refuses to recede however hard the fog is pushed. Fading the alpha
        as well lets distant geometry dissolve into whatever sits behind it,
        which is what actually reads as distance.
        """
        if self.depth_cue <= 0.0 or extent <= 1e-6:
            return 1.0
        zx, zy, zz = axis
        # positive is towards the viewer, since eye z grows towards the eye
        towards = zx * point[0] + zy * point[1] + zz * point[2]
        far = (extent - towards) / (2.0 * extent)  # 0 nearest, 1 furthest
        return 1.0 - self.depth_cue * min(1.0, max(0.0, far))

    def draw_shape_rays(self):
        r = self.earth_radius
        projection = self.cartographer.projection_panel.projection
        proj_type = projection.projection_type
        ProjectionType = projection.ProjectionType

        # Use shapes selected from Resolution menu (synced with 2D panel)
        shapes = self.opengl_shapes

        rotate = self._earth_rotate

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

        # Every cylindrical projection is placed from its own formula, rather
        # than only the two that used to be recognised by class name. Anything
        # not matched fell through to a geometric ray/cylinder hit, which is a
        # different projection entirely and did not match the 2D panel.
        is_cylindrical = (proj_type == ProjectionType.Cylindrical)
        is_conic = (proj_type == ProjectionType.Conic)
        is_azimuthal = (proj_type == ProjectionType.Azimuthal)

        # Normalising scale for the azimuthal formula-based projections, so the
        # flat map matches the 2D panel's shape at a sensible on-screen size.
        if is_azimuthal:
            self._az_scale = self._azimuthal_scale()

        # Collect sampled points (flat list for rays/dots) and
        # part-aware intersection lists (for outlines)
        all_intersections = []
        all_sphere_points = []
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

                    # Calculate projection surface intersection point
                    if is_cylindrical:
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

                            # Use effective lat/lon with the projection's own formula
                            mx, my, mz = self._get_cylinder_point(lon_eff_deg, lat_eff_deg)
                            # Apply cylinder unwrap transformation
                            hit = self._unwrap_point(mx, my, mz)

                            if hit is not None:
                                all_intersections.append(hit)
                                all_sphere_points.append((px, py, pz))
                                # Store effective lat/lon for ray curvature calculation
                                part_hits.append(hit)
                        else:
                            hit = None
                    elif is_conic:
                        # The cone is fixed while the earth turns inside it, so
                        # the point has to be placed by its world-space lat/lon
                        sphere_radius = math.sqrt(px * px + py * py + pz * pz)
                        if sphere_radius > 1e-9:
                            lat_eff = math.asin(pz / sphere_radius)
                            lon_eff = math.atan2(px, -py)
                            hit = self._get_cone_point(math.degrees(lon_eff),
                                                       math.degrees(lat_eff))
                            if hit is not None:
                                all_intersections.append(hit)
                                all_sphere_points.append((px, py, pz))
                                part_hits.append(hit)
                    elif proj_type == ProjectionType.PseudoCylindrical:
                        # Use the rotated (effective) lat/lon, exactly as the
                        # cylindrical and conic cases do, so the continents on
                        # the flat map move and deform as the earth turns and
                        # match what the 2D panel draws.
                        sphere_radius = math.sqrt(px * px + py * py + pz * pz)
                        if sphere_radius > 1e-9:
                            lat_eff = math.asin(pz / sphere_radius)
                            lon_eff = math.atan2(px, -py)
                            hit = self._compute_pseudocylindrical_surface_point(
                                math.degrees(lon_eff), math.degrees(lat_eff))
                            if hit is not None:
                                all_intersections.append(hit)
                                all_sphere_points.append((px, py, pz))
                                part_hits.append(hit)
                    else:
                        # Use geometric projection for other types
                        # Special handling for azimuthal projections with different ray origins
                        if proj_type == ProjectionType.Azimuthal:
                            hit = self._compute_azimuthal_intersection(px, py, pz)
                        else:
                            hit = ray_intersect(px, py, pz)

                        if hit is not None:
                            all_intersections.append(hit)
                            all_sphere_points.append((px, py, pz))
                            part_hits.append(hit)
                if len(part_hits) >= 2:
                    part_intersections.append(part_hits)

        if not all_intersections:
            return

        # Disable texture for drawing lines (rays and outlines)
        glDisable(GL_TEXTURE_2D)

        # Shade both the rays and the projected coastlines by distance: fog
        # darkens them, and the per-line alpha fade below makes them recede
        cue_axis = self._eye_depth_axis()
        cue_extent = self._points_depth_extent(all_intersections)
        fogged = self._begin_depth_cue(cue_extent)

        # Only draw rays and dots when cylinder is fully closed (not unfolding)
        # During unfolding, the 3D projection concept doesn't apply
        if self.surface_unroll == 0:
            # Draw rays showing how projection works
            # Depth testing is enabled, so Earth will hide the interior portions
            glLineWidth(1.0)
            ray_alpha = self.ray_alpha / 100.0  # Convert 0-100 slider to 0.0-1.0
            # Normal alpha blending here: with the additive blending used for the
            # solids, overlapping rays pile up channel by channel and wash out to
            # white, which hides the colour completely where the rays are dense.
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            for i, (ix, iy, iz) in enumerate(all_intersections):
                sphere_pt = all_sphere_points[i]
                # Light blue, faded by how far away this ray lands
                glColor4f(0.45, 0.65, 1.0,
                          ray_alpha * self._depth_fade((ix, iy, iz), cue_axis, cue_extent))

                if is_cylindrical or is_conic:
                    # Ray from the centre out to where the projection puts the
                    # point on the cylinder or cone; how far it bends is how far
                    # the projection departs from a straight-line one
                    ray_points = self._generate_ray(sphere_pt, (ix, iy, iz), steps=20)
                    glBegin(GL_LINE_STRIP)
                    for px, py, pz in ray_points:
                        glVertex3f(px, py, pz)
                    glEnd()
                elif proj_type == ProjectionType.PseudoCylindrical:
                    # A straight correspondence line joining the point on the
                    # globe to where it lands on the flat map. There is no
                    # surface to project onto for these projections, so the old
                    # curved ray implied a geometry that does not exist; a
                    # straight "this point goes there" line is the honest story.
                    # Only drawn for the hemisphere facing the map (py < 0), so
                    # the lines reach the map without cutting back through the
                    # globe.
                    if sphere_pt[1] < 0:
                        glBegin(GL_LINES)
                        glVertex3f(*sphere_pt)
                        glVertex3f(ix, iy, iz)
                        glEnd()
                elif proj_type == ProjectionType.Azimuthal:
                    # Correspondence line from the globe point to where it lands
                    # on the map, for every point so nothing is left unconnected.
                    # Back-hemisphere lines pass through the translucent globe.
                    glBegin(GL_LINES)
                    glVertex3f(*sphere_pt)
                    glVertex3f(ix, iy, iz)
                    glEnd()
                else:
                    # Draw straight ray from center for other projections
                    glBegin(GL_LINES)
                    glVertex3f(0, 0, 0)
                    glVertex3f(ix, iy, iz)
                    glEnd()

        # Draw continent outlines on projection surface.
        # These write depth (unlike everything else here) so the translucent
        # earth, drawn afterwards, is depth-rejected wherever a coastline sits
        # in front of it - otherwise the earth paints over the near-side
        # projected continents and hides them. Rays keep writing no depth, so
        # the earth still shows through as glass over them.
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)
        glDepthMask(GL_TRUE)

        import math as m

        cyl_radius = r * 1.01

        for part_hits in part_intersections:
            for j in range(len(part_hits) - 1):
                # Drop coastline segments that jump across the surface: adjacent
                # samples that wrap over the back seam, or round the effective
                # pole where longitude spins. Left in, they draw a long line
                # straight across the map connecting two unrelated points.
                a, b = part_hits[j], part_hits[j + 1]
                skip = False
                if self.surface_unroll > 0 and proj_type == ProjectionType.Conic:
                    # Opened cone: every point sits at nearly the same y, so the
                    # jump shows up as a big straight-line distance across the fan.
                    skip = m.dist(a, b) > r * 1.5
                elif self.surface_unroll > 0:
                    # Opening cylinder: measure the angle round the axis.
                    ad = abs(m.atan2(a[1], a[0]) - m.atan2(b[1], b[0]))
                    if ad > m.pi:
                        ad = 2 * m.pi - ad
                    skip = ad > m.pi / 2
                elif proj_type == ProjectionType.PseudoCylindrical:
                    # Flat map: the antimeridian jump spans the map width in x.
                    skip = abs(a[0] - b[0]) > r * 1.5
                elif proj_type in (ProjectionType.Cylindrical, ProjectionType.Conic):
                    # Wrapped cylinder / cone: a seam or pole jump is a big step
                    # AROUND the axis, i.e. a big horizontal (xy) distance. Using
                    # only the horizontal part keeps a tall map's legitimate
                    # vertical stretch (Mercator near the poles) from being cut.
                    skip = m.hypot(a[0] - b[0], a[1] - b[1]) > r * 1.2
                elif proj_type == ProjectionType.Azimuthal:
                    # Flat disc: skip a straight segment that leaps across it.
                    skip = m.dist(a, b) > r * 1.5
                if skip:
                    continue

                seg = self._interpolate_on_surface(
                    part_hits[j], part_hits[j + 1], proj_type, ProjectionType)
                if len(seg) >= 2:
                    mid = seg[len(seg) // 2]
                    glBegin(GL_LINE_STRIP)
                    glColor4f(0.0, 1.0, 1.0,
                              0.8 * self._depth_fade(mid, cue_axis, cue_extent))
                    for sx, sy, sz in seg:
                        glVertex3f(sx, sy, sz)
                    glEnd()

        if fogged:
            glDisable(GL_FOG)

        glDepthMask(GL_FALSE)
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

    def draw_pseudocylindrical_surface(self):
        """Draw the characteristic surface shape for pseudo-cylindrical projections.

        Creates a mesh showing the projection's shape (ellipse, pointed poles, etc.)
        positioned in front of the Earth.
        """
        r = self.earth_radius
        projection = self.cartographer.projection_panel.projection
        proj_type = self.get_pseudocylindrical_type()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(0.7, 0.9, 1.0, 0.2)  # Light blue, semi-transparent
        glDisable(GL_TEXTURE_2D)

        # Draw a mesh grid showing the projection surface
        # Sample latitudes and longitudes to create the mesh
        lat_steps = 20
        lon_steps = 36

        # The graticule turns with the earth (the geographic grid drawn in the
        # oblique aspect), matching the 2D panel. A segment that jumps across
        # the antimeridian spans most of the map, so skip those.
        max_step = r * 1.5

        glBegin(GL_LINES)

        # Draw meridians (longitude lines)
        for i_lon in range(lon_steps):
            lon_deg = -180 + i_lon * 360.0 / lon_steps
            prev_pt = None
            for i_lat in range(lat_steps + 1):
                lat_deg = -90 + i_lat * 180.0 / lat_steps
                pt = self._pseudocyl_surface_point_geo(lon_deg, lat_deg)
                if pt is not None and prev_pt is not None and \
                        abs(pt[0] - prev_pt[0]) < max_step:
                    glVertex3f(prev_pt[0], prev_pt[1], prev_pt[2])
                    glVertex3f(pt[0], pt[1], pt[2])
                prev_pt = pt

        # Draw parallels (latitude lines)
        for i_lat in range(lat_steps + 1):
            lat_deg = -90 + i_lat * 180.0 / lat_steps
            prev_pt = None
            for i_lon in range(lon_steps + 1):
                lon_deg = -180 + i_lon * 360.0 / lon_steps
                pt = self._pseudocyl_surface_point_geo(lon_deg, lat_deg)
                if pt is not None and prev_pt is not None and \
                        abs(pt[0] - prev_pt[0]) < max_step:
                    glVertex3f(prev_pt[0], prev_pt[1], prev_pt[2])
                    glVertex3f(pt[0], pt[1], pt[2])
                prev_pt = pt

        glEnd()

        # Outline the map boundary - the +/-180 meridians traced pole to pole -
        # so the characteristic silhouette reads at a glance: pointed poles for
        # Sinusoidal, an ellipse for Mollweide, a diamond for Collignon.
        glColor4f(1.0, 1.0, 1.0, 0.6)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for i_lat in range(lat_steps + 1):
            lat_deg = -90 + i_lat * 180.0 / lat_steps
            pt = self._compute_pseudocylindrical_surface_point(-180, lat_deg)
            if pt is not None:
                glVertex3f(*pt)
        for i_lat in range(lat_steps + 1):
            lat_deg = 90 - i_lat * 180.0 / lat_steps
            pt = self._compute_pseudocylindrical_surface_point(180, lat_deg)
            if pt is not None:
                glVertex3f(*pt)
        glEnd()

        glEnable(GL_TEXTURE_2D)
        glLineWidth(1.0)

    def set_standard_parallels(self, phi1, phi2):
        """Set standard parallels for conic projections.

        Args:
            phi1, phi2: Standard parallel values in degrees

        Kept in degrees: the cone drawing code scales them to earth radii
        where it needs them, so don't pre-scale here.
        """
        self.standard_parallel1 = phi1
        self.standard_parallel2 = phi2

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

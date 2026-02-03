import math
import wx

from PIL.Image import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx import glcanvas
from wx.glcanvas import GLCanvas


class EarthCanvas(GLCanvas):

    def __init__(self, parent, cartographer):
        GLCanvas.__init__(self, parent, -1, style=wx.SUNKEN_BORDER, attribList=[
            wx.glcanvas.WX_GL_DOUBLEBUFFER,
            wx.glcanvas.WX_GL_DEPTH_SIZE, 24,
        ])
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
        self.draw_rays = True
        self.ray_density = 50
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

    def InitGL(self):
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
            cyl_size = 6
            glPushMatrix()
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

    def draw_shape_rays(self):
        r = self.earth_radius
        projection = self.cartographer.projection_panel.projection
        proj_type = projection.projection_type
        ProjectionType = projection.ProjectionType

        shapes = self.cartographer.projection_panel.shapes

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
                    if count % self.ray_density != 0:
                        continue
                    p = points[i]
                    px, py, pz = sphere_point(p[0], p[1])
                    hit = ray_intersect(px, py, pz)
                    if hit is not None:
                        all_intersections.append(hit)
                        all_sphere_points.append((px, py, pz))
                        part_hits.append(hit)
                if len(part_hits) >= 2:
                    part_intersections.append(part_hits)

        if not all_intersections:
            return

        # Draw rays as lines from center of earth to projection surface
        glDisable(GL_TEXTURE_2D)
        glLineWidth(1.0)
        ray_alpha = self.ray_alpha / 100.0  # Convert 0-100 slider to 0.0-1.0
        glBegin(GL_LINES)
        glColor4f(0.4, 0.4, 0.0, ray_alpha)
        for ix, iy, iz in all_intersections:
            glVertex3f(0, 0, 0)
            glVertex3f(ix, iy, iz)
        glEnd()

        # Draw dots at intersections and on earth surface
        dot_size = max(2.0, min(10.0, 1000.0 / max(1, len(all_intersections))))
        glPointSize(dot_size)
        glBegin(GL_POINTS)
        glColor4f(1.0, 0.0, 0.0, 0.8)
        for ix, iy, iz in all_intersections:
            glVertex3f(ix, iy, iz)
        for sx, sy, sz in all_sphere_points:
            glVertex3f(sx, sy, sz)
        glEnd()

        # Draw continent outlines on projection surface
        # Switch to standard alpha blending so outlines overlay the surface
        # instead of being washed out by additive blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(2.0)
        glColor4f(0.0, 1.0,0.0, 0.6)
        for part_hits in part_intersections:
            for j in range(len(part_hits) - 1):
                seg = self._interpolate_on_surface(
                    part_hits[j], part_hits[j + 1], proj_type, ProjectionType)
                if len(seg) >= 2:
                    glBegin(GL_LINE_STRIP)
                    for sx, sy, sz in seg:
                        glVertex3f(sx, sy, sz)
                    glEnd()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_TEXTURE_2D)


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
                self.posx += self.x - self.lastx
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

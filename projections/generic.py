import wx


class GenericProjection():
    def __init__(self):
        self.projection_type = None

    def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
        return (x, y)

    # draws a frame of the map
    def draw_frame(self, projection_panel, dc):
        pass
        dc.SetPen(wx.Pen("black", 2))
        projection_panel.draw_parallel(-180, False, dc)
        projection_panel.draw_parallel(180, False, dc)

        if self.projection_type == self.ProjectionType.Cylindric:
            projection_panel.draw_meridian(-90, False, dc)
            projection_panel.draw_meridian(90, False, dc)

    class ProjectionType:
        (Cylindric, PseudoCylindric, Conic, Azimuthal) = range(4)

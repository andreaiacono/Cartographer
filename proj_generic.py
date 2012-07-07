import wx
class GenericProjection():

    def __init__(self):
        self.projection_type = None

    def get_coords(self, x, centerx, y, centery, original_x, original_y, width, height):
        return (x, y)
    
    #    draws a frame of the map 
    def draw_frame(self, width, height, projection_panel, dc):
        
        dc.SetPen(wx.Pen("black", 1))
        
        if self.projection_type == self.ProjectionType.Cylindric:
            
            # TODO: draw polyline?
            dc.DrawLine(projection_panel.tx - projection_panel.mf * 180 , projection_panel.ty - projection_panel.mf * 90 + 10, projection_panel.tx + projection_panel.mf * 180, projection_panel.ty - projection_panel.mf * 90 + 10)
            dc.DrawLine(projection_panel.tx + projection_panel.mf * 180 , projection_panel.ty - projection_panel.mf * 90 + 10, projection_panel.tx + projection_panel.mf * 180, projection_panel.ty + projection_panel.mf * 90 - 10)
            dc.DrawLine(projection_panel.tx + projection_panel.mf * 180 , projection_panel.ty + projection_panel.mf * 90 - 10, projection_panel.tx - projection_panel.mf * 180, projection_panel.ty + projection_panel.mf * 90 - 10)
            dc.DrawLine(projection_panel.tx - projection_panel.mf * 180 , projection_panel.ty + projection_panel.mf * 90 - 10, projection_panel.tx - projection_panel.mf * 180, projection_panel.ty - projection_panel.mf * 90 + 10)
        
        elif self.projection_type == self.ProjectionType.PseudoCylindric:
            
            self.draw_parallel(-90, width, height, False, dc)
            self.draw_parallel(90, width, height, False, dc)
            self.draw_meridian(-180, width, height, False, dc)
            self.draw_meridian(180, width, height, False, dc)
        

    class ProjectionType:
            (Cylindric, PseudoCylindric, Conic, Azimuthal) = range(4)

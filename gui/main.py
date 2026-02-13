import wx
import sys
import os
import math

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get project root directory for absolute paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import earth_canvas_params
from gui.projections_configs import dynamic_config
import earth_canvas
import projection_panel
from projections import (mercator, equal_area, miller, sinusoidal, eckertIV,
                        collignon, mollweide, lambert, albers, orthographic,
                        equidistant, stereographic, gnomonic, aitoff, weichel)
import lib.shapefile
import options_window

class CartographerFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Cartographer", size=wx.Size(1000, 600))

        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        # Initialize attributes needed by other components
        self.rotationx = 0
        self.rotationy = 0
        self.rotationz = 0
        self.shape = lib.shapefile.Reader(os.path.join(PROJECT_ROOT, "shapes/ne_50m_coastline/ne_50m_coastline.shp")).shapes()

        # Menu tracking
        self.id_shapes = {}
        self.current_shape_id = None
        self.shape_menu = None
        self.projection_menus = {}
        self.current_projection_id = None
        self.options = None  # Options window

        # Store reference to left splitter for swapping config panels
        self.left_splitter = None

        # Define zones for "Center on" menu
        self.zones = {
            "Europe": (20, -5, 35),
            "North America": (-90, -45, 0),
            "South America": (243, 170, 147),
            "Africa": (10, 0, 0),
            "Asia": (85, 41, 0),
            "Oceania": (130, 0, 330),
            "Antarctica": (120, 0, 280)
        }
        self.id_zones = {}

        # Create a dummy projection_panel attribute for params panel to reference
        class DummyProjection:
            class ProjectionType:
                Cylindrical = 1
                PseudoCylindrical = 2
                Conic = 3
                Azimuthal = 4

            def __init__(self):
                self.projection_type = self.ProjectionType.Cylindrical

        class DummyProjectionPanel:
            def __init__(self):
                self.resolution = 1
                self.projection = DummyProjection()
            def set_resolution(self, value):
                self.resolution = value
            def compute_size(self):
                pass
            def OnDraw(self):
                pass
            def Refresh(self):
                pass

        self.projection_panel_dummy = DummyProjectionPanel()

        # Create main vertical splitter (left column | right column)
        main_splitter = wx.SplitterWindow(self)

        # LEFT COLUMN: Create splitter for projection + params
        left_splitter = wx.SplitterWindow(main_splitter)
        self.left_splitter = left_splitter  # Store reference for config panel swapping

        # Create projection panel container (top of left column)
        projection_container = wx.Panel(left_splitter)
        projection_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create projection panel inside the container
        self.projection_panel = projection_panel.ProjectionPanel(projection_container, -1, self)
        self.projection_panel.projection = mercator.MercatorProjection()  # Add Mercator projection
        self.projection_panel.setShape(self.shape)  # Load shapes
        projection_sizer.Add(self.projection_panel, 1, wx.EXPAND)

        projection_container.SetSizer(projection_sizer)

        # Define projections (name and projection object only, no config panels)
        self.projections = {
            "&Cylindrical": {
                wx.Window.NewControlId(): ("&Equal Area (Balthasart, Behrmann, Gall, Lambert, Peters, Trystan Edwards)",
                                          equal_area.EqualAreaProjection()),
                wx.Window.NewControlId(): ("&Mercator",
                                          mercator.MercatorProjection()),
                wx.Window.NewControlId(): ("&Miller",
                                          miller.MillerProjection())
            },
            "&Pseudo Cylindrical": {
                wx.Window.NewControlId(): ("&Sinusoidal",
                                          sinusoidal.SinusoidalProjection()),
                wx.Window.NewControlId(): ("&Eckert IV",
                                          eckertIV.EckertIVProjection()),
                wx.Window.NewControlId(): ("&Collignon",
                                          collignon.CollignonProjection()),
                wx.Window.NewControlId(): ("M&ollweide",
                                          mollweide.MollweideProjection())
            },
            "C&onic": {
                wx.Window.NewControlId(): ("&Lambert",
                                          lambert.LambertProjection()),
                wx.Window.NewControlId(): ("&Albers",
                                          albers.AlbersProjection())
            },
            "&Azimuthal": {
                wx.Window.NewControlId(): ("&Orthographic",
                                          orthographic.AzimuthalOrthographicProjection()),
                wx.Window.NewControlId(): ("&Equidistant",
                                          equidistant.AzimuthalEquidistantProjection()),
                wx.Window.NewControlId(): ("&Stereographic",
                                          stereographic.StereographicProjection()),
                wx.Window.NewControlId(): ("&Gnomonic",
                                          gnomonic.GnomonicProjection()),
                wx.Window.NewControlId(): ("&Aitoff",
                                          aitoff.AitoffProjection()),
                wx.Window.NewControlId(): ("&Weichel",
                                          weichel.WeichelProjection())
            }
        }

        # Create menu bar (after projections are defined)
        self.SetMenuBar(self.create_menu_bar())

        # Create params panel (bottom of left column)
        self.params_panel = dynamic_config.DynamicParamsPanel(left_splitter, self)
        # Initialize with default Mercator projection
        self.params_panel.set_projection(mercator.MercatorProjection())

        # Split left column into projection (top) and params (bottom)
        left_splitter.SplitHorizontally(projection_container, self.params_panel)
        left_splitter.SetSashGravity(1.0)  # Keep params panel at minimum size
        left_splitter.SetMinimumPaneSize(120)
        # Set initial sash position to keep params at minimum
        wx.CallAfter(lambda: left_splitter.SetSashPosition(-150))

        # RIGHT COLUMN: Create splitter for earth + sliders
        right_splitter = wx.SplitterWindow(main_splitter)

        # Create earth panel container (top of right column)
        earth_panel_container = wx.Panel(right_splitter)
        earth_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create earth canvas inside the container
        self.earth_canvas = earth_canvas.EarthCanvas(earth_panel_container, self)
        self.earth_canvas.opengl_shapes = self.shape
        earth_sizer.Add(self.earth_canvas, 1, wx.EXPAND)

        earth_panel_container.SetSizer(earth_sizer)

        # Create earth canvas params panel (bottom of right column)
        self.sliders_panel = earth_canvas_params.EarthCanvasParams(right_splitter, self)

        # Split right column into earth (top) and sliders (bottom)
        right_splitter.SplitHorizontally(earth_panel_container, self.sliders_panel)
        right_splitter.SetSashGravity(1.0)  # Keep sliders panel at minimum size
        right_splitter.SetMinimumPaneSize(120)
        # Set initial sash position to keep sliders at minimum
        wx.CallAfter(lambda: right_splitter.SetSashPosition(-150))

        # Split main window into left column and right column
        main_splitter.SplitVertically(left_splitter, right_splitter)
        main_splitter.SetSashGravity(0.5)

        # Add main splitter to frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(main_splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def create_menu_bar(self):
        """Create the menu bar with all menus"""
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        export_id = wx.Window.NewControlId()
        file_menu.Append(export_id, "&Export projection as Image", "Export the actual projection as an image")
        self.Bind(wx.EVT_MENU, self.OnExport, id=export_id)
        file_menu.AppendSeparator()
        quit_id = wx.Window.NewControlId()
        file_menu.Append(quit_id, "&Quit", "Quit Cartographer")
        self.Bind(wx.EVT_MENU, self.OnQuit, id=quit_id)
        menu_bar.Append(file_menu, "&File")

        # Projections menu with cylindrical submenu
        menu_projections = wx.Menu()
        for projection_type in self.projections:
            submenu = wx.Menu()
            name = str(projection_type) + " Projections"
            menu_projections.AppendSubMenu(submenu, name)

            for projection_id in self.projections[projection_type]:
                proj_name = self.projections[projection_type][projection_id][0]
                submenu.AppendCheckItem(projection_id, proj_name, "Sets the " + proj_name + " projection")
                self.projection_menus[projection_id] = submenu  # Store menu reference
                self.Bind(wx.EVT_MENU, self.OnProjectionChange, id=projection_id)
                # Set checkmark for default Mercator projection
                if "&Mercator" in proj_name:
                    submenu.Check(projection_id, True)
                    self.current_projection_id = projection_id
        menu_bar.Append(menu_projections, "&Projections")

        # Center on menu
        menu_center = wx.Menu()
        for zone_name, coords in self.zones.items():
            zone_id = wx.Window.NewControlId()
            self.id_zones[zone_id] = (zone_name, coords)
            menu_center.Append(zone_id, zone_name, zone_name)
            self.Bind(wx.EVT_MENU, self.OnCenter, id=zone_id)
        menu_bar.Append(menu_center, "&Center on")

        # Maps menu (resolution selection)
        menu_shapes = wx.Menu()
        self.shape_menu = menu_shapes
        shape_mapping = {
            "Low Resolution (1/110M scale)": "110m_land",
            "Mid Resolution (1/50M scale)": "ne_50m_coastline",
            "High Resolution (1/10M scale)": "10m_land",
            "Countries (1/50M scale)": "ne_50m_admin_0_countries"
        }
        default_shape_id = None
        for friendly_name, shapefile_name in shape_mapping.items():
            shape_id = wx.Window.NewControlId()
            self.id_shapes[shape_id] = shapefile_name
            menu_shapes.AppendCheckItem(shape_id, friendly_name)
            self.Bind(wx.EVT_MENU, self.OnSetShape, id=shape_id)
            # Set Mid Res (ne_50m_coastline) as default
            if shapefile_name == "ne_50m_coastline":
                default_shape_id = shape_id

        if default_shape_id is not None:
            menu_shapes.Check(default_shape_id, True)
            self.current_shape_id = default_shape_id

        menu_bar.Append(menu_shapes, "&Maps")

        # Tools menu
        menu_tools = wx.Menu()
        options_id = wx.Window.NewControlId()
        menu_tools.Append(options_id, "&Options", "Shows the options window")
        self.Bind(wx.EVT_MENU, self.OnOptions, id=options_id)
        menu_bar.Append(menu_tools, "&Tools")

        # About menu
        menu_about = wx.Menu()
        info_id = wx.Window.NewControlId()
        menu_about.Append(info_id, "&Info", "Shows info")
        self.Bind(wx.EVT_MENU, self.OnInfo, id=info_id)
        menu_bar.Append(menu_about, "&About")

        return menu_bar

    def OnSetShape(self, event):
        """Handle shape/resolution menu selection"""
        self.setShape(event.GetId())

    def setShape(self, shape_id):
        """Load a new shapefile and update both panels"""
        shape_name = self.id_shapes[shape_id]
        self.shape = lib.shapefile.Reader(os.path.join(PROJECT_ROOT, "shapes", shape_name, shape_name + ".shp")).shapes()

        # Update both 2D projection panel and 3D OpenGL panel with the same shapes
        self.projection_panel.setShape(self.shape)
        self.earth_canvas.opengl_shapes = self.shape

        # Update menu checkmarks
        if self.current_shape_id is not None:
            self.shape_menu.Check(self.current_shape_id, False)
        self.shape_menu.Check(shape_id, True)
        self.current_shape_id = shape_id

        # Refresh both panels
        self.projection_panel.Refresh()
        self.earth_canvas.Refresh()

    def OnProjectionChange(self, event):
        """Handle projection menu selection"""
        projection_id = event.GetId()

        # Find the projection in the dictionary
        for projection_type in self.projections:
            if projection_id in self.projections[projection_type]:
                (name, proj_object) = self.projections[projection_type][projection_id]

                # Update the projection
                self.projection_panel.projection = proj_object

                # Update params panel to show appropriate controls
                self.params_panel.set_projection(proj_object)

                # Update window title
                self.SetTitle("Cartographer - " + name.replace('&', '') + " projection")

                # Update projection checkmarks
                if self.current_projection_id is not None and self.current_projection_id in self.projection_menus:
                    old_menu = self.projection_menus[self.current_projection_id]
                    old_menu.Check(self.current_projection_id, False)
                if projection_id in self.projection_menus:
                    current_menu = self.projection_menus[projection_id]
                    current_menu.Check(projection_id, True)
                    self.current_projection_id = projection_id

                # Refresh display
                self.projection_panel.Refresh()
                self.earth_canvas.Refresh()  # Also refresh 3D earth panel
                break

    def OnCenter(self, event):
        """Center the view on a specific zone"""
        zone_name, (x, y, z) = self.id_zones[event.GetId()]
        self.rotationx = x
        self.rotationy = y
        self.rotationz = z
        # Update projection panel
        self.projection_panel.rotationx = x
        self.projection_panel.rotationy = y
        self.projection_panel.rotationz = z
        # Update earth canvas
        self.earth_canvas.set_earth_coordinates(x, y, z)
        # Refresh both
        self.projection_panel.Refresh()
        self.earth_canvas.Refresh()

    def OnExport(self, event):
        """Export projection as image"""
        # Ask user for filename
        wildcard = "PNG files (*.png)|*.png|JPEG files (*.jpg)|*.jpg"
        dlg = wx.FileDialog(self, "Export projection", wildcard=wildcard,
                           defaultFile="projection.png",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()

            # Add extension if not present
            if not filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath += '.png'

            # Save the current projection panel's content
            # Get the projection panel's current size
            panel_width, panel_height = self.projection_panel.GetSize()

            # Create a bitmap and draw the projection
            bmp = wx.Bitmap(panel_width, panel_height)
            dc = wx.MemoryDC(bmp)

            # Draw the projection (trigger the same OnPaint logic)
            self.projection_panel._cache_rotation_matrix()
            dc.SetBackground(wx.Brush("white"))
            dc.Clear()

            # Draw grid if enabled
            if self.projection_panel.paint_grid or self.projection_panel.paint_grid_specials:
                self.projection_panel.draw_grid(dc)

            # Draw shapes
            if self.projection_panel.shapes and self.projection_panel.projection:
                self.projection_panel.projection.set_central_point(
                    self.projection_panel.rotationx,
                    self.projection_panel.rotationy
                )
                # Use the same drawing code from test_projection_panel
                dc.SetPen(wx.Pen(self.projection_panel.shapes_color, 1))
                width_third = panel_width / 3
                height_third = panel_height / 3

                for shape in self.projection_panel.shapes:
                    points = shape.points
                    if len(points) < 2:
                        continue

                    step = max(1, int(self.projection_panel.resolution))
                    lines = []
                    current_line = []
                    prev_x = None
                    prev_y = None

                    for i in range(0, len(points), step):
                        lon, lat = points[i]
                        try:
                            lon_rad = math.radians(-lon)
                            lat_rad = math.radians(lat)
                            cos_lat = math.cos(lat_rad)
                            sx = cos_lat * math.cos(lon_rad)
                            sy = cos_lat * math.sin(lon_rad)
                            sz = math.sin(lat_rad)

                            px = self.projection_panel._rot_a * sx + self.projection_panel._rot_b * sy + self.projection_panel._rot_c * sz
                            py = self.projection_panel._rot_d * sx + self.projection_panel._rot_e * sy + self.projection_panel._rot_f * sz
                            pz = self.projection_panel._rot_g * sx + self.projection_panel._rot_h * sy + self.projection_panel._rot_i * sz

                            lat_eff = math.asin(math.radians(pz))
                            lon_eff = math.atan2(math.radians(py), math.radians(px))
                            proj_x, proj_y = self.projection_panel.projection.get_coords(-lon_eff, -lat_eff * 90)

                            x = int(proj_x * self.projection_panel.mf + self.projection_panel.tx)
                            y = int(proj_y * self.projection_panel.mf + self.projection_panel.ty)

                            if prev_x is not None:
                                dx = x - prev_x
                                dy = y - prev_y
                                if abs(dx) < width_third and abs(dy) < height_third:
                                    current_line.append((x, y))
                                else:
                                    if len(current_line) > 1:
                                        lines.append(current_line)
                                    current_line = [(x, y)]
                            else:
                                current_line.append((x, y))

                            prev_x = x
                            prev_y = y
                        except:
                            if len(current_line) > 1:
                                lines.append(current_line)
                            current_line = []
                            prev_x = None
                            prev_y = None

                    if len(current_line) > 1:
                        lines.append(current_line)

                    for line in lines:
                        if len(line) > 1:
                            dc.DrawLines(line)

            # Save the bitmap
            dc.SelectObject(wx.NullBitmap)
            bmp.SaveFile(filepath, wx.BITMAP_TYPE_PNG)
            wx.MessageBox(f"Projection exported to {filepath}", "Export Complete", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def OnOptions(self, event):
        """Show options window"""
        if self.options is None or not self.options.IsShown():
            self.options = options_window.Options(None, self)
            self.options.Show(True)
        else:
            self.options.Raise()  # Bring to front if already open

    def OnInfo(self, event):
        """Show about/info dialog"""
        licence_text = """Cartographer is free software; you can redistribute
it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Cartographer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details."""

        info_text = """Cartographer - Map Projection Visualization Tool

A tool for exploring and visualizing different map projections.

License:
""" + licence_text

        wx.MessageBox(info_text, "About Cartographer", wx.OK | wx.ICON_INFORMATION)

    def OnQuit(self, event):
        if self.options:
            self.options.Destroy()
        self.Destroy()

    def getShape(self):
        return self.shape

    def set_earth_coordinates(self, x, y, z):
        self.rotationx = x
        self.rotationy = y
        self.rotationz = z


class CartographerApplication(wx.App):
    def OnInit(self):
        frame = CartographerFrame()
        frame.Show(True)
        self.SetTopWindow(frame)

        # Force initial refresh of earth canvas after window is shown
        wx.CallAfter(frame.earth_canvas.Refresh)

        return True


if __name__ == '__main__':
    app = CartographerApplication(redirect=False)
    app.MainLoop()

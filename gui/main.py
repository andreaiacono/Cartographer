import wxversion

wxversion.select('3.0')
import wx

from gui import projection_panel, earth_canvas, options_window

from os import listdir
from projections import aitoff
from projections import albers
from projections import equidistant
from projections import orthographic
from projections import collignon
from projections import eckertIV
from projections_configs import empty_config, equal_area_config, albers_config, \
    lambert_config
from projections import equal_area
from projections import lambert
from projections import mercator
from projections import miller
from projections import mollweide
from projections import sinusoidal
from projections import stereographic
from projections import weichel

import lib.euclid
import lib.shapefile

ROTATION_STEP = 3

ZONES = {
    wx.NewId(): ("Europe", (20, -5, 35)),
    wx.NewId(): ("North America", (-90, -45, 0)),
    wx.NewId(): ("South America", (243, 170, 147)),
    wx.NewId(): ("Africa", (10, 0, 0)),
    wx.NewId(): ("Asia", (85, 41, 0)),
    wx.NewId(): ("Oceania", (130, 0, 330)),
    wx.NewId(): ("Antarctica", (120, 0, 280))
}

class CartographerFrame(wx.Frame):
    def __init__(self):
        self.shape = ""
        self.id_shapes = {}
        self.rotationx = 0
        self.rotationy = 0
        self.rotationz = 0

        wx.Frame.__init__(self, parent=None, id=-1, title="Cartographer - Mercator projection", pos=wx.DefaultPosition, size=wx.Size(1000, 600))
        wx.EVT_CLOSE(self, self.OnQuit)
        wx.EVT_KEY_DOWN(self, self.OnKeyDown)

        self.CreateStatusBar()

        top_splitter = wx.SplitterWindow(self, style=wx.SP_BORDER)
        self.settings_splitter = wx.SplitterWindow(top_splitter)

        self.projection_panel = projection_panel.ProjectionPanel(top_splitter, -1, self)
        self.projection_panel.projection = mercator.MercatorProjection()
        top_splitter.SplitVertically(self.projection_panel, self.settings_splitter)
        top_splitter.SetSashGravity(0.72)

        self.earth_canvas = earth_canvas.EarthCanvas(self.settings_splitter, self)
        self.configuration_panel = empty_config.EmptyPanel(self.settings_splitter)
        self.settings_splitter.SplitHorizontally(self.earth_canvas, self.configuration_panel)
        self.settings_splitter.SetSashGravity(0.5)

        wx.EVT_KEY_DOWN(self.configuration_panel, self.OnKeyDown)
        wx.EVT_KEY_DOWN(self.earth_canvas, self.OnKeyDown)
        wx.EVT_KEY_DOWN(self.projection_panel, self.OnKeyDown)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.options = None

        self.projections = {
            "&Cylindrical": {
                wx.NewId(): ("&Equal Area (Balthasart, Behrmann, Gall, Lambert, Peters, Trystan Edwards)",
                             equal_area.EqualAreaProjection(),
                             equal_area_config.ConfigurationPanel(self.settings_splitter, -1, self)),
                wx.NewId(): ("&Mercator", mercator.MercatorProjection(), empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): ("&Miller", miller.MillerProjection(), empty_config.EmptyPanel(self.settings_splitter))
            },
            "&Pseudo Cylindrical": {
                wx.NewId(): (
                "&Sinusoidal", sinusoidal.SinusoidalProjection(), empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): ("&Eckert IV", eckertIV.EckertIVProjection(), empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): (
                "&Collignon", collignon.CollignonProjection(), empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): (
                "M&ollweide", mollweide.MollweideProjection(), empty_config.EmptyPanel(self.settings_splitter)),
            },
            "C&onic": {
                wx.NewId(): ("&Lambert", lambert.LambertProjection(),
                             lambert_config.ConfigurationPanel(self.settings_splitter, -1, self)),
                wx.NewId(): ("&Albers", albers.AlbersProjection(),
                             albers_config.ConfigurationPanel(self.settings_splitter, -1, self)),
            },
            "&Azimuthal": {
                wx.NewId(): ("&Orthographic", orthographic.AzimuthalOrthographicProjection(),
                             empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): ("&Equidistant", equidistant.AzimuthalEquidistantProjection(),
                             empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): ("&Stereographic", stereographic.StereographicProjection(),
                             empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): ("&Aitoff", aitoff.AitoffProjection(), empty_config.EmptyPanel(self.settings_splitter)),
                wx.NewId(): ("&Weichel", weichel.WeichelProjection(), empty_config.EmptyPanel(self.settings_splitter)),
            }
        }

        self.SetMenuBar(self.create_menu_bar())
        self.SetStatusText("Ready")

    def create_menu_bar(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()

        ## file menu
        export_id = wx.NewId()
        file_menu.Append(export_id, "&Export projection as Image", "Export the actual projection as an image")
        wx.EVT_MENU(self, export_id, self.OnExport)

        file_menu.AppendSeparator()

        quit_id = wx.NewId()
        file_menu.Append(quit_id, "&Quit", "Quit Cartographer")
        wx.EVT_MENU(self, quit_id, self.OnQuit)

        menu_bar.Append(file_menu, "&File")

        ## projections menu
        menu_projections = wx.Menu()
        for projection_type in self.projections:
            menu = wx.Menu()
            menu_projections.AppendMenu(wx.ID_ANY, projection_type + " Projections", menu)
            for projection_id in self.projections[projection_type]:
                name = self.projections[projection_type][projection_id][0]
                self.add_projection(menu, projection_id, name, "Sets the " + name + " projection", self.set_projection)
        menu_bar.Append(menu_projections, "&Projections")

        ## center menu
        menu_views = wx.Menu()
        for zone_id in ZONES:
            self.add_center(menu_views, zone_id, ZONES[zone_id])
        menu_bar.Append(menu_views, "&Center")

        ## shapes menu
        menu_shapes = wx.Menu()
        for shape in self.read_shapes():
            shape_id = wx.NewId()
            self.id_shapes[shape_id] = shape
            menu_shapes.Append(shape_id, shape)
            wx.EVT_MENU(self, shape_id, self.OnSetShape)

        self.setShape(shape_id)
        menu_bar.Append(menu_shapes, "&Shapes")

        ## tools menu
        menu_tools = wx.Menu()
        options_id = wx.NewId()
        menu_tools.Append(options_id, "&Option", "Shows the options window")
        wx.EVT_MENU(self, options_id, self.OnOptions)
        menu_bar.Append(menu_tools, "&Tools")

        ## about menu
        menu_about = wx.Menu()
        info_id = wx.NewId()
        menu_about.Append(info_id, "&Info", "Shows info")
        wx.EVT_MENU(self, info_id, self.OnInfo)
        menu_bar.Append(menu_about, "&About")

        return menu_bar

    def add_projection(self, menu, id, name, description, function):
        menu.Append(id, name, description)
        wx.EVT_MENU(self, id, function)

    def add_center(self, menu, id, zone):
        name = zone[0]
        menu.Append(id, "Center map on " + name, "Centers the map on " + name)
        wx.EVT_MENU(self, id, self.Center)

    def Center(self, event):
        (x, y, z) = ZONES[event.GetId()][1]
        self.rotationx = x
        self.rotationy = y
        self.rotationz = z
        self.refresh()

    def OnOptions(self, event):
        self.options = options_window.Options(None, self)
        self.options.Show(True)

    def OnQuit(self, event):
        if self.options:
            self.options.Destroy()
        self.Destroy()

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_LEFT or key == wx.WXK_NUMPAD_LEFT:
            self.rotationx -= ROTATION_STEP
            self.projection_panel.rotationx = self.rotationx
            self.projection_panel.Refresh()
        elif key == wx.WXK_RIGHT or key == wx.WXK_NUMPAD_RIGHT:
            self.rotationx += ROTATION_STEP
            self.projection_panel.rotationx = self.rotationx
            self.projection_panel.Refresh()
        elif key == wx.WXK_UP or key == wx.WXK_NUMPAD_UP:
            self.rotationy -= ROTATION_STEP
            self.projection_panel.rotationy = self.rotationy
            self.projection_panel.Refresh()
        elif key == wx.WXK_DOWN or key == wx.WXK_NUMPAD_DOWN:
            self.rotationy += ROTATION_STEP
            self.projection_panel.rotationy = self.rotationy
            self.projection_panel.Refresh()
        elif key == wx.WXK_PAGEUP or key == wx.WXK_NUMPAD_PAGEUP:
            self.rotationz -= ROTATION_STEP
            self.projection_panel.rotationz = self.rotationz
            self.projection_panel.Refresh()
        elif key == wx.WXK_PAGEDOWN or key == wx.WXK_NUMPAD_PAGEDOWN:
            self.rotationz += ROTATION_STEP
            self.projection_panel.rotationz = self.rotationz
            self.projection_panel.Refresh()

    def OnSetShape(self, event):
        self.setShape(event.GetId())

    def setShape(self, shape):
        shape_name = self.id_shapes[shape]
        self.shape = lib.shapefile.Reader("shapes/" + shape_name + "/" + shape_name + ".shp").shapes()
        self.projection_panel.setShape(self.shape)
        self.refresh()

    def getShape(self):
        return self.shape

    def refresh(self):
        self.projection_panel.set_coordinates(self.rotationx, self.rotationy, self.rotationz)
        self.earth_canvas.set_earth_coordinates(self.rotationx, self.rotationy, self.rotationz)

        self.projection_panel.Refresh()
        self.earth_canvas.Refresh()

    def set_projection(self, event):
        for projection_type in self.projections:
            if event.GetId() in self.projections[projection_type]:
                (name, proj_function, config_function) = self.projections[projection_type].get(event.GetId())
                self.replace_projection(name, proj_function, config_function)
                break

    def replace_projection(self, name, new_projection, new_configuration):
        self.projection_panel.projection = new_projection
        old_conf = self.settings_splitter.GetWindow2()
        old_conf.Hide()
        new_configuration.Show()
        self.settings_splitter.ReplaceWindow(old_conf, new_configuration)
        self.SetTitle("Cartographer - " + name.replace('&', '') + " projection")
        self.refresh()

    def OnExport(self, event):
        dlg = wx.FileDialog(self, "Choose a file name to save the image as a PNG to", defaultDir="", defaultFile="",
                            wildcard="*.png", style=wx.SAVE)
        if dlg.ShowModal() != wx.ID_OK:
            return
        height = 2000
        width = 4000
        mem = wx.MemoryDC()
        image = wx.EmptyBitmap(width, height)
        mem.SelectObject(image)
        mem.BeginDrawing()

        proj_panel = projection_panel.ProjectionPanel(self, -1, self)
        proj_panel.projection = self.projection_panel.projection
        proj_panel.resolution = 1
        proj_panel.grid_resolution = 1
        proj_panel.set_paint_grid(self.projection_panel.paint_grid)
        proj_panel.set_paint_grid_specials(self.projection_panel.paint_grid_specials)
        proj_panel.rotationx = self.projection_panel.rotationx
        proj_panel.rotationy = self.projection_panel.rotationy
        proj_panel.rotationz = self.projection_panel.rotationz
        proj_panel.width = width
        proj_panel.height = height
        proj_panel.mf = height / float(180)
        proj_panel.tx = proj_panel.mf * 180 + (width - proj_panel.mf * 360) / 2
        proj_panel.ty = proj_panel.mf * 90
        proj_panel.draw_projection(mem, width, height)

        mem.Blit(0, 0, 2000, 1000, wx.PaintDC(proj_panel), 0, 0)
        mem.EndDrawing()

        image.SaveFile(dlg.GetPath(), wx.BITMAP_TYPE_PNG)
        proj_panel.Destroy()

    def read_shapes(self):
        shapes_dirs = [f for f in listdir("shapes")]
        return shapes_dirs

    def OnInfo(self, event):

        licence = """Cartographer is free software; you can redistribute
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

Cartographer is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  

See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""

        author = "Andrea Iacono (andrea.iacono.nl@gmail.com)"
        credits = author + "\n\nThe sources of this project are available at:\nhttp://www.github.com/andreaiacono/cartographer"

        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon('img/mercator.jpg', wx.BITMAP_TYPE_JPEG))
        info.SetName('Cartographer')
        info.SetVersion('0.8')
        info.SetDescription("Cartographer is a simple cartography application for making earth maps in real-time")
        info.SetCopyright('(C) 2012-2016 Andrea Iacono')
        info.SetWebSite('http://www.github.com/andreaiacono/cartographer')
        info.SetLicence(licence)
        info.AddDeveloper(credits)
        info.AddDocWriter(author)

        wx.AboutBox(info)


class CartographerApplication(wx.App):
    def OnInit(self):
        frame = CartographerFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        # self.SetSize(800, 600)
        return True


app = CartographerApplication()
app.MainLoop()

import wxversion

wxversion.select('3.0')
import wx

from main import panel_projection, panel_earth, options_window

from os import listdir
from projections import proj_aitoff
from projections import proj_albers
from projections import proj_albers_configuration
from projections import proj_azimuthal_equidistant
from projections import proj_azimuthal_orthographic
from projections import proj_collignon
from projections import proj_eckertIV
from projections import proj_empty_configuration
from projections import proj_equal_area
from projections import proj_equal_area_configuration
from projections import proj_lambert
from projections import proj_lambert_configuration
from projections import proj_mercator
from projections import proj_miller
from projections import proj_mollweide
from projections import proj_sinusoidal
from projections import proj_stereographic
from projections import proj_weichel

import lib.euclid
import lib.shapefile

ZONES = {
    wx.NewId(): ("Europe", (20, -5, 35)),
    wx.NewId(): ("North America", (-90, -45, 0)),
    wx.NewId(): ("South America", (243, 170, 147)),
    wx.NewId(): ("Africa", (20, 0, 0)),
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

        wx.Frame.__init__(self, parent=None, id=-1, title="Cartographer", pos=wx.DefaultPosition, size=wx.Size(800, 600))
        wx.EVT_CLOSE(self, self.OnQuit)
        wx.EVT_KEY_DOWN(self, self.OnKeyDown)

        self.CreateStatusBar()

        top_splitter = wx.SplitterWindow(self, style=wx.SP_BORDER)
        self.settings_splitter = wx.SplitterWindow(top_splitter)

        self.projection_panel = panel_projection.ProjectionPanel(top_splitter, -1, self)
        self.projection_panel.projection = proj_mercator.MercatorProjection()
        top_splitter.SplitVertically(self.projection_panel, self.settings_splitter)
        top_splitter.SetSashGravity(0.65)

        self.configurationPanel = proj_empty_configuration.EmptyPanel(self.settings_splitter, "Mercator")
        self.earth_canvas = panel_earth.EarthCanvas(self.settings_splitter, self)
        self.settings_splitter.SplitHorizontally(self.earth_canvas, self.configurationPanel)
        self.settings_splitter.SetSashGravity(0.5)

        wx.EVT_KEY_DOWN(self.configurationPanel, self.OnKeyDown)
        wx.EVT_KEY_DOWN(self.earth_canvas, self.OnKeyDown)
        wx.EVT_KEY_DOWN(self.projection_panel, self.OnKeyDown)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.options = None

        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()


        ## file menu
        ID_EXPORT = wx.NewId()
        file_menu.Append(ID_EXPORT, "&Export projection as Image", "Export the actual projection as an image")
        wx.EVT_MENU(self, ID_EXPORT, self.OnExport)

        file_menu.AppendSeparator()

        ID_QUIT = wx.NewId()
        file_menu.Append(ID_QUIT, "&Quit", "Quit Cartographer")
        wx.EVT_MENU(self, ID_QUIT, self.OnQuit)

        menu_bar.Append(file_menu, "&File")

        ## projections menu
        menu_proj = wx.Menu()
        menu_cylindrical = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "&Cylindrical Projections", menu_cylindrical)
        self.add_projection(menu_cylindrical, "&Mercator", "Shows a Mercator projection", self.SetMercatorProjection)
        self.add_projection(menu_cylindrical,
                            "&Equal Area (Balthasart, Behrmann, Gall, Lambert, Peters, Trystan Edwards)",
                            "Shows an equal area projection (Balthasart, Behrmann, Gall, Lambert, Peters, Trystan Edwards)",
                            self.SetEqualAreaProjection)
        self.add_projection(menu_cylindrical, "M&iller", "Shows a Miller projection", self.SetMillerProjection)

        menu_pseudocylindrical = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "P&seudo Cylindrical Projections", menu_pseudocylindrical)
        self.add_projection(menu_pseudocylindrical, "&Sinusoidal", "Shows a sinusoidal projection",
                            self.SetSinusoidalProjection)
        self.add_projection(menu_pseudocylindrical, "&Eckert IV", "Shows an Eckert IV projection",
                            self.SetEckertIVProjection)
        self.add_projection(menu_pseudocylindrical, "&Collignon", "Shows a Collignon projection",
                            self.SetCollignonProjection)
        self.add_projection(menu_pseudocylindrical, "M&ollweide", "Shows a Mollweide projection",
                            self.SetMollweideProjection)

        menu_conic = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "C&onic Projections", menu_conic)
        self.add_projection(menu_conic, "&Lambert", "Shows a Lambert projection", self.SetLambertProjection)
        self.add_projection(menu_conic, "&Albers", "Shows a Albers projection", self.SetAlbersProjection)

        menu_azimuthal = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "A&zimuthal Projections", menu_azimuthal)
        self.add_projection(menu_azimuthal, "&Orthographic", "Shows an orthographic azimuthal projection",
                            self.SetAzimuthalOrtographicProjection)
        self.add_projection(menu_azimuthal, "&Equidistant", "Shows an orthographic equidstant projection",
                            self.SetAzimuthalEquidistantProjection)
        self.add_projection(menu_azimuthal, "&Stereographic", "Shows a stereographic projection",
                            self.SetStereographicProjection)
        self.add_projection(menu_azimuthal, "&Aitoff Projection", "Shows a Aiteoff projection",
                            self.SetAitoffProjection)
        self.add_projection(menu_azimuthal, "&Weichel Projection", "Shows a Weichel projection",
                            self.SetWeichelProjection)

        menu_bar.Append(menu_proj, "&Projections")


        ## center menu
        menu_views = wx.Menu()
        for zone_id in ZONES:
            self.add_center(menu_views, zone_id, ZONES[zone_id])
        menu_bar.Append(menu_views, "&Center")


        ## shapes menu
        menu_shapes = wx.Menu()
        for shape in self.read_shapes():
            shapeId = wx.NewId()
            self.id_shapes[shapeId] = shape
            menu_shapes.Append(shapeId, shape)
            wx.EVT_MENU(self, shapeId, self.OnSetShape)

        self.setShape(shapeId)
        menu_bar.Append(menu_shapes, "&Shapes")


        ## tools menu
        menu_tools = wx.Menu()
        ID_OPTIONS = wx.NewId()
        menu_tools.Append(ID_OPTIONS, "&Option", "Shows the options window")
        wx.EVT_MENU(self, ID_OPTIONS, self.OnOptions)
        menu_bar.Append(menu_tools, "&Tools")


        ## about menu
        menu_about = wx.Menu()
        ID_INFO = wx.NewId()
        menu_about.Append(ID_INFO, "&Info", "Shows info")
        wx.EVT_MENU(self, ID_INFO, self.OnInfo)
        menu_bar.Append(menu_about, "&About")

        self.SetMenuBar(menu_bar)
        self.SetStatusText("Ready")

    def add_projection(self, menu, name, description, function):
        ID = wx.NewId()
        menu.Append(ID, name, description)
        wx.EVT_MENU(self, ID, function)

    def add_center(self, menu, ID, zone):
        name = zone[0]
        print("ID=" + str(ID) + " name=" + str(name))
        menu.Append(ID, "Center map on " + name, "Centers the map on " + name)
        wx.EVT_MENU(self, ID, self.Center)


    def Center(self, event):
        self.set_center(ZONES[event.GetId()][1])

    def set_center(self, coords):
        (x, y, z) = coords
        self.rotationx = x
        self.rotationy = y
        self.rotationz = z
        self.refresh()

    def OnOptions(self, event):
        self.options = options_window.Options(None, self)
        self.options.Show(True)

    def OnQuit(self, event):
        if self.options is not None:
            self.options.Destroy()
        self.Destroy()

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        # print key
        if key == wx.WXK_LEFT or key == wx.WXK_NUMPAD_LEFT:
            self.rotationx -= 5
            self.projection_panel.rotationx = self.rotationx
            self.projection_panel.Refresh()
        elif key == wx.WXK_RIGHT or key == wx.WXK_NUMPAD_RIGHT:
            self.rotationx += 5
            self.projection_panel.rotationx = self.rotationx
            self.projection_panel.Refresh()
        elif key == wx.WXK_UP or key == wx.WXK_NUMPAD_UP:
            self.rotationy -= 5
            self.projection_panel.rotationy = self.rotationy
            self.projection_panel.Refresh()
        elif key == wx.WXK_DOWN or key == wx.WXK_NUMPAD_DOWN:
            self.rotationy += 5
            self.projection_panel.rotationy = self.rotationy
            self.projection_panel.Refresh()
        elif key == wx.WXK_PAGEUP or key == wx.WXK_NUMPAD_PAGEUP:
            self.rotationz -= 5
            self.projection_panel.rotationz = self.rotationz
            self.projection_panel.Refresh()
        elif key == wx.WXK_PAGEDOWN or key == wx.WXK_NUMPAD_PAGEDOWN:
            self.rotationz += 5
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

    def SetMercatorProjection(self, event):
        name = "Mercator projection"
        self.replace_projection(name, proj_mercator.MercatorProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetEqualAreaProjection(self, event):
        name = "Equal Area projection"
        proj = proj_equal_area.EqualAreaProjection()
        self.replace_projection(name, proj,
                                proj_equal_area_configuration.ConfigurationPanel(self.settings_splitter, -1, self,
                                                                                 proj))

    def SetLambertProjection(self, event):
        name = "Lambert projection"
        proj = proj_lambert.LambertProjection()
        self.replace_projection(name, proj,
                                proj_lambert_configuration.ConfigurationPanel(self.settings_splitter, -1, self, proj))

    def SetAlbersProjection(self, event):
        name = "Albers projection"
        proj = proj_albers.AlbersProjection()
        self.replace_projection(name, proj,
                                proj_albers_configuration.ConfigurationPanel(self.settings_splitter, -1, self, proj))

    def SetAzimuthalOrtographicProjection(self, event):
        name = "Azimuthal ortographic projection"
        self.replace_projection(name, proj_azimuthal_orthographic.AzimuthalOrthographicProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetAzimuthalEquidistantProjection(self, event):
        name = "Azimuthal equidistant projection"
        self.replace_projection(name, proj_azimuthal_equidistant.AzimuthalEquidistantProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetStereographicProjection(self, event):
        name = "Stereographic projection"
        self.replace_projection(name, proj_stereographic.StereographicProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetSinusoidalProjection(self, event):
        name = "Sinusoidal projection"
        self.replace_projection(name, proj_sinusoidal.SinusoidalProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetEckertIVProjection(self, event):
        name = "Eckert IV Projection"
        self.replace_projection(name, proj_eckertIV.EckertIVProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetCollignonProjection(self, event):
        name = "Collignon projection"
        self.replace_projection(name, proj_collignon.CollignonProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetMillerProjection(self, event):
        name = "Miller projection"
        self.replace_projection(name, proj_miller.MillerProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetMollweideProjection(self, event):
        name = "Mollweide projection"
        self.replace_projection(name, proj_mollweide.MollweideProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetAitoffProjection(self, event):
        name = "Aitoff projection"
        self.replace_projection(name, proj_aitoff.AitoffProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def SetWeichelProjection(self, event):
        name = "Weichel projection"
        self.replace_projection(name, proj_weichel.WeichelProjection(),
                                proj_empty_configuration.EmptyPanel(self.settings_splitter, name))

    def replace_projection(self, name, new_projection, new_configuration):

        self.projection_panel.projection = new_projection
        old_conf = self.settings_splitter.GetWindow2()
        new_conf = new_configuration
        self.settings_splitter.ReplaceWindow(old_conf, new_conf)
        old_conf.Destroy()

        self.SetTitle("Cartographer - " + name)
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

        proj_panel = panel_projection.ProjectionPanel(self, -1, self)
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
        creds = author + "\n\nThe sources of this project are available at:\nhttp://www.github.com/andreaiacono/cartographer"

        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon('img/mercator.jpg', wx.BITMAP_TYPE_JPEG))
        info.SetName('Cartographer')
        info.SetVersion('0.8')
        info.SetDescription("Cartographer is a simple cartography application for making earth maps in real-time")
        info.SetCopyright('(C) 2012-2016 Andrea Iacono')
        info.SetWebSite('http://www.github.com/andreaiacono/cartographer')
        info.SetLicence(licence)
        info.AddDeveloper(creds)
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

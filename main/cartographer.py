import wxversion

wxversion.select('3.0')
import wx

from main import panel_projection, panel_earth, options_window

from os import listdir
from os.path import isfile, join
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


class CartographerFrame(wx.Frame):
    def __init__(self):
        self.shape = ""
        self.id_shapes = {}
        self.rotationx = 0
        self.rotationy = 0
        self.rotationz = 0

        wx.Frame.__init__(self, parent=None, id=-1, title="Cartographer", pos=wx.DefaultPosition,
                          size=wx.Size(800, 600))
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

        ID_EXPORT = wx.NewId()
        file_menu.Append(ID_EXPORT, "&Export projection as Image", "Export the actual projection as an image")
        wx.EVT_MENU(self, ID_EXPORT, self.OnExport)

        file_menu.AppendSeparator()

        ID_QUIT = wx.NewId()
        file_menu.Append(ID_QUIT, "&Quit", "Quit Cartographer")
        wx.EVT_MENU(self, ID_QUIT, self.OnQuit)

        menu_bar.Append(file_menu, "&File")

        menu_proj = wx.Menu()

        menu_cylindrical = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "&Cylindrical Projections", menu_cylindrical)

        ID_PROJ_MERCATOR = wx.NewId()
        menu_cylindrical.Append(ID_PROJ_MERCATOR, "&Mercator", "Shows a Mercator projection")
        wx.EVT_MENU(self, ID_PROJ_MERCATOR, self.SetMercatorProjection)

        ID_PROJ_EQUAL_AREA = wx.NewId()
        menu_cylindrical.Append(ID_PROJ_EQUAL_AREA,
                                "&Equal Area (Balthasart, Behrmann, Gall, Lambert, Peters, Trystan Edwards)",
                                "Shows an equal area projection (Balthasart, Behrmann, Gall, Lambert, Peters, Trystan Edwards)")
        wx.EVT_MENU(self, ID_PROJ_EQUAL_AREA, self.SetEqualAreaProjection)

        ID_PROJ_MILLER = wx.NewId()
        menu_cylindrical.Append(ID_PROJ_MILLER, "M&iller", "Shows a Miller projection")
        wx.EVT_MENU(self, ID_PROJ_MILLER, self.SetMillerProjection)

        menu_pseudocyl = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "P&seudo Cylindrical Projections", menu_pseudocyl)

        ID_PROJ_SINUSOIDAL = wx.NewId()
        menu_pseudocyl.Append(ID_PROJ_SINUSOIDAL, "&Sinusoidal", "Shows a sinusoidal projection")
        wx.EVT_MENU(self, ID_PROJ_SINUSOIDAL, self.SetSinusoidalProjection)

        ID_PROJ_ECKERTIV = wx.NewId()
        menu_pseudocyl.Append(ID_PROJ_ECKERTIV, "&Eckert IV", "Shows an Eckert IV projection")
        wx.EVT_MENU(self, ID_PROJ_ECKERTIV, self.SetEckertIVProjection)

        ID_PROJ_COLLIGNON = wx.NewId()
        menu_pseudocyl.Append(ID_PROJ_COLLIGNON, "&Collignon", "Shows a Collignon projection")
        wx.EVT_MENU(self, ID_PROJ_COLLIGNON, self.SetCollignonProjection)

        ID_PROJ_MOLLWEIDE = wx.NewId()
        menu_pseudocyl.Append(ID_PROJ_MOLLWEIDE, "M&ollweide", "Shows a Mollweide projection")
        wx.EVT_MENU(self, ID_PROJ_MOLLWEIDE, self.SetMollweideProjection)

        menu_conic = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "C&onic Projections", menu_conic)

        ID_PROJ_LAMBERT = wx.NewId()
        menu_conic.Append(ID_PROJ_LAMBERT, "&Lambert", "Shows a Lambert projection")
        wx.EVT_MENU(self, ID_PROJ_LAMBERT, self.SetLambertProjection)

        ID_PROJ_ALBERS = wx.NewId()
        menu_conic.Append(ID_PROJ_ALBERS, "&Albers", "Shows a Albers projection")
        wx.EVT_MENU(self, ID_PROJ_ALBERS, self.SetAlbersProjection)

        menu_azimuthal = wx.Menu()
        menu_proj.AppendMenu(wx.ID_ANY, "A&zimuthal Projections", menu_azimuthal)

        ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC = wx.NewId()
        menu_azimuthal.Append(ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC, "&Orthographic",
                              "Shows an orthographic azimuthal projection")
        wx.EVT_MENU(self, ID_PROJ_AZIMUTHAL_ORTHOGRAPHIC, self.SetAzimuthalOrtographicProjection)

        ID_PROJ_AZIMUTHAL_EQUIDISTANT = wx.NewId()
        menu_azimuthal.Append(ID_PROJ_AZIMUTHAL_EQUIDISTANT, "&Equidistant",
                              "Shows an orthographic equidstant projection")
        wx.EVT_MENU(self, ID_PROJ_AZIMUTHAL_EQUIDISTANT, self.SetAzimuthalEquidistantProjection)

        ID_PROJ_STEREOGRAPHIC = wx.NewId()
        menu_azimuthal.Append(ID_PROJ_STEREOGRAPHIC, "&Stereographic", "Shows a stereographic projection")
        wx.EVT_MENU(self, ID_PROJ_STEREOGRAPHIC, self.SetStereographicProjection)

        ID_PROJ_AITOFF = wx.NewId()
        menu_azimuthal.Append(ID_PROJ_AITOFF, "&Aitoff Projection", "Shows a Aiteoff projection")
        wx.EVT_MENU(self, ID_PROJ_AITOFF, self.SetAitoffProjection)

        ID_PROJ_WIECHEL = wx.NewId()
        menu_azimuthal.Append(ID_PROJ_WIECHEL, "&Weichel Projection", "Shows a Weichel projection")
        wx.EVT_MENU(self, ID_PROJ_WIECHEL, self.SetWeichelProjection)

        menu_bar.Append(menu_proj, "&Projections")

        menu_views = wx.Menu()

        self.ID_EUROPE = wx.NewId()
        menu_views.Append(self.ID_EUROPE, "Center map on &Europe", "Centers the map on Europe")
        wx.EVT_MENU(self, self.ID_EUROPE, self.Center)

        self.ID_NORTH_AMERICA = wx.NewId()
        menu_views.Append(self.ID_NORTH_AMERICA, "Center map on &North America", "Centers the map on North America")
        wx.EVT_MENU(self, self.ID_NORTH_AMERICA, self.Center)

        self.ID_SOUTH_AMERICA = wx.NewId()
        menu_views.Append(self.ID_SOUTH_AMERICA, "Center map on &South America", "Centers the map on South America")
        wx.EVT_MENU(self, self.ID_SOUTH_AMERICA, self.Center)

        self.ID_ASIA = wx.NewId()
        menu_views.Append(self.ID_ASIA, "Center map on &Asia", "Centers the map on Asia")
        wx.EVT_MENU(self, self.ID_ASIA, self.Center)

        self.ID_AFRICA = wx.NewId()
        menu_views.Append(self.ID_AFRICA, "Center map on A&frica", "Centers the map on Africa")
        wx.EVT_MENU(self, self.ID_AFRICA, self.Center)

        self.ID_OCEANIA = wx.NewId()
        menu_views.Append(self.ID_OCEANIA, "Center map on &Oceania", "Centers the map on Oceania")
        wx.EVT_MENU(self, self.ID_OCEANIA, self.Center)

        self.ID_ANTARCTICA = wx.NewId()
        menu_views.Append(self.ID_ANTARCTICA, "Center map on An&tarctica", "Centers the map on Antarctica")
        wx.EVT_MENU(self, self.ID_ANTARCTICA, self.Center)
        menu_bar.Append(menu_views, "&Center")

        menu_shapes = wx.Menu()
        for shape in self.read_shapes():
            shapeId = wx.NewId()
            self.id_shapes[shapeId] = shape
            menu_shapes.Append(shapeId, shape)
            wx.EVT_MENU(self, shapeId, self.OnSetShape)

        self.setShape(shapeId)
        menu_bar.Append(menu_shapes, "&Shapes")

        menu_tools = wx.Menu()
        ID_OPTIONS = wx.NewId()
        menu_tools.Append(ID_OPTIONS, "&Option", "Shows the options window")
        wx.EVT_MENU(self, ID_OPTIONS, self.OnOptions)
        menu_bar.Append(menu_tools, "&Tools")

        menu_about = wx.Menu()
        ID_INFO = wx.NewId()
        menu_about.Append(ID_INFO, "&Info", "Shows info")
        wx.EVT_MENU(self, ID_INFO, self.OnInfo)
        menu_bar.Append(menu_about, "&About")

        self.SetMenuBar(menu_bar)
        self.SetStatusText("Ready")

    def OnOptions(self, event):
        self.options = options_window.Options(None, self)
        self.options.Show(True)

    def OnQuit(self, event):
        # if self.options != None:
        #	self.options.Destroy()
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

    def Center(self, event):
        if event.GetId() == self.ID_EUROPE:
            self.set_center(20, -5, 35)
        elif event.GetId() == self.ID_NORTH_AMERICA:
            self.set_center(-90, -45, 0)
        elif event.GetId() == self.ID_SOUTH_AMERICA:
            self.set_center(243, 170, 147)
        elif event.GetId() == self.ID_ASIA:
            self.set_center(85, 41, 0)
        elif event.GetId() == self.ID_AFRICA:
            self.set_center(20, 0, 0)
        elif event.GetId() == self.ID_OCEANIA:
            self.set_center(152, 0, 330)
        elif event.GetId() == self.ID_ANTARCTICA:
            self.set_center(120, 0, 280)

    def set_center(self, x, y, z):

        self.rotationx = x
        self.rotationy = y
        self.rotationz = z
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

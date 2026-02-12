import wx


class Options(wx.Frame):
    def __init__(self, parent, cartographer):
        super(Options, self).__init__(parent, title="Options", size=(500, 560))
        self.cartographer = cartographer
        panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(3, 10, 5)
        fgs.AddGrowableCol(1, 1)

        label_parallel_number = wx.StaticText(panel, label="Parallels to draw")
        label_meridian_number = wx.StaticText(panel, label="Meridians to draw")
        label_shapes_color = wx.StaticText(panel, label="Shapes color")
        label_grid_color = wx.StaticText(panel, label="Grid color")

        self.slider_parallel_number = wx.Slider(panel, minValue=2, maxValue=60, value=3, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.slider_meridian_number = wx.Slider(panel, minValue=1, maxValue=120, value=6, style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        # Color pickers
        self.color_shapes = wx.ColourPickerCtrl(panel, colour=cartographer.projection_panel.shapes_color)
        self.color_grid = wx.ColourPickerCtrl(panel, colour=cartographer.projection_panel.grid_color)

        self.check_draw_frame = wx.CheckBox(panel, label='Draw Frame')
        self.check_draw_grid = wx.CheckBox(panel, label='Draw meridians and parallels')
        self.check_draw_specials = wx.CheckBox(panel, label='Draw Special Parallels')
        self.check_draw_tissot = wx.CheckBox(panel, label="Draw Tissot's Indicatrix")

        self.check_draw_frame.SetValue(cartographer.projection_panel.paint_frame)
        self.check_draw_grid.SetValue(cartographer.projection_panel.paint_grid)
        self.check_draw_specials.SetValue(cartographer.projection_panel.paint_grid_specials)
        self.check_draw_tissot.SetValue(cartographer.projection_panel.draw_tissot)

        self.Bind(wx.EVT_SLIDER, self.on_slider_change)
        self.Bind(wx.EVT_CHECKBOX, self.on_slider_change)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_color_change)

        fgs.Add(self.check_draw_frame, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
        fgs.Add(wx.StaticText(panel))

        fgs.Add(self.check_draw_grid, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
        fgs.Add(wx.StaticText(panel))

        fgs.Add(label_meridian_number)
        fgs.Add(self.slider_meridian_number, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))

        fgs.Add(label_parallel_number)
        fgs.Add(self.slider_parallel_number, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))

        fgs.Add(self.check_draw_specials, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
        fgs.Add(wx.StaticText(panel))

        fgs.Add(self.check_draw_tissot, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
        fgs.Add(wx.StaticText(panel))

        fgs.Add(label_shapes_color)
        fgs.Add(self.color_shapes, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))

        fgs.Add(label_grid_color)
        fgs.Add(self.color_grid, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))

        # fgs.AddMany([
        #     (label_res), (self.slider_proj_res, 1, wx.EXPAND), (empty_label),
        #     (self.check_draw_frame, 1, wx.EXPAND), (empty_label), (empty_label),
        #     (self.check_draw_grid, 1, wx.EXPAND), (empty_label), (empty_label),
        #     (label_grid_res, 1, wx.EXPAND), (self.slider_grid_res, 1, wx.EXPAND), (empty_label),
        #     (label_meridian_number), (self.slider_meridian_number, 1, wx.EXPAND), (label_meridian_number_end),
        #     (label_parallel_number), (self.slider_parallel_number, 1, wx.EXPAND), (label_parallel_number_end),
        #     (self.check_draw_specials, 1, wx.EXPAND), (empty_label), (empty_label),
        #     (self.check_show_countries, 1, wx.EXPAND), (empty_label), (empty_label),
        #     (self.check_draw_tissot, 1, wx.EXPAND), (empty_label), (empty_label)])

        hbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        panel.SetSizer(hbox)

    def on_slider_change(self, event):
        self.cartographer.projection_panel.set_paint_frame(self.check_draw_frame.GetValue())
        self.cartographer.projection_panel.set_paint_grid(self.check_draw_grid.GetValue())
        self.cartographer.projection_panel.set_draw_tissot(self.check_draw_tissot.GetValue())
        self.cartographer.projection_panel.set_paint_grid_specials(self.check_draw_specials.GetValue())
        self.cartographer.projection_panel.set_meridian_number(self.slider_meridian_number.GetValue()-1)
        self.cartographer.projection_panel.set_parallel_number(self.slider_parallel_number.GetValue())

        self.cartographer.projection_panel.compute_size()
        self.cartographer.projection_panel.OnDraw()
        self.cartographer.projection_panel.Refresh()

    def on_color_change(self, event):
        """Handle color picker changes"""
        self.cartographer.projection_panel.set_shapes_color(self.color_shapes.GetColour())
        self.cartographer.projection_panel.set_grid_color(self.color_grid.GetColour())
        self.cartographer.projection_panel.Refresh()


if __name__ == '__main__':
    app = wx.App()
    frame = Options(None, None)
    frame.Show()
    app.MainLoop()

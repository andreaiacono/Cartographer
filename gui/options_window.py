import wx


class Options(wx.Frame):
    def __init__(self, parent, cartographer):
        super(Options, self).__init__(parent, title="Options", size=(500, 370))
        self.cartographer = cartographer
        panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(3, 8, 5)
        fgs.AddGrowableCol(1, 1)
        label_res = wx.StaticText(panel, label="Projection Resolution       HiRes")
        label_res_end = wx.StaticText(panel, label=" LowRes")
        # label_grid_res = wx.StaticText(panel, label="Grid Resolution                   HiRes")
        # label_grid_res_end = wx.StaticText(panel, label=" LowRes")

        self.slider_proj_res = wx.Slider(panel, minValue=1, maxValue=cartographer.projection_panel.resolution_scale,
                                         style=wx.SL_HORIZONTAL)
        # self.slider_grid_res = wx.Slider(panel, minValue=1, maxValue=cartographer.projection_panel.resolution_scale,
        #                                  style=wx.SL_HORIZONTAL)
        self.slider_proj_res.SetValue(cartographer.projection_panel.resolution)
        # self.slider_grid_res.SetValue(cartographer.projection_panel.grid_resolution)

        label_parallel_number = wx.StaticText(panel, label="\nDraw a parallel every ")
        label_parallel_number_end = wx.StaticText(panel, label="\n degrees")
        label_meridian_number = wx.StaticText(panel, label="\nDraw a meridian every ")
        label_meridian_number_end = wx.StaticText(panel, label="\n degrees")

        self.slider_parallel_number = wx.Slider(panel, minValue=1, maxValue=90, value=30,
                                                style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.slider_meridian_number = wx.Slider(panel, minValue=1, maxValue=180, value=30,
                                                style=wx.SL_HORIZONTAL | wx.SL_LABELS)

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

        fgs.Add(label_res)
        fgs.Add(self.slider_proj_res, 1, wx.EXPAND)
        fgs.Add(label_res_end)

        fgs.Add(self.check_draw_frame, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
        fgs.Add(wx.StaticText(panel))

        fgs.Add(self.check_draw_grid, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
        fgs.Add(wx.StaticText(panel))

        # fgs.Add(label_grid_res, 1, wx.EXPAND)
        # fgs.Add(self.slider_grid_res, 1, wx.EXPAND)
        # fgs.Add(label_grid_res_end)
        #
        # fgs.Add(label_grid_res, 1, wx.EXPAND)
        # fgs.Add(self.slider_grid_res, 1, wx.EXPAND)
        # fgs.Add(label_grid_res_end)
        #
        fgs.Add(label_meridian_number)
        fgs.Add(self.slider_meridian_number, 1, wx.EXPAND)
        fgs.Add(label_meridian_number_end)

        fgs.Add(label_parallel_number)
        fgs.Add(self.slider_parallel_number, 1, wx.EXPAND)
        fgs.Add(label_parallel_number_end)

        fgs.Add(self.check_draw_specials, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
        fgs.Add(wx.StaticText(panel))

        fgs.Add(self.check_draw_tissot, 1, wx.EXPAND)
        fgs.Add(wx.StaticText(panel))
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

        self.cartographer.projection_panel.set_resolution(self.slider_proj_res.GetValue())
        # self.cartographer.projection_panel.set_grid_resolution(self.slider_grid_res.GetValue())
        self.cartographer.projection_panel.set_paint_frame(self.check_draw_frame.GetValue())
        self.cartographer.projection_panel.set_paint_grid(self.check_draw_grid.GetValue())
        self.cartographer.projection_panel.set_draw_tissot(self.check_draw_tissot.GetValue())
        self.cartographer.projection_panel.set_paint_grid_specials(self.check_draw_specials.GetValue())
        self.cartographer.projection_panel.set_meridian_degrees(self.slider_meridian_number.GetValue())
        self.cartographer.projection_panel.set_parallel_degrees(self.slider_parallel_number.GetValue())

        self.cartographer.projection_panel.compute_size()
        self.cartographer.projection_panel.refresh_window()
        self.cartographer.projection_panel.Refresh()


if __name__ == '__main__':
    app = wx.App()
    frame = Options(None, None)
    frame.Show()
    app.MainLoop()

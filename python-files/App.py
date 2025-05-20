import wx
import math
MAX_IMAGE_SIZE = (600, 600)
class ImagePanel(wx.Panel):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.image = wx.Bitmap(path)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        w, h = self.GetSize()
        img = self.image.ConvertToImage().Scale(w, h)
        dc = wx.PaintDC(self)
        dc.DrawBitmap(wx.Bitmap(img), 0, 0)

class MyFrame(wx.Frame):
    def __init__(self, image_path):
        super().__init__(parent=None, title='Mouse Vector Viewer')
        image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        choices = ["Accular (infantry missiles)", "EXTRA HEF (vehicle missiles)", "PZH (shit artillery)","PHL-81 (infantry missiles)","BM-30 (vehicle missiles)"]

        if not image.IsOk():
            wx.MessageBox(f"Failed to load image: {image_path}", "Error", wx.ICON_ERROR)
            self.Close()
            return

        img_width, img_height = image.GetSize()
        scale_x = min(MAX_IMAGE_SIZE[0] / img_width, 1.0)
        scale_y = min(MAX_IMAGE_SIZE[1] / img_height, 1.0)
        scale = min(scale_x, scale_y)

        if scale < 1.0:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)

        red_img = wx.Image("redscope.png", wx.BITMAP_TYPE_PNG)
        blu_img = wx.Image("bluescope.png", wx.BITMAP_TYPE_PNG)

        imagered = red_img.Scale(50, 50, wx.IMAGE_QUALITY_HIGH)
        imageblu = blu_img.Scale(50, 50, wx.IMAGE_QUALITY_HIGH)

        self.redbmp = wx.Bitmap(imagered)
        self.blubmp = wx.Bitmap(imageblu)

        self.bitmap_original = wx.Bitmap(image)
        self.bitmap_image = self.bitmap_original

        # Marker positions
        self.target_pos_marker = (0,0)
        self.artillery_pos_marker = (0,0)

        # --------------------------------------------- PANELS AND BOXSIZERS ---------------------------------------------
        self.panel = wx.Panel(self)
        self.leftpanel = wx.Panel(self.panel)
        self.rightpanel = wx.Panel(self.panel)
        self.rightpanel.SetBackgroundColour(wx.Colour(0, 0, 200))

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        leftbox = wx.BoxSizer(wx.VERTICAL)
        rightbox = wx.BoxSizer(wx.VERTICAL)

        # ------------------------- LEFT SIDE -------------------------
        self.coord_text = wx.StaticText(self.leftpanel, label="MOUSE VECTOR: (0,0)")

        self.image_ctrl = wx.StaticBitmap(self.leftpanel, bitmap=self.bitmap_original)
        self.image_ctrl.SetSize(self.bitmap_original.GetSize())
        self.image_ctrl.Bind(wx.EVT_PAINT, self.on_paint)
        self.image_ctrl.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.image_ctrl.Bind(wx.EVT_LEFT_DOWN, self.lmb)
        self.image_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.rmb)
        self.image_ctrl.Refresh()
        self.image_ctrl.Update()
          # Custom background

        leftbox.Add(self.coord_text, 0, wx.ALL | wx.CENTER, 10)
        leftbox.Add(self.image_ctrl, 0, wx.ALL | wx.CENTER, 10)

        # ------------------------- RIGHT SIDE -------------------------
        self.artillery_pos = wx.StaticText(self.rightpanel, label="ARTILLERY: ")
        self.target_pos = wx.StaticText(self.rightpanel, label="TARGET: ")
        self.elevation = wx.StaticText(self.rightpanel, label="ELEVATION: SELECT A SHELL")
        self.droplist = wx.Choice(self.rightpanel, choices=choices)
        self.droplist.Bind(wx.EVT_CHOICE, self.droplistus)

        rightbox.Add(self.artillery_pos, 0, wx.ALL | wx.CENTER, 10)
        rightbox.Add(self.target_pos, 0, wx.ALL | wx.CENTER, 10)
        rightbox.Add(self.droplist, 0, wx.ALL | wx.CENTER, 10)
        rightbox.Add(self.elevation, 0, wx.ALL | wx.CENTER, 10)

        self.leftpanel.SetSizer(leftbox)
        self.rightpanel.SetSizer(rightbox)

        hbox.Add(self.leftpanel, 1, wx.EXPAND | wx.ALL, 10)
        hbox.Add(self.rightpanel, 0, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(hbox)

        self.SetSize(800, 700)
        self.Show()

    def droplistus(self, event):
        choice = self.droplist.GetStringSelection()
        match choice:
            case "Accular (infantry missiles)":
                return 1200
            case "EXTRA HEF (vehicle missiles)":
                return 1500
            case "PZH (shit artillery)":
                return 1400
            case "PHL-81 (infantry missiles)":
                return 1300
            case "BM-30 (vehicle missiles)":
                return 1500
    def on_mouse_move(self, event):
        pos = event.GetPosition()
        self.coord_text.SetLabel(f"MOUSE VECTOR: ({pos.x},{pos.y})")

    def lmb(self, event):
        pos = event.GetPosition()
        self.target_pos.SetLabel(f"TARGET: ({pos.x},{pos.y})")
        self.target_pos_marker = (pos.x, pos.y)
        self.image_ctrl.Refresh()
        val=self.droplistus(None)
        shoo=self.get_distance(self.artillery_pos_marker,self.target_pos_marker)
        tism=self.calculate_artillery_elevation(val,shoo)
        print(tism)
        self.elevation.SetLabel(f"ELEVATION: {tism}")
        self.image_ctrl.Refresh()
    def rmb(self, event):
        pos = event.GetPosition()
        self.artillery_pos.SetLabel(f"ARTILLERY: ({pos.x},{pos.y})")
        self.artillery_pos_marker = (pos.x, pos.y)
        self.image_ctrl.Refresh()

    def on_paint(self, event):
        dc = wx.PaintDC(self.image_ctrl)
        dc.DrawBitmap(self.bitmap_image, 0, 0, True)

        if self.target_pos_marker:
            x, y = self.target_pos_marker
            dc.DrawBitmap(self.redbmp, x - 25, y - 25, True)

        if self.artillery_pos_marker:
            x, y = self.artillery_pos_marker
            dc.DrawBitmap(self.blubmp, x - 25, y - 25, True)
    def get_distance(self,shooter_pos, target_pos):
        x1, y1 = shooter_pos
        x2, y2 = target_pos
        return math.sqrt((x2*20 - x1*20)**2 + (y2*20 - y1*20)**2)
    def calculate_artillery_elevation(self,v , horizontal_distance):
        print(horizontal_distance)
        g=196.2
        x = horizontal_distance
        y = 0
        discriminant = v**4 - g * (g * x**2 + 2 * y * v**2)

        if discriminant < 0:
            return None  # CANT HIT HIM 

        sqrt_discriminant = math.sqrt(discriminant)

        angle_low = math.atan((v**2 - sqrt_discriminant) / (g * x))
        angle_high = math.atan((v**2 + sqrt_discriminant) / (g * x))
        
        angle_low=angle_low
        angle_high=angle_high
        low=math.degrees(angle_low)
        high=math.degrees(angle_high)
        return round(low), round(high)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame("rush.png")
        return True

if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()

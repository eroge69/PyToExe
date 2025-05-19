from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

Window.size = (800, 600)

class Kare(Widget):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 40)
        self.pos = (x * 42 + 100, y * 42 + 150)
        self.x_index = x
        self.y_index = y
        self.dolu = False
        self.vuruldu = False
        with self.canvas:
            self.rect_color = Color(1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

    def guncelle(self):
        self.rect.pos = self.pos
        if self.vuruldu:
            self.rect_color.rgb = (1, 0, 0) if self.dolu else (0.5, 0.5, 0.5)
        elif self.dolu:
            self.rect_color.rgb = (0.5, 0.5, 1)
        else:
            self.rect_color.rgb = (1, 1, 1)

class Gemi(Widget):
    def __init__(self, uzunluk=1, **kwargs):
        super().__init__(**kwargs)
        self.uzunluk = uzunluk
        self.size = (42 * uzunluk, 42)
        with self.canvas:
            Color(0.2, 1, 0.2)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.dragging = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dragging = True
            return True

    def on_touch_move(self, touch):
        if self.dragging:
            self.pos = (touch.x - self.width / 2, touch.y - self.height / 2)
            self.rect.pos = self.pos

    def on_touch_up(self, touch):
        self.dragging = False

class Tahta:
    def __init__(self):
        self.kareler = [[Kare(x, y) for y in range(5)] for x in range(5)]

    def ekle(self, root):
        for satir in self.kareler:
            for kare in satir:
                root.add_widget(kare)

    def kare_bul(self, pos):
        for satir in self.kareler:
            for kare in satir:
                if kare.collide_point(*pos):
                    return kare
        return None

    def guncelle(self):
        for satir in self.kareler:
            for kare in satir:
                kare.guncelle()

class AnaOyun(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tahta1 = Tahta()
        self.tahta2 = Tahta()
        self.tahta1.ekle(self)
        self.tahta2.ekle(self)
        for satir in self.tahta2.kareler:
            for kare in satir:
                kare.pos = (kare.pos[0] + 300, kare.pos[1])

        self.gemi1 = Gemi(2)
        self.gemi2 = Gemi(1)
        self.gemi1.pos = (100, 50)
        self.gemi2.pos = (200, 50)
        self.add_widget(self.gemi1)
        self.add_widget(self.gemi2)

        self.onayla_btn = Button(text="Onayla", size_hint=(None, None), size=(120, 50), pos=(650, 20))
        self.onayla_btn.bind(on_release=self.onayla)
        self.add_widget(self.onayla_btn)

        self.oyuncu = 1
        self.durum = "yerlesim"
        self.bind(on_touch_down=self.atis)

    def onayla(self, instance):
        hedef = self.tahta1 if self.oyuncu == 1 else self.tahta2
        for gemi in [self.gemi1, self.gemi2]:
            x = int((gemi.x - 100) // 42)
            y = int((gemi.y - 150) // 42)
            if 0 <= x < 5 and 0 <= y < 5:
                for i in range(gemi.uzunluk):
                    try:
                        hedef.kareler[x + i][y].dolu = True
                    except IndexError:
                        pass
        hedef.guncelle()
        if self.oyuncu == 1:
            self.oyuncu = 2
            self.remove_widget(self.gemi1)
            self.remove_widget(self.gemi2)
            self.gemi1 = Gemi(2)
            self.gemi2 = Gemi(1)
            self.gemi1.pos = (100, 50)
            self.gemi2.pos = (200, 50)
            self.add_widget(self.gemi1)
            self.add_widget(self.gemi2)
        else:
            self.remove_widget(self.gemi1)
            self.remove_widget(self.gemi2)
            self.durum = "oyun"
            self.clear_widgets()
            self.tahta1.ekle(self)
            self.tahta2.ekle(self)
            self.label = Label(text="Oyuncu 1 Sırası", pos=(0, 250), size_hint=(1, None), font_size=20)
            self.add_widget(self.label)

    def atis(self, instance, touch):
        if self.durum != "oyun":
            return
        hedef = self.tahta2 if self.oyuncu == 1 else self.tahta1
        kare = hedef.kare_bul(touch.pos)
        if kare and not kare.vuruldu:
            kare.vuruldu = True
            hedef.guncelle()
            if not kare.dolu:
                self.oyuncu = 2 if self.oyuncu == 1 else 1
                self.label.text = f"Oyuncu {self.oyuncu} Sırası"

class AmiralBattApp(App):
    def build(self):
        return AnaOyun()

if __name__ == '__main__':
    AmiralBattApp().run()
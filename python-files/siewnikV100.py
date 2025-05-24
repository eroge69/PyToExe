import os, json, datetime, random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line

# --- KOLORY ---
KOLOR_TLO = (32/255, 35/255, 39/255, 1)
KOLOR_KARTY = (36/255, 38/255, 46/255, 1)
KOLOR_NIEBIESKI = (59/255, 130/255, 246/255, 1)
KOLOR_BIALY = (1, 1, 1, 1)
KOLOR_CZERWONY = (0.9, 0.1, 0.1, 1)
KOLOR_ZIELONY = (0.25, 0.85, 0.22, 1)
KOLOR_CIEMNY = (0.11, 0.11, 0.11, 1)
KOLOR_SZARY = (0.93, 0.93, 0.93, 1)
KOLOR_CIEN = (0,0,0,0.22)

Window.size = (800, 480)

def policz_obsade(dawka, mtn, sila):
    try:
        obs = dawka*100/(mtn*(sila/100.0))
        return int(round(obs))
    except Exception:
        return 0

class Konfiguracja:
    def __init__(self, plik="konfiguracja.json"):
        self.plik = plik
    def zapisz(self, dane):
        try:
            with open(self.plik, "w") as f:
                json.dump(dane, f)
        except Exception as e:
            print("Błąd zapisu konfiguracji:", e)
    def wczytaj(self):
        try:
            if os.path.exists(self.plik):
                with open(self.plik, "r") as f:
                    return json.load(f)
        except Exception as e:
            print("Błąd odczytu konfiguracji:", e)
        return {}
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line

class MenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = KOLOR_BIALY
        self.font_size = 22
        self.bold = True
        with self.canvas.before:
            # Tło kafelka
            Color(*KOLOR_KARTY)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
            # Białe obramowanie
            Color(*KOLOR_BIALY)
            self.obram = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 14], width=2)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.obram.rounded_rectangle = [self.pos[0], self.pos[1], self.size[0], self.size[1], 14]

class RoundedCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*KOLOR_KARTY)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[28])
            Color(*KOLOR_NIEBIESKI)
            self.obram = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 28], width=3)
        self.bind(pos=self.update_bg, size=self.update_bg)
    def update_bg(self, *a):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.obram.rounded_rectangle = [self.pos[0], self.pos[1], self.size[0], self.size[1], 28]
# --- NOWY STYL POPUPA ---

class CardPopup(Popup):
    def __init__(self, title="", content=None, size_hint=(0.5, None), color=KOLOR_NIEBIESKI, height=None, **kwargs):
        super().__init__(title="", size_hint=size_hint, auto_dismiss=False, **kwargs)
        self.color = color
        self._padding = 38
        with self.canvas.before:
            # Cień pod kafelkiem (lekki cień)
            Color(*KOLOR_CIEN)
            self.shadow = RoundedRectangle(pos=(self.x+8, self.y-8), size=self.size, radius=[36])
            # Tło kafelka
            Color(*KOLOR_KARTY)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[36])
            # Ramka
            Color(*color)
            self.line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 36], width=4)
        self.bind(pos=self.update_bg, size=self.update_bg)
        self.content = content if content else Label(text=title, font_size=32, color=color, halign='center', bold=True)
        if height is None:
            if hasattr(self.content, 'height'):
                self.height = self.content.height + self._padding * 2
            else:
                self.height = 240
        else:
            self.height = height

    def update_bg(self, *args):
        self.shadow.pos = (self.pos[0]+8, self.pos[1]-8)
        self.shadow.size = self.size
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.line.rounded_rectangle = [self.pos[0], self.pos[1], self.size[0], self.size[1], 36]

# --- Nowy NumericInputPopup
class NumericKeyboard(GridLayout):
    def __init__(self, text_input, **kwargs):
        super().__init__(cols=3, spacing=7, size_hint_y=None, height=200, **kwargs)
        self.text_input = text_input
        for key in ['1','2','3','4','5','6','7','8','9','.','0','<-']:
            btn = Button(text=key, font_size=28, background_color=KOLOR_BIALY, color=KOLOR_NIEBIESKI, bold=True)
            btn.bind(on_press=self.on_key_press)
            self.add_widget(btn)
    def on_key_press(self, instance):
        key = instance.text
        if key == '<-':
            self.text_input.text = self.text_input.text[:-1]
        else:
            self.text_input.insert_text(key)

class NumericInputPopup(CardPopup):
    def __init__(self, label, value, on_validate, input_filter='float', **kwargs):
        content = BoxLayout(orientation='vertical', spacing=13, padding=[24,20,24,18])
        content.add_widget(Label(text=label, font_size=28, color=KOLOR_NIEBIESKI, bold=True, size_hint_y=None, height=46))
        self.input = TextInput(
            text=str(value),
            font_size=42,
            multiline=False,
            halign='center',
            input_filter=input_filter,
            size_hint_y=None,
            height=66,
            background_color=KOLOR_SZARY,
            foreground_color=KOLOR_NIEBIESKI,
            cursor_color=KOLOR_NIEBIESKI,
            keyboard_mode='managed'
        )
        content.add_widget(self.input)
        content.add_widget(NumericKeyboard(self.input))
        ok_btn = Button(text="ZATWIERDŹ", font_size=28, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY, size_hint_y=None, height=58, bold=True, background_normal='')
        ok_btn.bind(on_press=lambda x: self._validate(on_validate))
        content.add_widget(ok_btn)
        super().__init__(content=content, size_hint=(0.4,0.43), color=KOLOR_NIEBIESKI, **kwargs)
    def _validate(self, on_validate):
        t = self.input.text.replace(",",".")
        try:
            val = float(t)
            on_validate(t)
            self.dismiss()
        except ValueError:
            self.input.background_color = KOLOR_CZERWONY

class AlarmManager:
    def __init__(self, root):
        self.root = root
        self._active_popup = None
        self.sound_alarm = SoundLoader.load('alarm.wav')
        self.sound_beep = SoundLoader.load('beep.wav')
    def show_alarm(self, text, color=KOLOR_BIALY, beep=None, blocking=True):
        self.close_alarm()
        main = BoxLayout(orientation='vertical', spacing=20, padding=18)
        main.add_widget(Label(text=text, font_size=36, color=color, halign="center", bold=True))
        ok_btn = Button(text="OK", font_size=28, background_color=color, color=KOLOR_BIALY, size_hint_y=None, height=54, bold=True)
        main.add_widget(ok_btn)
        popup = CardPopup(content=main, color=KOLOR_CZERWONY if color==KOLOR_CZERWONY else KOLOR_NIEBIESKI, size_hint=(0.39, 0.24))
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()
        self._active_popup = popup
        if beep == "alarm" and self.sound_alarm:
            self.sound_alarm.play()
        elif beep == "beep" and self.sound_beep:
            self.sound_beep.play()
        elif beep is True and self.sound_beep:
            self.sound_beep.play()
        if not blocking:
            Clock.schedule_once(lambda dt: self.close_alarm(), 8)
    def close_alarm(self, *args):
        if self._active_popup:
            self._active_popup.dismiss()
            self._active_popup = None
class ProbaKreconaFlow:
    def __init__(self, root, autostart_pro=False):
        self.root = root
        self.czas_proby = 4   # czas próby w sekundach DO USTAWIENIA >DOCELOWO 60S
        self.countdown_value = self.czas_proby
        self.popup = None
        self._clock_ev = None
        self.autostart_pro = autostart_pro
        self.licznik_obrotow = 0
        self.czy_liczy = False

    def start(self):
        self.countdown_value = self.czas_proby
        self.licznik_obrotow = 0
        self.czy_liczy = False
        main = BoxLayout(orientation='vertical', spacing=20, padding=20)
        main.add_widget(Label(text="[b]ROZPOCZNIJ PRÓBĘ (4s)[/b]", markup=True, font_size=32, color=KOLOR_NIEBIESKI))
        btn_start = Button(text="START", font_size=28, background_color=KOLOR_ZIELONY, color=KOLOR_CIEMNY, size_hint_y=None, height=54, bold=True, background_normal='')
        btn_start.bind(on_press=self._start_countdown)
        main.add_widget(btn_start)
        self.popup = CardPopup(content=main, size_hint=(0.5, 0.3), color=KOLOR_NIEBIESKI)
        self.popup.open()

    def _start_countdown(self, inst):
        self.popup.dismiss()
        main = BoxLayout(orientation='vertical', spacing=12, padding=20)
        self.countdown_label = Label(text=f"{self.countdown_value}s", font_size=64, color=KOLOR_ZIELONY, halign='center')
        main.add_widget(Label(text="[b]TRWA PRÓBA [/b]", markup=True, font_size=32, color=KOLOR_NIEBIESKI))
        main.add_widget(self.countdown_label)
        self.popup = CardPopup(content=main, size_hint=(0.5, 0.3), color=KOLOR_NIEBIESKI)
        self.popup.open()
        self.licznik_obrotow = 0
        self.czy_liczy = True
        self._clock_ev = Clock.schedule_interval(self._countdown_step, 1)

    def _countdown_step(self, dt):
        self.countdown_value -= 1
        self.countdown_label.text = f"{self.countdown_value}s"
        if self.countdown_value <= 0:
            self._clock_ev.cancel()
            self.czy_liczy = False
            self.popup.dismiss()
            Clock.schedule_once(lambda dt: self._popup_waga(), 0.3)
            return False
        return True

    def _popup_waga(self):
        # Po próbie pytamy o wagę
        label = f"Podaj wagę nasion [g]"
        self.root.numeric_input_popup(label, "", self._po_wpisaniu_wagi)

    def _po_wpisaniu_wagi(self, waga):
        try:
            waga = float(str(waga).replace(",", "."))
        except:
            waga = 0.0
        licznik = self.licznik_obrotow
        if licznik == 0:
            g_per_obrot = 0.0
        else:
            g_per_obrot = waga / licznik

        self.root.g_per_obrot = g_per_obrot

        if self.autostart_pro:
            self.root.otworz_pro_popup()
        else:
            # Teraz pojawi się popup na wpisanie dawki kg/ha
            self.root.numeric_input_popup(
                "USTAW DAWKĘ [kg/ha]",
                "",
                self._po_wpisaniu_dawki
            )

    def _po_wpisaniu_dawki(self, dawka):
        try:
            dawka = float(str(dawka).replace(",", "."))
        except:
            dawka = 0.0
        self.root.set_dawka_na_ha(dawka, is_zadana=True)
        # Po chwili otwiera się flow eksperta:
        Clock.schedule_once(lambda dt: ExpertStartPopup(self.root).open(), 0.7)

    def impuls_walka(self):
        if self.czy_liczy:
            self.licznik_obrotow += 1






class ExpertStartPopup(CardPopup):
    def __init__(self, root):
        self.root = root
        main = BoxLayout(orientation='vertical', spacing=18, padding=[18, 24, 18, 24], size_hint_y=None)
        main.add_widget(Label(
            text="[b]CZY ZNASZ MTN I SIŁĘ KIEŁKOWANIA[/b]",
            markup=True,
            font_size=25,
            color=KOLOR_NIEBIESKI,
            halign='center'
        ))
        btn_tak = Button(
            text="TAK", font_size=26, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY,
            bold=True, background_normal='', size_hint_y=None, height=54
        )
        btn_tak.bind(on_press=self.tak)
        btn_nie = Button(
            text="NIE", font_size=26, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY,
            bold=True, background_normal='', size_hint_y=None, height=54
        )
        btn_nie.bind(on_press=self.nie)
        main.add_widget(btn_tak)
        main.add_widget(btn_nie)
        main.bind(minimum_height=main.setter('height'))
        super().__init__(content=main, size_hint=(0.54, None), color=KOLOR_NIEBIESKI, height=main.height + 34)

    def tak(self, inst):
        self.dismiss()
        ExpertInputMTN(self.root).open()
    def nie(self, inst):
        self.dismiss()
        ExpertChooseSeed(self.root).open()

class ExpertInputMTN(CardPopup):
    def __init__(self, root):
        self.root = root
        main = BoxLayout(orientation='vertical', spacing=16, padding=[20,16,20,12])
        main.add_widget(Label(text="[b]WPROWADŹ MTN (g)[/b]", markup=True, font_size=25, color=KOLOR_NIEBIESKI))
        self.input = TextInput(text="", font_size=32, multiline=False, halign='center', input_filter='float', size_hint_y=None, height=50,
                               background_color=KOLOR_SZARY, foreground_color=KOLOR_NIEBIESKI)
        main.add_widget(self.input)
        main.add_widget(NumericKeyboard(self.input))
        btn_ok = Button(text="DALEJ", font_size=24, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY, bold=True, background_normal='', size_hint_y=None, height=46)
        btn_ok.bind(on_press=self.ok)
        main.add_widget(btn_ok)
        super().__init__(content=main, size_hint=(0.54,0.22), color=KOLOR_NIEBIESKI)
    def ok(self, inst):
        try:
            mtn = float(self.input.text.replace(",",".")) if self.input.text else 0
        except:
            mtn = 0
        self.dismiss()
        ExpertInputSila(self.root, mtn).open()

class ExpertInputSila(CardPopup):
    def __init__(self, root, mtn):
        self.root = root
        self.mtn = mtn
        main = BoxLayout(orientation='vertical', spacing=16, padding=[20,16,20,12])
        main.add_widget(Label(text="[b]SIŁA KIEŁKOWANIA (%)\n[/b]", markup=True, font_size=24, color=KOLOR_NIEBIESKI))
        self.input = TextInput(text="90", font_size=32, multiline=False, halign='center', input_filter='float', size_hint_y=None, height=50,
                               background_color=KOLOR_SZARY, foreground_color=KOLOR_NIEBIESKI)
        main.add_widget(self.input)
        main.add_widget(NumericKeyboard(self.input))
        btn_ok = Button(text="PRZELICZ", font_size=24, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY, bold=True, background_normal='', size_hint_y=None, height=46)
        btn_ok.bind(on_press=self.ok)
        main.add_widget(btn_ok)
        super().__init__(content=main, size_hint=(0.54,0.24), color=KOLOR_NIEBIESKI)
    def ok(self, inst):
        try:
            sila = float(self.input.text.replace(",",".")) if self.input.text else 90
        except:
            sila = 90
        obsada = policz_obsade(self.root.dawka, self.mtn, sila)
        self.dismiss()
        ObsadaWynikPopup(self.root, obsada, persist=True).open()
class ExpertChooseSeed(CardPopup):
    NASIONA = [
        ("Bobik", 430),
        ("Facelia", 2.2),
        ("Gorczyca", 8),
        ("Groch", 220),
        ("Gryka", 25),
        ("Jęczmień", 44),
        ("Łubin", 125),
        ("Owies", 34),
        ("Pszenżyto", 44),
        ("Rzepak", 5),
        ("Soja", 165),
        ("Sorgo", 23),
        ("Słonecznik", 65),
        ("Żyto", 32),
    ]
    def __init__(self, root):
        self.root = root
        main = BoxLayout(orientation='vertical', spacing=7, padding=[8,8,8,8])

        btn_up = Button(text="PRZEWIŃ W GÓRĘ", font_size=40, size_hint_y=None, height=50, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)
        btn_down = Button(text="PRZEWIŃ W DÓŁ", font_size=40, size_hint_y=None, height=50, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)

        # Najważniejsze: rozmiar ScrollView i GridLayout
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, spacing=7, size_hint_y=None, padding=[0,8])
        grid.bind(minimum_height=grid.setter('height'))

        for name, mtn in sorted(self.NASIONA, key=lambda x: x[0]):
            btn = Button(
                text=f"{name} (MTN {mtn}g)",
                font_size=23,
                background_color=KOLOR_BIALY,
                color=KOLOR_NIEBIESKI,
                bold=True,
                background_normal='',
                background_down='',
                size_hint_y=None,
                height=52
            )
            btn.bind(on_press=lambda btn, n=name, m=mtn: self.wybrano(n, m))
            grid.add_widget(btn)
        scroll.add_widget(grid)

        main.add_widget(btn_up)
        main.add_widget(scroll)
        main.add_widget(btn_down)

        btn_close = Button(text="Zamknij", font_size=19, background_color=KOLOR_CIEMNY, color=KOLOR_BIALY,
                           background_normal='', background_down='', size_hint_y=None, height=40)
        btn_close.bind(on_press=self.dismiss)
        main.add_widget(btn_close)
        super().__init__(content=main, size_hint=(0.74, 0.8), color=KOLOR_NIEBIESKI)

        def scroll_up(instance):
            scroll.scroll_y = min(1.0, scroll.scroll_y + 0.2)
        def scroll_down(instance):
            scroll.scroll_y = max(0.0, scroll.scroll_y - 0.2)
        btn_up.bind(on_press=scroll_up)
        btn_down.bind(on_press=scroll_down)

    def wybrano(self, nazwa, mtn):
        sila = 90
        obsada = policz_obsade(self.root.dawka, mtn, sila)
        self.dismiss()
        ObsadaWynikPopup(self.root, obsada, persist=True).open()
class ProListaNasionPopup(CardPopup):
    NASIONA = [
        ("Bobik", 430),
        ("Facelia", 2.2),
        ("Gorczyca", 8),
        ("Groch", 220),
        ("Gryka", 25),
        ("Jęczmień", 44),
        ("Łubin", 125),
        ("Owies", 34),
        ("Pszenżyto", 44),
        ("Rzepak", 5),
        ("Soja", 165),
        ("Sorgo", 23),
        ("Słonecznik", 65),
        ("Żyto", 32),
    ]
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        main = BoxLayout(orientation='vertical', spacing=7, padding=[8,8,8,8])
        btn_up = Button(text="PRZEWIŃ W GÓRĘ", font_size=40, size_hint_y=None, height=50, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)
        btn_down = Button(text="PRZEWIŃ W DÓŁ", font_size=40, size_hint_y=None, height=50, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, spacing=7, size_hint_y=None, padding=[0,8])
        grid.bind(minimum_height=grid.setter('height'))

        for name, mtn in sorted(self.NASIONA, key=lambda x: x[0]):
            btn = Button(
                text=f"{name} (MTN {mtn}g)",
                font_size=23,
                background_color=KOLOR_BIALY,
                color=KOLOR_NIEBIESKI,
                bold=True,
                background_normal='',
                background_down='',
                size_hint_y=None,
                height=52
            )
            btn.bind(on_press=lambda btn, n=name, m=mtn: self.wybrano(n, m))
            grid.add_widget(btn)
        scroll.add_widget(grid)

        main.add_widget(btn_up)
        main.add_widget(scroll)
        main.add_widget(btn_down)
        btn_close = Button(text="Zamknij", font_size=19, background_color=KOLOR_CIEMNY, color=KOLOR_BIALY,
                           background_normal='', background_down='', size_hint_y=None, height=40)
        btn_close.bind(on_press=self.dismiss)
        main.add_widget(btn_close)
        super().__init__(content=main, size_hint=(0.74, 0.8), color=KOLOR_NIEBIESKI)

        def scroll_up(instance):
            scroll.scroll_y = min(1.0, scroll.scroll_y + 0.2)
        def scroll_down(instance):
            scroll.scroll_y = max(0.0, scroll.scroll_y - 0.2)
        btn_up.bind(on_press=scroll_up)
        btn_down.bind(on_press=scroll_down)

    def wybrano(self, nazwa, mtn):
        self.dismiss()
        self.callback(mtn)

class ObsadaWynikPopup(CardPopup):
    def __init__(self, root, obsada, persist=False):
        self.root = root
        self.persist = persist
        main = BoxLayout(orientation='vertical', spacing=14, padding=[18, 24, 18, 16], size_hint_y=None)
        main.add_widget(Label(
            text=f"[b]{obsada}[/b]",
            markup=True,
            font_size=54,
            color=KOLOR_NIEBIESKI,
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=66
        ))
        main.add_widget(Label(
            text="szt/m²",
            font_size=24,
            color=KOLOR_NIEBIESKI,
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=32
        ))
        main.bind(minimum_height=main.setter('height'))
        super().__init__(content=main, size_hint=(0.54, None), color=KOLOR_NIEBIESKI, height=main.height + 60)
        if persist:
            self.root.set_obsada_roslin(obsada)
        else:
            self.root.ukryj_obsada_roslin()
        Clock.schedule_once(lambda dt: self.dismiss(), 5)

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=[20, 20, 20, 12], spacing=18, **kwargs)
        from kivy.graphics import Color, RoundedRectangle
        import datetime
        from kivy.clock import Clock
        from kivy.uix.widget import Widget
        from kivy.core.audio import SoundLoader

        with self.canvas.before:
            Color(*KOLOR_TLO)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.konfiguracja = Konfiguracja()
        self.szerokosc_robocza = 3.0
        self.liczba_sekcji = 21
        self.sekcje_sciezek = 4
        self.ilosc_przejazdow = 5
        self.nr_przejazdu_do_sciezki = self.ilosc_przejazdow
        self.dawka = 180
        self.dawka_zadana = 180
        self.predkosc = 0.0
        self.obsada_roslin = None
        self.dzienny_ha = 0.0
        self.calkowity_ha = 0.0
        self.czy_sieje = False
        self.korekta_dawki_sciezki = True
        self.g_per_obrot = 12.0
        self.silnik_walek_aktywny = False
        self.obroty_silnika = 0
        self.napiecie = 12.7
        self.napiecie_alarm = False
        self.nasiona_alarm = False
        self.ostatnie_obroty_walka = datetime.datetime.now()
        self.obroty_walka_alarm = False
        self.tryb_pro = False
        self.sciezki_technologiczne = True  # <-- ważne, kontroluje wyświetlanie
        self.sciezki_container = None
        self._miganie = False
        self._nasiona_alarm_popup = None
        self._obroty_alarm_popup = None
        self._napiecie_alarm_popup = None

        self.alarms = AlarmManager(self)
        self.sound_beep = SoundLoader.load('beep.wav')
        self.sound_alarm = SoundLoader.load('alarm.wav')

        # --- Top bar & icons ---
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=130, spacing=20)
        self.btn_menu = Button(text="Menu", size_hint=(None, 1), width=130, font_size=40 , color=KOLOR_NIEBIESKI)
        self.btn_menu.bind(on_press=self.otworz_menu)
        top.add_widget(self.btn_menu)
        self.ikona_gps = Image(source="gps_green.png", size_hint=(None, 1), width=130)
        top.add_widget(self.ikona_gps)
        self.ikona_sciezek = Image(source="sciezki_green.png", size_hint=(None, 1), width=130)
        top.add_widget(self.ikona_sciezek)
        self.ikona_nasiona = Image(source="nasiona_green.png", size_hint=(None, 1), width=130)
        top.add_widget(self.ikona_nasiona)
        self.lbl_napiecie = Label(text=f"{self.napiecie:.2f}V", font_size=40, color=KOLOR_CZERWONY, size_hint_x=0.14)
        top.add_widget(self.lbl_napiecie)
        self.lbl_czas = Label(text="", font_size=40, color=KOLOR_ZIELONY, size_hint_x=0.4)
        top.add_widget(self.lbl_czas)
        self.ikona_pro = Label(text="", font_size=30, color=KOLOR_ZIELONY, size_hint_x=0.1, markup=True)
        top.add_widget(self.ikona_pro)

        self.add_widget(top)

        # --- Main Grid 1 ---
        self.grid1 = GridLayout(cols=3, spacing=22, size_hint_y=None, height=120, padding=[10, 0, 10, 0])
        kafel_style = dict(padding=[18, 10], spacing=6, size_hint=(1, 1))

        self.dawka_card = RoundedCard(orientation="vertical", **kafel_style)
        self.dawka_card.add_widget(
            Label(text="[b]DAWKA kg/ha[/b]", markup=True, font_size=28, color=KOLOR_NIEBIESKI, bold=True))
        self.lbl_dawka = Label(text=f"[b]{int(round(self.dawka))}[/b]", markup=True, font_size=54, color=KOLOR_BIALY,
                               bold=True)
        self.dawka_card.add_widget(self.lbl_dawka)

        self.obsada_card = RoundedCard(orientation="vertical", **kafel_style)
        self.obsada_card.add_widget(
            Label(text="[b]OBSADA szt/m²[/b]", markup=True, font_size=28, color=KOLOR_NIEBIESKI, bold=True))
        self.lbl_obsada = Label(text="", markup=True, font_size=54, color=KOLOR_BIALY, bold=True)
        self.obsada_card.add_widget(self.lbl_obsada)

        self.predkosc_card = RoundedCard(orientation="vertical", **kafel_style)
        self.predkosc_card.add_widget(
            Label(text="[b]PRĘDKOŚĆ km/h[/b]", markup=True, font_size=28, color=KOLOR_NIEBIESKI, bold=True))
        self.lbl_predkosc = Label(text=f"[b]{self.predkosc:.1f}[/b]", markup=True, font_size=54, color=KOLOR_BIALY,
                                  bold=True)
        self.predkosc_card.add_widget(self.lbl_predkosc)

        self.grid1.add_widget(self.dawka_card)
        self.grid1.add_widget(self.obsada_card)
        self.grid1.add_widget(self.predkosc_card)

        self.add_widget(self.grid1)

        # --- Main Grid 2 ---
        grid2 = GridLayout(cols=3, spacing=22, size_hint_y=None, height=120, padding=[10, 0, 10, 0])

        dzienny_card = RoundedCard(orientation="vertical", **kafel_style)
        dzienny_card.add_widget(
            Label(text="[b]DZIENNE HA[/b]", markup=True, font_size=28, color=KOLOR_NIEBIESKI, bold=True))
        self.lbl_dzienny_ha = Label(text=f"{self.dzienny_ha:.2f}", font_size=54, color=KOLOR_BIALY, bold=True)
        dzienny_card.add_widget(self.lbl_dzienny_ha)
        dzienny_card.add_widget(Label(text="", font_size=24, color=KOLOR_BIALY, bold=True))
        dzienny_card.bind(on_touch_down=self.reset_dzienny_start)
        dzienny_card.bind(on_touch_up=self.reset_dzienny_stop)
        grid2.add_widget(dzienny_card)

        calk_card = RoundedCard(orientation="vertical", **kafel_style)
        calk_card.add_widget(
            Label(text="[b]ŁĄCZNIE HA[/b]", markup=True, font_size=28, color=KOLOR_NIEBIESKI, bold=True))
        self.lbl_calkowity_ha = Label(text=f"{self.calkowity_ha:.2f}", font_size=54, color=KOLOR_BIALY, bold=True)
        calk_card.add_widget(self.lbl_calkowity_ha)
        calk_card.add_widget(Label(text="", font_size=24, color=KOLOR_BIALY, bold=True))
        grid2.add_widget(calk_card)

        wydajnosc_card = RoundedCard(orientation="vertical", **kafel_style)
        wydajnosc_card.add_widget(
            Label(text="[b]HA/H[/b]", markup=True, font_size=28, color=KOLOR_NIEBIESKI, bold=True))
        self.lbl_wydajnosc = Label(text="0.00", font_size=54, color=KOLOR_BIALY, bold=True)
        wydajnosc_card.add_widget(self.lbl_wydajnosc)
        wydajnosc_card.add_widget(Label(text="", font_size=24, color=KOLOR_BIALY, bold=True))
        grid2.add_widget(wydajnosc_card)

        self.add_widget(grid2)

        # --- Main Grid 3 ---
        grid3 = GridLayout(cols=2, spacing=22, size_hint_y=None, height=100, padding=[80, 0, 80, 0])

        walek_card = RoundedCard(orientation="vertical", **kafel_style)
        walek_card.add_widget(
            Label(text="[b]WAŁEK obr/s[/b]", markup=True, font_size=30, color=KOLOR_NIEBIESKI, bold=True))
        self.lbl_obroty_walka = Label(text="0.00", font_size=54, color=KOLOR_BIALY, bold=True)
        walek_card.add_widget(self.lbl_obroty_walka)
        grid3.add_widget(walek_card)

        status_card = RoundedCard(orientation="vertical", **kafel_style)
        self.lbl_status_wysiewu = Label(
            text="[b]STOP[/b]", markup=True, font_size=48, color=KOLOR_CZERWONY, halign='center', bold=True
        )
        status_card.add_widget(Label(text="", font_size=14, color=KOLOR_KARTY))
        status_card.add_widget(self.lbl_status_wysiewu)
        status_card.add_widget(Label(text="", font_size=14, color=KOLOR_KARTY))
        grid3.add_widget(status_card)

        self.add_widget(grid3)

        # --- Rozciągliwy widget (wypycha niżej) ---
        self.add_widget(Widget(size_hint_y=1))

        # --- Ścieżki technologiczne (nad próba kręconą) ---
        self.sciezki_container = BoxLayout(size_hint_y=None, height=52, padding=[0, 6, 0, 0])
        self.add_widget(self.sciezki_container)
        self.odswiez_sciezki_box()

        # --- Próba kręcona (na samym dole) ---
        self.btn_proba = Button(
            text="PRÓBA KRĘCONA", font_size=27, size_hint_y=None, height=58,
            background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY, bold=True, background_normal=''
        )
        self.btn_proba.bind(on_press=self.otworz_probe)
        self.add_widget(self.btn_proba)

        # --- Timery / schedulery ---
        self.load_config()
        Clock.schedule_interval(self.update_czas, 1)
        Clock.schedule_interval(self.update_dzienny_ha, 1)
        Clock.schedule_interval(self.check_nasiona_status, 1)
        Clock.schedule_interval(self.steruj_walkiem, 1)
        Clock.schedule_interval(self.symuluj_alarmy, 1)
        Clock.schedule_interval(self.check_alarms, 1)
        Clock.schedule_interval(self.migaj_status, 0.5)

    def odswiez_sciezki_box(self):
        self.sciezki_container.clear_widgets()
        if not self.sciezki_technologiczne:
            # Ukryj container (zero wysokości)
            self.sciezki_container.height = 0
            self.sciezki_container.size_hint_y = None
            return
        else:
            self.sciezki_container.size_hint_y = None
            self.sciezki_container.height = 52

        btn_minus = Button(
            text="ODEJMIJ PRZEJAZD",
            font_size=19,
            background_color=KOLOR_ZIELONY,
            color=KOLOR_BIALY,
            size_hint_x=0.33
        )
        btn_minus.bind(on_press=self.sciezki_minus)
        self.sciezki_container.add_widget(btn_minus)

        lbl = Label(
            text=f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}",
            font_size=40,
            color=KOLOR_BIALY,
            size_hint_x=0.34,
            halign="center"
        )
        lbl.bind(size=lambda s, *a: setattr(s, 'text_size', s.size))
        self.sciezki_container.add_widget(lbl)
        self.lbl_sciezki_info = lbl  # zapisz referencję do aktualizacji tekstu

        btn_plus = Button(
            text="DODAJ PRZEJAZD",
            font_size=19,
            background_color=KOLOR_ZIELONY,
            color=KOLOR_BIALY,
            size_hint_x=0.33
        )
        btn_plus.bind(on_press=self.sciezki_plus)
        self.sciezki_container.add_widget(btn_plus)

    def sciezki_minus(self, inst):
        if self.nr_przejazdu_do_sciezki > 0:
            self.nr_przejazdu_do_sciezki -= 1
            if self.nr_przejazdu_do_sciezki == 0:
                self.alarms.show_alarm("ZAŁĄCZONO ŚCIEŻKĘ", color=KOLOR_ZIELONY, beep="beep", blocking=False)
                self.nr_przejazdu_do_sciezki = self.ilosc_przejazdow
        self.lbl_sciezki_info.text = f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}"
        self.update_sciezki_ikona()

    def sciezki_plus(self, inst):
        if self.nr_przejazdu_do_sciezki < self.ilosc_przejazdow:
            self.nr_przejazdu_do_sciezki += 1
        self.lbl_sciezki_info.text = f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}"
        self.update_sciezki_ikona()

    def update_ikona_sciezek_visibility(self):
        if self.sciezki_technologiczne:
            self.ikona_sciezek.opacity = 1  # włącz widoczność
            self.ikona_sciezek.disabled = False
        else:
            self.ikona_sciezek.opacity = 0  # ukryj ikonę
            self.ikona_sciezek.disabled = True

    def update_sciezki_ikona(self):
        if self.nr_przejazdu_do_sciezki == self.ilosc_przejazdow:
            self.ikona_sciezek.source = "sciezki_green.png"
        else:
            self.ikona_sciezek.source = "sciezki_red.png"

    # ---- SEKCJA: TRYB PRO / EKSPERT ----

    def odswiez_grafike_pro(self):
        self.ikona_pro.markup = True
        self.ikona_pro.text = "[b]PRO[/b]" if self.tryb_pro else ""

    def zamien_kafelki_pro(self, pro=True):
        self.grid1.clear_widgets()
        if pro:
            self.grid1.add_widget(self.obsada_card)
            self.grid1.add_widget(self.dawka_card)
            self.grid1.add_widget(self.predkosc_card)
        else:
            self.grid1.add_widget(self.dawka_card)
            self.grid1.add_widget(self.obsada_card)
            self.grid1.add_widget(self.predkosc_card)

    # ---- SEKCJA: PRÓBA KRĘCONA + PRO ----

    def otworz_probe(self, inst, pro_flow=False):
        if self.tryb_pro or pro_flow:
            self.proba_flow = ProbaKreconaFlow(self, autostart_pro=True)
            self.proba_flow.start()
        else:
            self.proba_flow = ProbaKreconaFlow(self)
            self.proba_flow.start()

    def otworz_pro_popup(self):
        self.odswiez_grafike_pro()
        self.proba_pro_krok1()

    def proba_pro_krok1(self):
        def on_tak(_):
            popup.dismiss()
            self.proba_pro_wpisz_mtn()

        def on_nie(_):
            popup.dismiss()
            self.proba_pro_lista_mtn()

        box = BoxLayout(orientation='vertical', spacing=12, padding=24)
        box.add_widget(Label(text="Czy znasz MTN (g)?", font_size=28, color=KOLOR_NIEBIESKI))
        btn_tak = Button(text="TAK", font_size=26, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)
        btn_nie = Button(text="NIE", font_size=26, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)
        btn_tak.bind(on_press=on_tak)
        btn_nie.bind(on_press=on_nie)
        box.add_widget(btn_tak)
        box.add_widget(btn_nie)
        popup = CardPopup(content=box, size_hint=(0.5, 0.3), color=KOLOR_NIEBIESKI)
        popup.open()

    def proba_pro_wpisz_mtn(self):
        def on_ok(val):
            self.pro_mtn = float(val.replace(",", "."))
            self.proba_pro_krok2()

        self.numeric_input_popup("Wpisz MTN [g]", "", on_ok)

    def proba_pro_lista_mtn(self):
        def callback(mtn):
            self.pro_mtn = mtn
            self.proba_pro_krok2()

        ProListaNasionPopup(self, callback).open()

    def proba_pro_krok2(self):
        def on_tak(_):
            popup.dismiss()
            self.proba_pro_wpisz_sila()

        def on_nie(_):
            popup.dismiss()
            self.pro_sila = 90
            self.proba_pro_krok3()

        box = BoxLayout(orientation='vertical', spacing=12, padding=24)
        box.add_widget(Label(text="Czy znasz siłę kiełkowania [%]?", font_size=26, color=KOLOR_NIEBIESKI))
        btn_tak = Button(text="TAK", font_size=26, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)
        btn_nie = Button(text="NIE", font_size=26, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY)
        btn_tak.bind(on_press=on_tak)
        btn_nie.bind(on_press=on_nie)
        box.add_widget(btn_tak)
        box.add_widget(btn_nie)
        popup = CardPopup(content=box, size_hint=(0.5, 0.3), color=KOLOR_NIEBIESKI)
        popup.open()

    def proba_pro_wpisz_sila(self):
        def on_ok(val):
            self.pro_sila = float(val.replace(",", "."))
            self.proba_pro_krok3()

        self.numeric_input_popup("Wpisz siłę kiełkowania [%]", 90, on_ok)

    def proba_pro_krok3(self):
        def on_ok(val):
            self.pro_obsada = int(float(val.replace(",", ".")))
            self.proba_pro_wynik()

        self.numeric_input_popup("Podaj docelową obsadę [szt/m²]", 400, on_ok)

    def proba_pro_wynik(self):
        dawka = (self.pro_obsada * self.pro_mtn) / self.pro_sila

        def on_zatwierdz(_):
            self.set_dawka_na_ha(dawka, is_zadana=True)
            self.set_obsada_roslin(self.pro_obsada)
            self.odswiez_grafike_pro()
            self.zamien_kafelki_pro(True)
            popup.dismiss()

        box = BoxLayout(orientation='vertical', spacing=16, padding=24)
        box.add_widget(Label(text=f"Obliczona dawka:", font_size=28, color=KOLOR_NIEBIESKI))
        box.add_widget(Label(text=f"[b]{dawka:.2f} kg/ha[/b]", markup=True, font_size=48, color=KOLOR_ZIELONY))
        btn = Button(text="USTAW DAWKĘ", font_size=26, background_color=KOLOR_ZIELONY, color=KOLOR_BIALY)
        btn.bind(on_press=on_zatwierdz)
        box.add_widget(btn)
        popup = CardPopup(content=box, size_hint=(0.46, 0.42), color=KOLOR_ZIELONY)
        popup.open()

    # ---- SEKCJA: MENU I POPUPY ----

    def otworz_menu(self, inst):
        MenuPopup(self).open()

    def numeric_input_popup(self, label, value, on_validate):
        NumericInputPopup(label, value, on_validate).open()

    # ---- KONTYNUACJA NIŻEJ ----
    # ---- SEKCJA: RESETY, UPDATE, STEROWANIE ----

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def update_sciezki_ikona(self):
        if getattr(self, "sciezki_technologiczne", True):
            if self.nr_przejazdu_do_sciezki == self.ilosc_przejazdow:
                self.ikona_sciezek.source = "sciezki_green.png"
            else:
                self.ikona_sciezek.source = "sciezki_red.png"
        else:
            self.ikona_sciezek.source = "sciezki_green.png"

    def reset_dzienny_start(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self._reset_hold_start = datetime.datetime.now()
            Clock.schedule_once(self._reset_dzienny_popup, 3)
    def reset_dzienny_stop(self, instance, touch):
        self._reset_hold_start = None
        Clock.unschedule(self._reset_dzienny_popup)
    def _reset_dzienny_popup(self, *args):
        if self._reset_hold_start:
            now = datetime.datetime.now()
            if (now - self._reset_hold_start).total_seconds() >= 2.8:
                popup = CardPopup(content=Label(text="[b]RESET = TRZYMAJ 3s[/b]", markup=True, font_size=27, color=KOLOR_CZERWONY),
                                     color=KOLOR_CZERWONY, size_hint=(0.3,0.18))
                popup.open()
                Clock.schedule_once(lambda dt: self.reset_dzienny_ha(popup), 1.3)
    def reset_dzienny_ha(self, popup):
        self.dzienny_ha = 0
        self.lbl_dzienny_ha.text = f"{self.dzienny_ha:.2f}"
        if popup:
            popup.dismiss()

    def set_siewnik_status(self, sieje):
        self.czy_sieje = sieje
        if sieje:
            self._miganie = True
            self.lbl_status_wysiewu.text = "[b]PRACA[/b]"
            self.lbl_status_wysiewu.color = KOLOR_ZIELONY
            self.ostatnie_obroty_walka = datetime.datetime.now()
            if self.sound_beep:
                self.sound_beep.play()
            self.alarms.show_alarm("WYSIEW ROZPOCZĘTY", color=KOLOR_ZIELONY, beep="beep", blocking=False)
            self.nr_przejazdu_do_sciezki = max(0, self.nr_przejazdu_do_sciezki - 1)
            if getattr(self, "sciezki_technologiczne", True):
                self.lbl_sciezki_info.text = f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}"
                self.update_sciezki_ikona()
                if self.nr_przejazdu_do_sciezki == 0:
                    self.alarms.show_alarm("ZAŁĄCZONO ŚCIEŻKĘ", color=KOLOR_ZIELONY, beep="beep", blocking=False)
                    self.nr_przejazdu_do_sciezki = self.ilosc_przejazdow
                    self.lbl_sciezki_info.text = f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}"
                    self.update_sciezki_ikona()
        else:
            self._miganie = False
            self.lbl_status_wysiewu.text = "[b]STOP[/b]"
            self.lbl_status_wysiewu.color = KOLOR_CZERWONY
            if self.sound_beep:
                self.sound_beep.play()

    def migaj_status(self, dt):
        if self.czy_sieje:
            if self.lbl_status_wysiewu.color == KOLOR_ZIELONY:
                self.lbl_status_wysiewu.color = KOLOR_TLO
            else:
                self.lbl_status_wysiewu.color = KOLOR_ZIELONY
        else:
            self.lbl_status_wysiewu.color = KOLOR_CZERWONY

    def sciezki_minus(self, inst):
        if getattr(self, "sciezki_technologiczne", True):
            if self.nr_przejazdu_do_sciezki > 0:
                self.nr_przejazdu_do_sciezki -= 1
                if self.nr_przejazdu_do_sciezki == 0:
                    self.alarms.show_alarm("ZAŁĄCZONO ŚCIEŻKĘ", color=KOLOR_ZIELONY, beep="beep", blocking=False)
                    self.nr_przejazdu_do_sciezki = self.ilosc_przejazdow
            self.lbl_sciezki_info.text = f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}"
            self.update_sciezki_ikona()

    def sciezki_plus(self, inst):
        if getattr(self, "sciezki_technologiczne", True):
            if self.nr_przejazdu_do_sciezki < self.ilosc_przejazdow:
                self.nr_przejazdu_do_sciezki += 1
            self.lbl_sciezki_info.text = f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}"
            self.update_sciezki_ikona()

    # ---- SEKCJA: KAFELKI, WARTOŚCI, OBSŁUGA ----

    def set_dawka_na_ha(self, wartosc, is_zadana=False):
        try:
            self.dawka = float(wartosc)
            self.lbl_dawka.text = f"[b]{int(round(self.dawka))}[/b]"
            if is_zadana:
                self.dawka_zadana = self.dawka
            if not is_zadana and self.tryb_pro:
                self.tryb_pro = False
                self.odswiez_grafike_pro()
                self.zamien_kafelki_pro(False)
        except Exception:
            pass

    def set_obsada_roslin(self, obsada):
        self.obsada_roslin = obsada
        self.lbl_obsada.text = f"[b]{obsada}[/b]"

    def ukryj_obsada_roslin(self):
        self.obsada_roslin = None
        self.lbl_obsada.text = ""

    # ---- SEKCJA: ZAPIS/ODCZYT KONFIGURACJI ----

    def save_config(self):
        self.konfiguracja.zapisz({
            "szerokosc_robocza": self.szerokosc_robocza,
            "liczba_sekcji": self.liczba_sekcji,
            "sekcje_sciezek": self.sekcje_sciezek,
            "ilosc_przejazdow": self.ilosc_przejazdow,
            "nr_przejazdu_do_sciezki": self.nr_przejazdu_do_sciezki,
            "dzienny_ha": self.dzienny_ha,
            "calkowity_ha": self.calkowity_ha,
            "dawka_zadana": self.dawka_zadana,
            "sciezki_technologiczne": self.sciezki_technologiczne  # <-- DODANE!
        })
    def load_config(self):
        cfg = self.konfiguracja.wczytaj()
        self.szerokosc_robocza = float(cfg.get("szerokosc_robocza", 3.0))
        self.liczba_sekcji = int(cfg.get("liczba_sekcji", 21))
        self.sekcje_sciezek = int(cfg.get("sekcje_sciezek", 4))
        self.ilosc_przejazdow = int(cfg.get("ilosc_przejazdow", 5))
        self.nr_przejazdu_do_sciezki = int(cfg.get("nr_przejazdu_do_sciezki", self.ilosc_przejazdow))
        self.dzienny_ha = float(cfg.get("dzienny_ha", 0.0))
        self.calkowity_ha = float(cfg.get("calkowity_ha", 0.0))
        self.dawka_zadana = float(cfg.get("dawka_zadana", 180))
        self.dawka = self.dawka_zadana
        self.sciezki_technologiczne = bool(cfg.get("sciezki_technologiczne", True))  # <-- DODANE!
        self.update_sciezki_ikona()
        self.odswiez_sciezki_box()


    # ---- KONTYNUACJA NIŻEJ ----
    # ---- SEKCJA: UPDATE DANYCH ----

    def update_czas(self, dt):
        now = datetime.datetime.now()
        self.lbl_czas.text = now.strftime("%H:%M    %d.%m.%Y")
        self.predkosc = (self.predkosc + 0.6) % 12.5
        self.lbl_predkosc.text = f"[b]{self.predkosc:.1f}[/b]"

    def update_dzienny_ha(self, dt):
        przyrost = (self.predkosc * self.szerokosc_robocza / 3600) * dt
        self.dzienny_ha += przyrost
        self.calkowity_ha += przyrost
        self.lbl_dzienny_ha.text = f"{self.dzienny_ha:.2f}"
        self.lbl_calkowity_ha.text = f"{self.calkowity_ha:.2f}"
        wydajnosc = self.predkosc * self.szerokosc_robocza
        self.lbl_wydajnosc.text = f"{wydajnosc:.2f}"
        self.lbl_predkosc.text = f"[b]{self.predkosc:.1f}[/b]"
        self.lbl_dawka.text = f"[b]{int(round(self.dawka))}[/b]"

    def steruj_walkiem(self, *args):
        if self.czy_sieje:
            obroty_na_sekunde = self.wylicz_obroty_na_sekunde()
            self.lbl_obroty_walka.text = f"{obroty_na_sekunde:.2f}"
            if not self.silnik_walek_aktywny or abs(self.obroty_silnika - obroty_na_sekunde) > 0.01:
                self.silnik_walek_aktywny = True
                self.obroty_silnika = obroty_na_sekunde
                print(f"[SILNIK WAŁKA] Włączony | Obroty: {obroty_na_sekunde:.2f} /s")
            self.ostatnie_obroty_walka = datetime.datetime.now()
        else:
            self.lbl_obroty_walka.text = "0.00"
            if self.silnik_walek_aktywny:
                print("[SILNIK WAŁKA] Wyłączony")
            self.silnik_walek_aktywny = False
            self.obroty_silnika = 0

    def wylicz_obroty_na_sekunde(self):
        szer = self.szerokosc_robocza
        if getattr(self, "sciezki_technologiczne", True) and self.korekta_dawki_sciezki and self.nr_przejazdu_do_sciezki == 0:
            aktywne = self.liczba_sekcji - self.sekcje_sciezek
            szer = szer * aktywne / self.liczba_sekcji
        v = self.predkosc / 3.6
        ha_na_sekunde = (v * szer) / 10000
        dawka_na_ha_g = self.dawka * 1000
        potrzebne_g_per_s = dawka_na_ha_g * ha_na_sekunde
        obroty_na_sekunde = potrzebne_g_per_s / self.g_per_obrot if self.g_per_obrot else 0
        return max(0, obroty_na_sekunde)

    # ---- ALARMY ----

    def symuluj_alarmy(self, dt):
        if random.randint(0,40)==0:
            self.napiecie -= 0.03
        if random.randint(0,40)==0:
            self.napiecie += 0.02
        self.napiecie = max(11.6, min(13.2, self.napiecie))
        self.lbl_napiecie.text = f"{self.napiecie:.2f}V"

    def check_nasiona_status(self, dt=None):
        if self.nasiona_alarm:
            self.ikona_nasiona.source = "nasiona_red.png"
            if self._nasiona_alarm_popup is None or not self._nasiona_alarm_popup.parent:
                box = BoxLayout(orientation='vertical', spacing=14, padding=20)
                box.add_widget(Label(text="[b]NISKI POZIOM NASION![/b]", markup=True, font_size=32, color=KOLOR_CZERWONY))
                ok_btn = Button(text="OK", font_size=24, background_color=KOLOR_CZERWONY, color=KOLOR_BIALY, size_hint_y=None, height=54)
                box.add_widget(ok_btn)
                self._nasiona_alarm_popup = CardPopup(content=box, color=KOLOR_CZERWONY, size_hint=(0.38, 0.22))
                ok_btn.bind(on_press=self._nasiona_alarm_popup.dismiss)
                self._nasiona_alarm_popup.open()
                if self.sound_beep:
                    self.sound_beep.play()
        else:
            self.ikona_nasiona.source = "nasiona_green.png"
            if self._nasiona_alarm_popup:
                self._nasiona_alarm_popup.dismiss()
                self._nasiona_alarm_popup = None

    def check_alarms(self, dt):
        # NAPIĘCIE
        if self.napiecie < 12.1 and not self.napiecie_alarm:
            self.napiecie_alarm = True
            if self._napiecie_alarm_popup is None or not self._napiecie_alarm_popup.parent:
                box = BoxLayout(orientation='vertical', spacing=14, padding=20)
                box.add_widget(Label(text="[b]ZANIK NAPIĘCIA! (<12.1V)[/b]", markup=True, font_size=32, color=KOLOR_CZERWONY))
                ok_btn = Button(text="OK", font_size=24, background_color=KOLOR_CZERWONY, color=KOLOR_BIALY, size_hint_y=None, height=54)
                box.add_widget(ok_btn)
                self._napiecie_alarm_popup = CardPopup(content=box, color=KOLOR_CZERWONY, size_hint=(0.38, 0.22))
                ok_btn.bind(on_press=self._napiecie_alarm_popup.dismiss)
                self._napiecie_alarm_popup.open()
                if self.sound_alarm:
                    self.sound_alarm.play()
        if self.napiecie >= 12.2 and self.napiecie_alarm:
            self.napiecie_alarm = False
            if self._napiecie_alarm_popup:
                self._napiecie_alarm_popup.dismiss()
                self._napiecie_alarm_popup = None
        # WAŁEK (brak sygnału obrotów >3s gdy sieje)
        diff = (datetime.datetime.now() - self.ostatnie_obroty_walka).total_seconds()
        if self.czy_sieje and diff > 3 and not self.obroty_walka_alarm:
            self.obroty_walka_alarm = True
            if self._obroty_alarm_popup is None or not self._obroty_alarm_popup.parent:
                box = BoxLayout(orientation='vertical', spacing=14, padding=20)
                box.add_widget(Label(text="[b]ZANIK OBROTÓW WAŁKA![/b]", markup=True, font_size=32, color=KOLOR_CZERWONY))
                ok_btn = Button(text="OK", font_size=24, background_color=KOLOR_CZERWONY, color=KOLOR_BIALY, size_hint_y=None, height=54)
                box.add_widget(ok_btn)
                self._obroty_alarm_popup = CardPopup(content=box, color=KOLOR_CZERWONY, size_hint=(0.38, 0.22))
                ok_btn.bind(on_press=self._obroty_alarm_popup.dismiss)
                self._obroty_alarm_popup.open()
                if self.sound_alarm:
                    self.sound_alarm.play()
        if (not self.czy_sieje or diff < 2) and self.obroty_walka_alarm:
            self.obroty_walka_alarm = False
            if self._obroty_alarm_popup:
                self._obroty_alarm_popup.dismiss()
                self._obroty_alarm_popup = None

# ---- KONIEC KLASY ----



# ---- KONIEC KLASY ----

# do wylaczania sciezek
def odswiez_sciezki_box(self):

    if self.sciezki_box and self.sciezki_box.parent:
        self.remove_widget(self.sciezki_box)
    if self.sciezki_technologiczne:
        sciezki_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=52, spacing=10, padding=[0, 6, 0, 0])
        self.btn_sciezki_minus = Button(text="ODEJMIJ PRZEJAZD", font_size=19, background_color=KOLOR_ZIELONY,
                                        color=KOLOR_BIALY, size_hint_x=0.33)
        self.btn_sciezki_minus.bind(on_press=self.sciezki_minus)
        sciezki_box.add_widget(self.btn_sciezki_minus)
        self.lbl_sciezki_info = Label(text=f"DO ŚCIEŻKI: {self.nr_przejazdu_do_sciezki}", font_size=40,
                                      color=KOLOR_BIALY, size_hint_x=0.34, halign="center")
        self.lbl_sciezki_info.bind(size=lambda s, *a: setattr(s, 'text_size', s.size))
        sciezki_box.add_widget(self.lbl_sciezki_info)
        self.btn_sciezki_plus = Button(text="DODAJ PRZEJAZD", font_size=19, background_color=KOLOR_ZIELONY,
                                       color=KOLOR_BIALY, size_hint_x=0.33)
        self.btn_sciezki_plus.bind(on_press=self.sciezki_plus)
        sciezki_box.add_widget(self.btn_sciezki_plus)
        self.add_widget(sciezki_box, index=4)  # index=4 = przed przyciskiem PRÓBA KRĘCONA
        self.sciezki_box = sciezki_box
    else:
        self.sciezki_box = None




class MenuPopup(CardPopup):
    def __init__(self, root):
        self.root = root
        main = BoxLayout(orientation='vertical', spacing=18, padding=20)
        main.add_widget(Label(text="[b]MENU[/b]", markup=True, font_size=32, color=KOLOR_NIEBIESKI))
        btn_tryb = Button(
            text="Tryb Ekspert" if self.root.tryb_pro else "Tryb PRO",
            font_size=25,
            background_color=KOLOR_ZIELONY,
            color=KOLOR_BIALY,
            size_hint_y=None,
            height=54
        )
        btn_tryb.bind(on_press=self.przelacz_tryb)
        main.add_widget(btn_tryb)
        btn_ustawienia = Button(text="Ustawienia siewnika", font_size=25, background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY, size_hint_y=None, height=54)
        btn_ustawienia.bind(on_press=self.otworz_ustawienia)
        main.add_widget(btn_ustawienia)

        main.add_widget(Label(text="--- TESTY SERWISOWE ---", font_size=17, color=KOLOR_NIEBIESKI))

        btn_test_silnik = Button(text="Test silnika wałka", font_size=21, background_color=KOLOR_BIALY, color=KOLOR_NIEBIESKI, size_hint_y=None, height=44)
        btn_test_silnik.bind(on_press=lambda x: self.root.test_silnik())
        main.add_widget(btn_test_silnik)

        btn_test_silownik = Button(text="Test siłownika ścieżek", font_size=21, background_color=KOLOR_BIALY, color=KOLOR_NIEBIESKI, size_hint_y=None, height=44)
        btn_test_silownik.bind(on_press=lambda x: self.root.test_silownik_sciezki())
        main.add_widget(btn_test_silownik)

        btn_test_czujnik = Button(text="Test czujnika opuszczenia", font_size=21, background_color=KOLOR_BIALY, color=KOLOR_NIEBIESKI, size_hint_y=None, height=44)
        btn_test_czujnik.bind(on_press=lambda x: self.root.test_czujnik_opuszczenia())
        main.add_widget(btn_test_czujnik)

        btn_test_predkosc = Button(text="Test prędkości", font_size=21, background_color=KOLOR_BIALY, color=KOLOR_NIEBIESKI, size_hint_y=None, height=44)
        btn_test_predkosc.bind(on_press=lambda x: self.root.test_predkosc())
        main.add_widget(btn_test_predkosc)

        btn_korekta = Button(
            text=f'Korekta dawki przy ścieżkach: {"ON" if self.root.korekta_dawki_sciezki else "OFF"}',
            font_size=18, background_color=KOLOR_BIALY, color=KOLOR_NIEBIESKI)
        btn_korekta.bind(on_press=self.toggle_korekta_sciezek)
        main.add_widget(btn_korekta)

        btn_close = Button(text="Zamknij", font_size=22, background_color=KOLOR_CIEMNY, color=KOLOR_BIALY, size_hint_y=None, height=46)
        btn_close.bind(on_press=self.dismiss)
        main.add_widget(btn_close)

        super().__init__(content=main, size_hint=(0.56,0.92), color=KOLOR_NIEBIESKI)

    def przelacz_tryb(self, inst):
        self.root.tryb_pro = not self.root.tryb_pro
        print(f"[MenuPopup] Tryb PRO: {self.root.tryb_pro}")
        self.root.odswiez_grafike_pro()
        self.root.zamien_kafelki_pro(self.root.tryb_pro)
        self.dismiss()
    def tryb_pro(self, inst):
        self.dismiss()
        self.root.otworz_pro_popup()
    def otworz_ustawienia(self, inst):
        self.dismiss()
        UstawieniaSiewnikaPopup(self.root).open()
    def toggle_korekta_sciezek(self, inst):
        self.root.korekta_dawki_sciezki = not self.root.korekta_dawki_sciezki
        inst.text = f'Korekta dawki przy ścieżkach: {"ON" if self.root.korekta_dawki_sciezki else "OFF"}'



class KafelekUstawien(BoxLayout):
    def __init__(self, label, value, on_click, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=75, padding=[0, 0, 0, 0], **kwargs)
        with self.canvas.before:
            Color(*KOLOR_KARTY)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            Color(*KOLOR_NIEBIESKI)
            self.obram = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 18], width=2)
        self.bind(pos=self.update_bg, size=self.update_bg)
        btn = Button(
            text=f"{label}\n[b]{value}[/b]",
            markup=True,
            font_size=22,
            halign='center',
            valign='middle',
            background_color=(0, 0, 0, 0),  # przezroczyste, bo tło maluje canvas
            color=KOLOR_NIEBIESKI,
            size_hint=(1, 1),
            background_normal='',
            border=(0, 0, 0, 0),
        )
        btn.bind(on_press=on_click)
        self.btn = btn
        self.add_widget(btn)
    def update_bg(self, *a):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.obram.rounded_rectangle = [self.pos[0], self.pos[1], self.size[0], self.size[1], 18]

    def set_value(self, label, value):
        self.btn.text = f"{label}\n[b]{value}[/b]"

from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock

class UstawieniaSiewnikaPopup(CardPopup):
    def __init__(self, root):
        self.root = root
        self.root.nr_przejazdu_do_sciezki = self.root.ilosc_przejazdow
        self.temp_config = {
            "szerokosc_robocza": float(root.szerokosc_robocza),
            "liczba_sekcji": int(root.liczba_sekcji),
            "sekcje_sciezek": int(root.sekcje_sciezek),
            "ilosc_przejazdow": int(root.ilosc_przejazdow),
            "sciezki_technologiczne": root.sciezki_technologiczne,
        }
        main = BoxLayout(orientation='vertical', spacing=14, padding=[26, 22, 26, 22])
        self.kafelki = {}
        parametry = [
            ("Szerokość robocza (m)", "szerokosc_robocza", 'float'),
            ("Liczba sekcji", "liczba_sekcji", 'int'),
            ("Sekcje ścieżek", "sekcje_sciezek", 'int'),
            ("Ilość przejazdów do ścieżki", "ilosc_przejazdow", 'int'),
        ]
        for label, key, input_filter in parametry:
            kafelek = KafelekUstawien(
                label, self.temp_config[key],
                on_click=lambda btn, k=key, l=label, f=input_filter: self.zmien_wartosc(k, l, f)
            )
            self.kafelki[key] = kafelek
            main.add_widget(kafelek)

        # Dodaj checkbox dla ścieżek technologicznych
        box_sciezki = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, padding=[10,0])
        self.checkbox_sciezki = CheckBox(active=self.temp_config["sciezki_technologiczne"])
        box_sciezki.add_widget(self.checkbox_sciezki)
        box_sciezki.add_widget(Label(text="Ścieżki technologiczne", font_size=20, color=KOLOR_NIEBIESKI))
        main.add_widget(box_sciezki)

        # g/obrót – tylko do podglądu
        main.add_widget(Label(
            text=f"[b]g/obrót wałka:[/b] {self.root.g_per_obrot:.2f}",
            markup=True, font_size=20, color=KOLOR_NIEBIESKI,
            size_hint_y=None, height=38, halign="center"
        ))

        btns = BoxLayout(orientation='horizontal', spacing=14, size_hint_y=None, height=54)
        btn_save = Button(
            text="Zapisz", font_size=22,
            background_color=KOLOR_NIEBIESKI, color=KOLOR_BIALY,
            background_normal='', border=(0,0,0,0)
        )
        btn_save.bind(on_press=self.save)
        btn_close = Button(
            text="Anuluj", font_size=21,
            background_color=KOLOR_CIEMNY, color=KOLOR_BIALY,
            background_normal='', border=(0,0,0,0)
        )
        btn_close.bind(on_press=self.dismiss)
        btns.add_widget(btn_save)
        btns.add_widget(btn_close)
        main.add_widget(btns)

        super().__init__(content=main, size_hint=(0.58, 0.82), color=KOLOR_NIEBIESKI)

    def zmien_wartosc(self, key, label, input_filter):
        def on_ok(wartosc):
            if input_filter == 'int':
                try:
                    wartosc = int(float(wartosc))
                except Exception:
                    wartosc = 0
            else:
                try:
                    wartosc = float(str(wartosc).replace(',','.'))
                except Exception:
                    wartosc = 0.0
            self.temp_config[key] = wartosc
            self.kafelki[key].set_value(label, wartosc)
        NumericInputPopup(
            label=label,
            value=self.temp_config[key],
            on_validate=on_ok,
            input_filter=input_filter
        ).open()

    def save(self, inst):
        try:
            self.root.szerokosc_robocza = float(self.temp_config["szerokosc_robocza"])
            self.root.liczba_sekcji = int(self.temp_config["liczba_sekcji"])
            self.root.sekcje_sciezek = int(self.temp_config["sekcje_sciezek"])
            nowa_ilosc = int(self.temp_config["ilosc_przejazdow"])
            self.root.ilosc_przejazdow = nowa_ilosc
            self.root.nr_przejazdu_do_sciezki = nowa_ilosc
            self.root.sciezki_technologiczne = self.checkbox_sciezki.active
            self.root.save_config()
            self.root.odswiez_sciezki_box()
            self.root.update_ikona_sciezek_visibility()
            self.dismiss()
            Clock.schedule_once(lambda dt: self.root.lbl_sciezki_info.setter('text')(
                self.root.lbl_sciezki_info, f"DO ŚCIEŻKI: {self.root.nr_przejazdu_do_sciezki}"
            ), 0.05)
        except Exception as e:
            AlarmManager(self.root).show_alarm("Błąd zapisu ustawień!", color=KOLOR_CZERWONY, beep="alarm")





class SiewnikApp(App):
    def build(self):
        return MainScreen()
    def on_stop(self):
        if hasattr(self, "root") and hasattr(self.root, "save_config"):
            self.root.save_config()
    def on_start(self):
        Window.bind(on_key_down=self.on_key_down)
    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if not hasattr(self, 'root') or not self.root:
            return
        if codepoint == "+":
            self.root.predkosc = min(50, self.root.predkosc + 1)
        elif codepoint == "-":
            self.root.predkosc = max(0, self.root.predkosc - 1)
        elif key == 27:  # ESC
            self.stop()

if __name__ == "__main__":
    SiewnikApp().run()

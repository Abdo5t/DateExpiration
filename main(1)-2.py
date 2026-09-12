"""DateExpirationApp - modern Kivy interface.

Keep this file beside the existing assets/ folder:
    assets/Co.png
    assets/LHP.png
    assets/LBEN.png
    assets/LAF.png
"""

from datetime import date, datetime, timedelta
from pathlib import Path
import calendar
import json

import kivy
kivy.require("2.0.0")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget

try:
    from plyer import notification
except ImportError:
    notification = None

try:
    from android.permissions import Permission, request_permissions
except ImportError:
    Permission = None
    request_permissions = None


# ---------------------------------------------------------------------------
# App data
# ---------------------------------------------------------------------------

DUREES = {"LHP": 5, "LBEN": 20, "LAF": 30}
NOMS = {
    "LHP": "Lait pasteurisé",
    "LBEN": "Lben",
    "LAF": "Lait à fermentation",
}

JOURS = [
    "Lundi", "Mardi", "Mercredi", "Jeudi",
    "Vendredi", "Samedi", "Dimanche",
]
MOIS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]
CODES_MOIS = [
    "JAN", "FEV", "MAR", "AVR", "MAI", "JUN",
    "JUL", "AOU", "SEP", "OCT", "NOV", "DEC",
]

GREEN_DARK = (0.015, 0.20, 0.13, 1)
GREEN = (0.02, 0.40, 0.24, 1)
GREEN_SOFT = (0.82, 0.95, 0.87, 1)
MINT = (0.91, 0.98, 0.93, 1)
INK = (0.07, 0.13, 0.15, 1)
MUTED = (0.39, 0.46, 0.46, 1)
WHITE = (1, 1, 1, 1)
LIGHT = (0.95, 0.97, 0.96, 1)
RED_SOFT = (1.0, 0.92, 0.90, 1)
RED = (0.75, 0.18, 0.12, 1)
ASSETS = Path(__file__).resolve().parent / "assets"
REMINDER_INTERVAL = 30 * 60


def expiration(product, extra=0, production=None):
    production = production or date.today()
    if isinstance(production, datetime):
        production = production.date()
    return production + timedelta(days=DUREES[product] - 1 + extra)


def printable_code(product, extra=0, production=None):
    """Return the original product code format used by the app."""
    if product not in DUREES:
        return "Nom de produit inconnu"
    production = production or date.today()
    result = expiration(product, extra, production)
    weekday_code = JOURS[production.weekday()][:2].upper()
    return f"{product} : {result.day} {CODES_MOIS[result.month - 1]} {weekday_code}"


def long_date(value):
    return f"{value.day} {MOIS[value.month - 1]} {value.year}"


# ---------------------------------------------------------------------------
# Reusable modern widgets
# ---------------------------------------------------------------------------

class Card(BoxLayout):
    fill = ListProperty(WHITE)
    radius = ListProperty([dp(20)])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # A very light shadow makes the cards stand out on a phone screen.
            self.shadow_color = Color(0.02, 0.10, 0.07, 0.08)
            self.shadow = RoundedRectangle(
                pos=(self.x, self.y - dp(2)),
                size=self.size,
                radius=self.radius,
            )
            self.background_color = Color(*self.fill)
            self.shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=self.radius,
            )
        self.bind(pos=self.redraw, size=self.redraw, fill=self.redraw, radius=self.redraw)

    def redraw(self, *_):
        self.shadow.pos = (self.x, self.y - dp(2))
        self.shadow.size = self.size
        self.shadow.radius = self.radius
        self.background_color.rgba = self.fill
        self.shape.pos = self.pos
        self.shape.size = self.size
        self.shape.radius = self.radius


class ModernButton(Button):
    fill = ListProperty(GREEN)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        kwargs.setdefault("font_size", sp(15))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("color", WHITE)
        super().__init__(
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            **kwargs,
        )
        with self.canvas.before:
            self.paint = Color(*self.fill)
            self.shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(13)],
            )
        self.bind(
            pos=self.redraw,
            size=self.redraw,
            fill=self.redraw,
            state=self.redraw,
            disabled=self.redraw,
        )

    def redraw(self, *_):
        rgba = list(self.fill)
        if self.state == "down":
            rgba[:3] = [value * 0.84 for value in rgba[:3]]
        if self.disabled:
            rgba[3] = 0.35
        self.paint.rgba = rgba
        self.shape.pos = self.pos
        self.shape.size = self.size


def text_label(
    text="",
    height=28,
    size=15,
    color=INK,
    bold=False,
    align="left",
):
    item = Label(
        text=text,
        size_hint_y=None,
        height=dp(height),
        font_size=sp(size),
        color=color,
        bold=bold,
        halign=align,
        valign="middle",
    )
    item.bind(size=lambda obj, value: setattr(obj, "text_size", value))
    return item


def card_column(fill=WHITE, padding=16, spacing=10):
    item = Card(
        orientation="vertical",
        size_hint_y=None,
        padding=dp(padding),
        spacing=dp(spacing),
        fill=fill,
    )
    item.bind(minimum_height=item.setter("height"))
    return item


class ProductChoice(BoxLayout):
    def __init__(self, code, callback, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(76),
            spacing=dp(4),
            **kwargs,
        )
        self.code = code
        self.button = ModernButton(text=code, height=dp(48))
        self.caption = text_label(
            f"{DUREES[code]} jours",
            height=20,
            size=11,
            color=MUTED,
            align="center",
        )
        self.button.bind(on_release=lambda *_: callback(code))
        self.add_widget(self.button)
        self.add_widget(self.caption)

    def set_selected(self, selected):
        self.button.fill = GREEN if selected else LIGHT
        self.button.color = WHITE if selected else INK
        self.button.text = f"✓  {self.code}" if selected else self.code


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class DateExpirationApp(App):
    def build(self):
        self.title = "Colaimo • Date d'expiration"
        Window.clearcolor = (0.94, 0.96, 0.95, 1)

        self.product = "LHP"
        self.extra = 0
        self.production = date.today()
        self.history = self.load_history()
        self.reminder_event = None

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        page = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=(dp(16), dp(18)),
            spacing=dp(15),
        )
        page.bind(minimum_height=page.setter("height"))
        scroll.add_widget(page)

        # Header -------------------------------------------------------------
        header = Card(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(104),
            padding=dp(14),
            spacing=dp(12),
            fill=GREEN_DARK,
        )
        logo = Image(
            source=str(ASSETS / "Co.png"),
            size_hint_x=None,
            width=dp(76),
            allow_stretch=True,
            keep_ratio=True,
        )
        header.add_widget(logo)
        header_text = BoxLayout(orientation="vertical", spacing=dp(2))
        header_text.add_widget(text_label("Date d'expiration", 38, 23, WHITE, True))
        header_text.add_widget(text_label("Calcul rapide de vos produits", 26, 13, GREEN_SOFT))
        header_text.add_widget(text_label("Simple  •  Rapide  •  Fiable", 22, 11, (0.72, 0.88, 0.78, 1)))
        header.add_widget(header_text)
        history_button = ModernButton(
            text="Historique",
            fill=WHITE,
            color=GREEN_DARK,
            size_hint_x=None,
            width=dp(94),
            height=dp(42),
            font_size=sp(11),
        )
        history_button.bind(on_release=self.open_history)
        header.add_widget(history_button)
        page.add_widget(header)

        # Production monitoring reminder -----------------------------------
        reminder = Card(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(82),
            padding=dp(12),
            spacing=dp(9),
            fill=GREEN_SOFT,
        )
        reminder_text = BoxLayout(orientation="vertical", spacing=dp(1))
        reminder_text.add_widget(text_label(
            "Surveillance de la production",
            27,
            14,
            GREEN_DARK,
            True,
        ))
        self.reminder_status = text_label(
            "Rappel désactivé",
            24,
            11,
            MUTED,
        )
        reminder_text.add_widget(self.reminder_status)
        reminder_text.add_widget(text_label(
            "Notification toutes les 30 minutes",
            20,
            10,
            MUTED,
        ))
        reminder.add_widget(reminder_text)

        self.reminder_switch = Switch(active=False, size_hint_x=None, width=dp(52))
        self.reminder_switch.bind(active=self.on_reminder_toggle)
        reminder.add_widget(self.reminder_switch)

        test_reminder = ModernButton(
            text="Tester",
            fill=WHITE,
            color=GREEN_DARK,
            size_hint_x=None,
            width=dp(66),
            height=dp(42),
            font_size=sp(10),
        )
        test_reminder.bind(on_release=self.test_reminder)
        reminder.add_widget(test_reminder)
        page.add_widget(reminder)

        # Product and inputs card -------------------------------------------
        form = card_column(fill=WHITE, padding=16, spacing=10)
        form.add_widget(text_label("1  •  Choisissez un produit", 28, 16, GREEN_DARK, True))

        products = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(76))
        self.product_choices = {}
        for code in DUREES:
            choice = ProductChoice(code, self.select_product)
            self.product_choices[code] = choice
            products.add_widget(choice)
        form.add_widget(products)

        product_info = BoxLayout(size_hint_y=None, height=dp(76), spacing=dp(12))
        self.product_image = Image(
            size_hint_x=None,
            width=dp(74),
            allow_stretch=True,
            keep_ratio=True,
        )
        product_info.add_widget(self.product_image)
        self.product_name = text_label("", 76, 19, INK, True)
        product_info.add_widget(self.product_name)
        form.add_widget(product_info)

        form.add_widget(text_label("2  •  Date de production", 28, 16, GREEN_DARK, True))
        self.date_button = ModernButton(fill=LIGHT, color=INK, height=dp(52))
        self.date_button.bind(on_release=self.open_calendar)
        form.add_widget(self.date_button)

        form.add_widget(text_label("3  •  Jours supplémentaires", 28, 16, GREEN_DARK, True))
        stepper = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(9))
        self.minus = ModernButton(text="−", fill=LIGHT, color=INK, font_size=sp(23))
        self.counter = text_label("0", 52, 22, GREEN_DARK, True, "center")
        self.plus = ModernButton(text="+", fill=LIGHT, color=INK, font_size=sp(23))
        self.minus.bind(on_release=lambda *_: self.change_extra(-1))
        self.plus.bind(on_release=lambda *_: self.change_extra(1))
        stepper.add_widget(self.minus)
        stepper.add_widget(self.counter)
        stepper.add_widget(self.plus)
        form.add_widget(stepper)

        self.extra_hint = text_label("", 28, 11, MUTED, align="center")
        form.add_widget(self.extra_hint)

        actions = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(9))
        calculate = ModernButton(text="Calculer la date", height=dp(54), font_size=sp(16))
        reset = ModernButton(text="Réinitialiser", fill=LIGHT, color=INK, height=dp(54), font_size=sp(13))
        calculate.bind(on_release=self.calculate)
        reset.bind(on_release=self.reset)
        actions.add_widget(calculate)
        actions.add_widget(reset)
        form.add_widget(actions)
        page.add_widget(form)

        # Result card --------------------------------------------------------
        result = card_column(fill=MINT, padding=17, spacing=5)
        result.add_widget(text_label("RÉSULTAT", 24, 13, GREEN, True, "center"))
        self.result_date = text_label("À calculer", 58, 27, GREEN_DARK, True, "center")
        self.result_day = text_label("", 26, 16, GREEN, True, "center")
        result.add_widget(self.result_date)
        result.add_widget(self.result_day)
        result.add_widget(text_label("Code à imprimer", 24, 12, MUTED, False, "center"))
        self.result_code = text_label("—", 40, 22, GREEN_DARK, True, "center")
        result.add_widget(self.result_code)
        result.add_widget(text_label(
            "Les deux dernières lettres indiquent le jour de production.",
            32,
            10,
            MUTED,
            False,
            "center",
        ))
        page.add_widget(result)

        self.summary = text_label(
            "Choisissez les paramètres, puis calculez.",
            34,
            11,
            MUTED,
            False,
            "center",
        )
        page.add_widget(self.summary)

        self.select_product("LHP")
        return scroll

    def on_start(self):
        """Request notification permission on Android when available."""
        if request_permissions is None or Permission is None:
            return
        permission = getattr(
            Permission,
            "POST_NOTIFICATIONS",
            "android.permission.POST_NOTIFICATIONS",
        )
        try:
            request_permissions([permission])
        except Exception:
            # Older Android versions do not expose this runtime permission.
            pass

    def on_reminder_toggle(self, _switch, active):
        """Start or stop the 30-minute production monitoring reminder."""
        if active:
            if self.reminder_event is None:
                self.reminder_event = Clock.schedule_interval(
                    self.send_production_reminder,
                    REMINDER_INTERVAL,
                )
            self.reminder_status.text = "Rappel activé — toutes les 30 minutes"
            self.reminder_status.color = GREEN
        else:
            if self.reminder_event is not None:
                self.reminder_event.cancel()
                self.reminder_event = None
            self.reminder_status.text = "Rappel désactivé"
            self.reminder_status.color = MUTED

    def test_reminder(self, *_):
        """Send one immediate reminder so the user can test notifications."""
        self.send_production_reminder(0)

    def send_production_reminder(self, _dt):
        title = "Surveillance de la production"
        message = "Il est temps de vérifier la progression de la production."
        if notification is not None:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name=self.title,
                    timeout=10,
                )
                return
            except Exception:
                pass
        self.show_message_popup(title, message)

    def on_stop(self):
        if self.reminder_event is not None:
            self.reminder_event.cancel()
            self.reminder_event = None

    @staticmethod
    def show_message_popup(title, message):
        popup = Popup(
            title=title,
            content=text_label(message, 70, 15, INK, False, "center"),
            size_hint=(0.86, None),
            height=dp(210),
        )
        popup.open()

    def reset(self, *_):
        self.product = "LHP"
        self.extra = 0
        self.production = date.today()
        self.select_product("LHP")

    @property
    def history_file(self):
        return Path(self.user_data_dir) / "date_expiration_history.json"

    def load_history(self):
        try:
            if not self.history_file.exists():
                return []
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, ValueError, TypeError):
            return []

    def save_history(self):
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.write_text(
                json.dumps(self.history, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            # The calculator still works if the device refuses file storage.
            pass

    def add_to_history(self, product, extra, production, result):
        entry = {
            "product": product,
            "production": production.isoformat(),
            "expiration": result.isoformat(),
            "code": printable_code(product, extra, production),
        }
        if self.history and self.history[0] == entry:
            return
        self.history.insert(0, entry)
        self.history = self.history[:20]
        self.save_history()

    def open_history(self, *_):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(9))
        history_scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        history_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
        )
        history_list.bind(minimum_height=history_list.setter("height"))
        history_scroll.add_widget(history_list)
        content.add_widget(history_scroll)

        footer = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        clear = ModernButton(text="Effacer", fill=RED_SOFT, color=RED, font_size=sp(12))
        close = ModernButton(text="Fermer", fill=LIGHT, color=INK, font_size=sp(12))
        footer.add_widget(clear)
        footer.add_widget(close)
        content.add_widget(footer)

        popup = Popup(
            title="Historique des calculs",
            content=content,
            size_hint=(0.95, 0.88),
            auto_dismiss=False,
        )

        def display_date(raw):
            try:
                return long_date(date.fromisoformat(raw))
            except (TypeError, ValueError):
                return raw

        def render_history(*_):
            history_list.clear_widgets()
            if not self.history:
                history_list.add_widget(text_label(
                    "Aucun calcul enregistré pour le moment.",
                    height=60,
                    size=14,
                    color=MUTED,
                    align="center",
                ))
                return
            for entry in self.history:
                product = entry.get("product", "")
                item = Card(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(86),
                    padding=dp(10),
                    spacing=dp(2),
                    fill=LIGHT,
                )
                item.add_widget(text_label(
                    f"{product}  •  {NOMS.get(product, product)}",
                    height=23,
                    size=14,
                    color=GREEN_DARK,
                    bold=True,
                ))
                item.add_widget(text_label(
                    f"Production : {display_date(entry.get('production'))}",
                    height=21,
                    size=11,
                    color=INK,
                ))
                item.add_widget(text_label(
                    f"Expiration : {display_date(entry.get('expiration'))}  •  {entry.get('code', '—')}",
                    height=22,
                    size=11,
                    color=MUTED,
                ))
                history_list.add_widget(item)

        def clear_history(*_):
            self.history = []
            self.save_history()
            render_history()

        clear.bind(on_release=clear_history)
        close.bind(on_release=popup.dismiss)
        render_history()
        popup.open()

    def invalidate(self):
        self.result_date.text = "À calculer"
        self.result_day.text = ""
        self.result_code.text = "—"
        self.summary.text = "Choisissez les paramètres, puis calculez."

    def select_product(self, product):
        self.product = product
        self.extra = 0
        for code, choice in self.product_choices.items():
            choice.set_selected(code == product)
        self.product_image.source = str(ASSETS / f"{product}.png")
        self.product_name.text = NOMS[product]
        self.refresh_inputs()
        self.invalidate()

    def refresh_inputs(self):
        self.date_button.text = f"{long_date(self.production)}    ›"
        self.counter.text = str(self.extra)
        self.minus.disabled = self.product != "LHP" or self.extra == 0
        self.plus.disabled = self.product != "LHP" or self.extra == 1
        if self.product == "LHP":
            self.extra_hint.text = "LHP : vous pouvez ajouter 0 ou 1 jour."
        else:
            self.extra_hint.text = "Aucun jour supplémentaire pour ce produit."

    def change_extra(self, delta):
        if self.product == "LHP":
            self.extra = max(0, min(1, self.extra + delta))
        self.refresh_inputs()
        self.invalidate()

    def calculate(self, *_):
        values = (self.product, self.extra, self.production)
        if self.product == "LHP" and self.extra == 1:
            content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
            content.add_widget(text_label(
                "Ajouter 1 jour à la date\nd'expiration de LHP ?",
                68,
                17,
                WHITE,
                True,
                "center",
            ))
            buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(9))
            cancel = ModernButton(text="Annuler", fill=LIGHT, color=INK)
            confirm = ModernButton(text="Confirmer")
            buttons.add_widget(cancel)
            buttons.add_widget(confirm)
            content.add_widget(buttons)
            popup = Popup(
                title="Confirmation",
                content=content,
                size_hint=(0.92, None),
                height=dp(235),
                auto_dismiss=False,
            )

            def cancel_extra(*_):
                self.extra = 0
                self.refresh_inputs()
                self.invalidate()
                popup.dismiss()

            def accept(*_):
                self.show_result(*values)
                popup.dismiss()

            cancel.bind(on_release=cancel_extra)
            confirm.bind(on_release=accept)
            popup.open()
        else:
            self.show_result(*values)

    def show_result(self, product, extra, production):
        result = expiration(product, extra, production)
        self.result_date.text = long_date(result)
        self.result_day.text = JOURS[result.weekday()]
        self.result_code.text = printable_code(product, extra, production)
        self.add_to_history(product, extra, production, result)
        self.summary.text = (
            f"{product}  •  Production : {long_date(production)}  •  +{extra} jour"
        )
        Clock.schedule_once(lambda *_: setattr(self.root, "scroll_y", 0), 0.05)

    def open_calendar(self, *_):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(9))
        navigation = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        previous = ModernButton(text="‹", size_hint_x=0.18, height=dp(44))
        month_title = text_label("", 44, 16, WHITE, True, "center")
        following = ModernButton(text="›", size_hint_x=0.18, height=dp(44))
        navigation.add_widget(previous)
        navigation.add_widget(month_title)
        navigation.add_widget(following)
        content.add_widget(navigation)

        grid = GridLayout(cols=7, spacing=dp(3))
        content.add_widget(grid)

        footer = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        today = ModernButton(text="Aujourd'hui")
        close = ModernButton(text="Annuler", fill=LIGHT, color=INK)
        footer.add_widget(today)
        footer.add_widget(close)
        content.add_widget(footer)

        popup = Popup(
            title="Date de production",
            content=content,
            size_hint=(0.94, 0.90),
        )
        shown = [self.production.year, self.production.month]

        def choose(value):
            self.production = value
            self.refresh_inputs()
            self.invalidate()
            popup.dismiss()

        def render(*_):
            year, month = shown
            month_title.text = f"{MOIS[month - 1].capitalize()} {year}"
            grid.clear_widgets()
            for day_name in ("L", "M", "M", "J", "V", "S", "D"):
                grid.add_widget(Label(text=day_name, color=WHITE, font_size=sp(13)))
            for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
                for day_number in week:
                    if not day_number:
                        grid.add_widget(Widget())
                        continue
                    value = date(year, month, day_number)
                    selected = value == self.production
                    button = ModernButton(
                        text=str(day_number),
                        size_hint_y=1,
                        font_size=sp(14),
                        fill=GREEN if selected else LIGHT,
                        color=WHITE if selected else INK,
                    )
                    button.bind(on_release=lambda _, chosen=value: choose(chosen))
                    grid.add_widget(button)

        def move(delta):
            index = shown[0] * 12 + shown[1] - 1 + delta
            year, month = divmod(index, 12)
            if 1 <= year <= 9999:
                shown[:] = [year, month + 1]
                render()

        previous.bind(on_release=lambda *_: move(-1))
        following.bind(on_release=lambda *_: move(1))
        today.bind(on_release=lambda *_: choose(date.today()))
        close.bind(on_release=popup.dismiss)
        render()
        popup.open()


if __name__ == "__main__":
    DateExpirationApp().run()

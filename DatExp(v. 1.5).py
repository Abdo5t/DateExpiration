from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.image import FitImage
from datetime import datetime, timedelta
from kivy.core.window import Window
from kivy.metrics import dp

Window.size = (360, 640)

def calculer_date_expiration(nom_produit: str) -> str:
    durees = {
        "LHP": 5,
        "LEBEN": 20,
        "LAF": 30
    }

    if nom_produit not in durees:
        return "Nom de produit inconnu"

    date_production = datetime.now()
    date_expiration = date_production + timedelta(days=durees[nom_produit] - 1)

    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_latins = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]

    jour_production = jours_fr[date_production.weekday()]
    mois_expiration = mois_latins[date_expiration.month - 1]

    return f"{nom_produit} : {date_expiration.day} {mois_expiration} {jour_production[:2].upper()}"

class ExpirationApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Light"

        self.selected_product = None

        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # Logo
        logo = FitImage(source='assets/Co.png', size_hint=(1, None), height=dp(150))
        layout.add_widget(logo)

        # Title
        layout.add_widget(MDLabel(
            text="Calcul de la date d'expiration",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        ))

        # Menu de sélection
        items = ["LHP", "LEBEN", "LAF"]
        menu_items = [
            {"text": i, "on_release": lambda x=i: self.set_item(x)} for i in items
        ]
        self.menu = MDDropdownMenu(
            caller=None,
            items=menu_items,
            width_mult=4,
        )

        self.product_button = MDRaisedButton(
            text="Sélectionner le produit",
            pos_hint={"center_x": 0.5},
            on_release=self.open_menu
        )
        layout.add_widget(self.product_button)

        # Button Calcul
        calc_button = MDRaisedButton(
            text="Calculer",
            pos_hint={"center_x": 0.5},
            md_bg_color=self.theme_cls.primary_color,
            on_release=self.calculer
        )
        layout.add_widget(calc_button)

        # Result
        self.result_label = MDLabel(
            text="",
            halign="center",
            font_style="H6",
            theme_text_color="Custom",
            text_color=(0, 0, 1, 1)
        )
        layout.add_widget(self.result_label)

        return layout

    def open_menu(self, instance):
        self.menu.caller = instance
        self.menu.open()

    def set_item(self, text_item):
        self.selected_product = text_item
        self.product_button.text = text_item
        self.menu.dismiss()

    def calculer(self, instance):
        if not self.selected_product:
            self.show_dialog("Erreur", "Veuillez sélectionner un produit.")
        else:
            result = calculer_date_expiration(self.selected_product)
            self.result_label.text = result

    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, 0.3))
        dialog.open()

if __name__ == '__main__':
    ExpirationApp().run()
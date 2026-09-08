import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from datetime import datetime, timedelta

kivy.require('2.0.0')

# خلفية بيضاء تقريبا
Window.clearcolor = (0.96, 0.96, 0.96, 1)

def calculer_date_expiration(nom_produit: str, ajouter_jour: bool) -> str:
    durees = {
        "LHP": 5,
        "LBEN": 20,
        "LAF": 30
    }

    if nom_produit not in durees:
        return "Produit inconnu"

    date_production = datetime.now()
    jours_ajoutes = durees[nom_produit] - 1

    if ajouter_jour:
        jours_ajoutes += 1

    date_expiration = date_production + timedelta(days=jours_ajoutes)

    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_latins = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]

    jour_production = jours_fr[date_production.weekday()]
    mois_expiration = mois_latins[date_expiration.month - 1]

    return f"{nom_produit} : {date_expiration.day} {mois_expiration} {jour_production[:2].upper()}"

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.2, 0.6, 0.86, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = 24
        self.size_hint = (0.5, None)
        self.height = 60

class RoundedSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.5, 0.5, 0.5, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = 22
        self.size_hint = (0.5, None)
        self.height = 60

class DateExpirationApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=30)

        logo_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=80)
        logo = Image(
            source='assets/Co.png',
            size_hint=(None, None),
            size=(80, 80),
            allow_stretch=True,
            keep_ratio=True
        )
        logo_layout.add_widget(logo)
        self.main_layout.add_widget(logo_layout)

        title_label = Label(
            text="Calcul de la date d'expiration",
            font_size=35,
            bold=True,
            color=(0.1, 0.2, 0.5, 1)
        )
        self.main_layout.add_widget(title_label)

        produit_calc_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, None), height=80)

        self.produit_spinner = RoundedSpinner(
            text="Choisir le produit",
            values=("LHP", "LBEN", "LAF")
        )
        self.produit_spinner.bind(text=self.on_produit_selected)

        self.calc_button = RoundedButton(
            text="Calculer"
        )
        self.calc_button.bind(on_press=self.on_calculer_button_click)

        produit_calc_layout.add_widget(self.produit_spinner)
        produit_calc_layout.add_widget(self.calc_button)

        self.main_layout.add_widget(produit_calc_layout)

        self.add_day_spinner = RoundedSpinner(
            text="Ajouter +1 jour ?",
            values=("Non", "Oui")
        )
        self.add_day_spinner.opacity = 0
        self.main_layout.add_widget(self.add_day_spinner)

        self.result_label = Label(
            text="",
            font_size=55,
            color=(0, 0, 0.7, 1),
            halign="center"
        )
        self.main_layout.add_widget(self.result_label)

        return self.main_layout

    def on_produit_selected(self, spinner, text):
        if text == "LHP":
            self.add_day_spinner.opacity = 1
        else:
            self.add_day_spinner.opacity = 0

    def on_calculer_button_click(self, instance):
        nom_produit = self.produit_spinner.text
        if nom_produit == "Choisir le produit":
            self.show_popup("Erreur", "Veuillez choisir un produit.")
            return

        ajouter_jour = False
        if nom_produit == "LHP" and self.add_day_spinner.text == "Oui":
            self.confirm_ajouter_jour()
        else:
            resultat = calculer_date_expiration(nom_produit, ajouter_jour)
            self.result_label.text = resultat

    def confirm_ajouter_jour(self):
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        label = Label(text="Êtes-vous sûr d'ajouter 1 jour supplémentaire ?", font_size=20)
        buttons = BoxLayout(orientation='horizontal', spacing=20)

        btn_oui = RoundedButton(text="Oui")
        btn_non = RoundedButton(text="Non", background_color=(0.8, 0, 0, 1))

        popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(0.7, 0.4)
        )

        def ajouter_jour_confirm(instance):
            popup.dismiss()
            resultat = calculer_date_expiration(self.produit_spinner.text, ajouter_jour=True)
            self.result_label.text = resultat

        def annuler(instance):
            popup.dismiss()
            resultat = calculer_date_expiration(self.produit_spinner.text, ajouter_jour=False)
            self.result_label.text = resultat

        btn_oui.bind(on_press=ajouter_jour_confirm)
        btn_non.bind(on_press=annuler)

        buttons.add_widget(btn_oui)
        buttons.add_widget(btn_non)

        content.add_widget(label)
        content.add_widget(buttons)

        popup.open()

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    DateExpirationApp().run()
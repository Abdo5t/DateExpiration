import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from datetime import datetime, timedelta

kivy.require('2.0.0')

# خلفية رمادية فاتحة
Window.clearcolor = (0.9, 0.9, 0.9, 1)

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

class DateExpirationApp(App):
    def build(self):
        # Layout Principal
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=35)

        # Logo en haut à gauche
        logo_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=100)
        logo = Image(
            source='assets/Co.png',
            size_hint=(None, None),
            size=(100, 100),
            allow_stretch=True,
            keep_ratio=True
        )
        logo_layout.add_widget(logo)
        self.main_layout.add_widget(logo_layout)

        # Titre de l'application
        title_label = Label(
            text="Calcul de la date d'expiration",
            font_size=40,
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        self.main_layout.add_widget(title_label)

        # Layout pour spinner produit et bouton calcul
        produit_calc_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, None), height=100)

        self.produit_spinner = Spinner(
            text="Choisir le produit",
            values=("LHP", "LBEN", "LAF"),
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=25
        )
        self.produit_spinner.bind(text=self.on_produit_selected)

        self.calc_button = Button(
            text="Calculer",
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.4, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=30
        )
        self.calc_button.bind(on_press=self.on_calculer_button_click)

        produit_calc_layout.add_widget(self.produit_spinner)
        produit_calc_layout.add_widget(self.calc_button)

        self.main_layout.add_widget(produit_calc_layout)

        # Spinner pour ajout de jour (affiché فقط مع LHP)
        self.add_day_spinner = Spinner(
            text="Ajouter +1 jour ?",
            values=("Non", "Oui"),
            size_hint=(None, None),
            size=(280, 75),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size=22
        )
        self.add_day_spinner.opacity = 0  # نخبّيه فالأول
        self.main_layout.add_widget(self.add_day_spinner)

        # Label résultat
        self.result_label = Label(
            text="",
            font_size=70,
            color=(0, 0, 1, 1),
            halign="center"
        )
        self.main_layout.add_widget(self.result_label)

        return self.main_layout

    def on_produit_selected(self, spinner, text):
        if text == "LHP":
            self.add_day_spinner.opacity = 1  # نضهر السبينر ديال إضافة يوم
        else:
            self.add_day_spinner.opacity = 0  # نخبّيه

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

        btn_oui = Button(text="Oui", background_color=(0, 0.6, 0, 1))
        btn_non = Button(text="Non", background_color=(0.6, 0, 0, 1))

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
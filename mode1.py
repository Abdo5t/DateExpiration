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

# Dark Mode background
Window.clearcolor = (0.1, 0.1, 0.1, 1)

def calculer_date_expiration(nom_produit: str, ajouter_jour: int = 0) -> str:
    durees = {
        "LHP": 5,
        "LBEN": 20,
        "LAF": 30
    }

    if nom_produit not in durees:
        return "Nom de produit inconnu"

    date_production = datetime.now()
    date_expiration = date_production + timedelta(days=durees[nom_produit] - 1 + ajouter_jour)

    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_latins = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]

    jour_production = jours_fr[date_production.weekday()]
    mois_expiration = mois_latins[date_expiration.month - 1]

    return f"{nom_produit} : {date_expiration.day} {mois_expiration} {jour_production[:2].upper()}"

class DateExpirationApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=35)

        logo = Image(source='assets/Co.png', size_hint=(None, None), size=(250, 250), pos_hint={'left_x': 0.8})
        layout.add_widget(logo)

        title_label = Label(
            text="Calcul de la date d'expiration", 
            font_size=45, 
            bold=True, 
            color=(1, 1, 1, 1),
            font_name='Roboto'
        )
        layout.add_widget(title_label)

        self.produit_spinner = Spinner(
            text="Sélectionner le produit",
            values=("LHP", "LBEN", "LAF"),
            size_hint=(None, None),
            size=(300, 75),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=25
        )
        self.produit_spinner.bind(text=self.on_produit_selected)
        layout.add_widget(self.produit_spinner)

        self.plus_one_spinner = Spinner(
            text="+0",
            values=("+0", "+1"),
            size_hint=(None, None),
            size=(150, 60),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.5, 0.3, 0.1, 1),
            color=(1, 1, 1, 1),
            font_size=25,
            opacity=0,
            disabled=True
        )
        layout.add_widget(self.plus_one_spinner)

        calc_button = Button(
            text="Calculer",
            size_hint=(None, None),
            width=300,
            height=75,
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=30,
            border=(10, 10, 10, 10)
        )
        calc_button.bind(on_press=self.on_calculer_button_click)
        layout.add_widget(calc_button)

        self.result_label = Label(
            text="", 
            font_size=90,
            color=(1, 1, 1, 1),
            halign="center",
            font_name='Roboto'
        )
        layout.add_widget(self.result_label)

        self.image_widget = Widget()
        layout.add_widget(self.image_widget)

        return layout

    def on_produit_selected(self, spinner, text):
        if text == "LHP":
            self.plus_one_spinner.opacity = 1
            self.plus_one_spinner.disabled = False
        else:
            self.plus_one_spinner.opacity = 0
            self.plus_one_spinner.disabled = True
            self.plus_one_spinner.text = "+0"

    def on_calculer_button_click(self, instance):
        nom_produit = self.produit_spinner.text
        if nom_produit == "Sélectionner le produit":
            self.show_popup("Erreur", "Veuillez sélectionner un produit.")
            return

        ajouter_jour = 1 if self.plus_one_spinner.text == "+1" else 0

        if nom_produit == "LHP" and ajouter_jour == 1:
            self.show_confirmation_popup(nom_produit)
        else:
            resultat = calculer_date_expiration(nom_produit, ajouter_jour)
            self.result_label.text = resultat
            self.show_product_image(nom_produit)

    def show_confirmation_popup(self, produit):
        content = BoxLayout(orientation='horizontal', spacing=40)
        confirmation_label = Label(
            text=f"Êtes-vous sûr de\n vouloir ajouter 1 jour à {produit} ?",
            font_size=45,
            size_hint_y=None,
            height=700,
            color=(1, 1, 1, 1)
        )
        content.add_widget(confirmation_label)

        confirm_button = Button(
            text="Confirmer",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        confirm_button.bind(on_press=lambda instance: self.on_confirm_add_day(produit))
        content.add_widget(confirm_button)

        cancel_button = Button(
            text="Annuler",
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.6, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        cancel_button.bind(on_press=lambda instance: self.on_cancel_add_day())
        content.add_widget(cancel_button)

        self.popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(0.7, 0.35)
        )
        self.popup.open()

    def on_confirm_add_day(self, produit):
        resultat = calculer_date_expiration(produit, 1)
        self.result_label.text = resultat
        self.show_product_image(produit)
        self.popup.dismiss()

    def on_cancel_add_day(self):
        self.plus_one_spinner.text = "+0"
        self.result_label.text = ""
        self.popup.dismiss()

    def show_product_image(self, produit):
        self.image_widget.clear_widgets()
        image_path = f'assets/{produit}.png'
        product_image = Image(source=image_path, size_hint=(None, None), size=(800, 800), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.image_widget.add_widget(product_image)

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, color=(1, 1, 1, 1)),
            size_hint=(0.7, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    DateExpirationApp().run()
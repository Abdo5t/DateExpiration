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

# تغيير خلفية التطبيق
Window.clearcolor = (0.9, 0.9, 0.9, 1)  # لون خلفية رمادي فاتح

# تغيير نوع الخط الأساسي
Window.add_widget(Label(text="COLAIMO. PREPAC"))

def calculer_date_expiration(nom_produit: str) -> str:
    durees = {
        "LHP": 5,
        "LBEN": 20,
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

class DateExpirationApp(App):
    def build(self):
        # Layout Principal avec BoxLayout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=35)

        # Ajouter le logo de l'entreprise en haut
        logo = Image(source='assets/Co.png', size_hint=(None, None), size=(500, 500), pos_hint={'center_x': 0.5})
        layout.add_widget(logo)

        # Titre de l'application
        title_label = Label(
            text="Calcul de la date d'expiration", 
            font_size=50,  # حجم الخط أكبر
            bold=True, 
            color=(0.2, 0.4, 0.6, 1)
        )
        layout.add_widget(title_label)

        # Spinner pour sélectionner le produit avec style
        self.produit_spinner = Spinner(
            text="Sélectionner le produit",
            values=("LHP", "LBEN", "LAF"),
            size_hint=(None, None),
            size=(280, 75),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),  # Couleur de fond du Spinner
            color=(1, 1, 1, 1),
            font_size=27  # زيادة حجم الخط في Spinner
        )
        layout.add_widget(self.produit_spinner)

        # Bouton calculer avec un style
        calc_button = Button(
            text="Calculer",
            size_hint=(None, None),
            width=280,
            height=75,
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.4, 0.7, 0.4, 1),  # Couleur du bouton
            color=(1, 1, 1, 1),
            font_size=35  # زيادة حجم الخط في الزر
        )
        calc_button.bind(on_press=self.on_calculer_button_click)
        layout.add_widget(calc_button)

        # Label pour afficher les résultats
        self.result_label = Label(
            text="", 
            font_size=90,  # زيادة حجم الخط لعرض النتيجة
            color=(0, 0, 1, 1),
            halign="center"
        )
        layout.add_widget(self.result_label)

        return layout

    def on_calculer_button_click(self, instance):
        nom_produit = self.produit_spinner.text
        if nom_produit == "Sélectionner le produit":
            self.show_popup("Erreur", "Veuillez sélectionner un produit.")
            return

        resultat = calculer_date_expiration(nom_produit)
        self.result_label.text = resultat

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    DateExpirationApp().run()
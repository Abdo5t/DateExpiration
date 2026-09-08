import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from datetime import datetime, timedelta

kivy.require('2.0.0')

# تغيير خلفية التطبيق
Window.clearcolor = (0.9, 0.9, 0.9, 1)  # لون خلفية رمادي فاتح

# تغيير نوع الخط الأساسي
kivy.resources.resource_add_path("assets/fonts")  # إضافة مجلد الخطوط
Window.add_widget(Label(text="Hello"))

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

class DateExpirationApp(App):
    def build(self):
        # Layout Principal avec BoxLayout
        layout = BoxLayout(orientation='vertical', padding=80, spacing=50)

        # Titre de l'application
        title_label = Label(text="Calcul de la date d'expiration", font_size=66, bold=True, color=(0.2, 0.4, 0.6, 1))
        layout.add_widget(title_label)

        # Spinner pour sélectionner le produit avec style
        self.produit_spinner = Spinner(
            text="Sélectionner le produit",
            values=("LHP", "LEBEN", "LAF"),
            size_hint=(None, None),
            size=(300, 50),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),  # Couleur de fond du Spinner
            color=(1, 1, 1, 1),
            font_size=25
        )
        layout.add_widget(self.produit_spinner)

        # Bouton calculer avec un style
        calc_button = Button(
            text="Calculer",
            size_hint=(None, None),
            width=150,
            height=50,
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.4, 0.7, 0.4, 1),  # Couleur du bouton
            color=(1, 1, 1, 1),
            font_size=25
        )
        calc_button.bind(on_press=self.on_calculer_button_click)
        layout.add_widget(calc_button)

        # Label pour afficher les résultats
        self.result_label = Label(text="", font_size=120, color=(0, 0, 1, 1))
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
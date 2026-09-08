import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from datetime import datetime, timedelta

kivy.require('2.0.0')

# تغيير لون الخلفية (احتياطي)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

def calculer_date_expiration(nom_produit: str, ajouter_jour: bool) -> str:
    durees = {
        "LHP": 5,
        "LBEN": 20,
        "LAF": 30
    }

    if nom_produit not in durees:
        return "Produit inconnu"

    date_production = datetime.now()
    jours_a_ajouter = durees[nom_produit] - 1
    if ajouter_jour:
        jours_a_ajouter += 1

    date_expiration = date_production + timedelta(days=jours_a_ajouter)

    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_fr = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]

    jour_semaine = jours_fr[date_expiration.weekday()]
    mois = mois_fr[date_expiration.month - 1]

    return f"{nom_produit} : {date_expiration.day} {mois} {jour_semaine[:2].upper()}"

class DateExpirationApp(App):
    def build(self):
        # Layout Principal
        principal = BoxLayout(orientation='vertical', padding=15, spacing=15)

        # خلفية مضافة
        with principal.canvas.before:
            Color(1, 1, 1, 0.2)  # الشفافية 20%
            self.background = Rectangle(source='assets/back.png', pos=principal.pos, size=Window.size)

        # نخلي الخلفية تتبع الحجم
        principal.bind(size=self.update_background, pos=self.update_background)

        # Layout pour le haut
        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)

        logo = Image(source='assets/Co.png', size_hint=(None, None), size=(100, 100))
        header.add_widget(logo)

        titre = Label(
            text="Calcul de la Date d'Expiration",
            font_size=70,
            bold=True,
            color=(0, 1, 0.5, 0.7),
            halign="center",
            valign="middle"
        )
        titre.bind(size=titre.setter('text_size'))
        header.add_widget(titre)

        principal.add_widget(header)

        # Layout pour les sélections
        selections = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=20)

        self.produit_spinner = Spinner(
            text="Choisir produit",
            values=("LHP", "LBEN", "LAF"),
            size_hint=(0.5, None),
            height=70,
            background_color=(0.2, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=24
        )
        self.produit_spinner.bind(text=self.on_product_select)

        selections.add_widget(self.produit_spinner)

        self.ajouter_jour_spinner = Spinner(
            text="Ajouter 1 jour ?",
            values=("Non", "Oui"),
            size_hint=(0.5, None),
            height=70,
            background_color=(0, 0, 1, 1),
            color=(1, 1, 1, 1),
            font_size=24,
            opacity=0  # مخفي فالأول
        )

        selections.add_widget(self.ajouter_jour_spinner)

        principal.add_widget(selections)

        # Bouton Calcul
        calc_btn = Button(
            text="Calculer",
            size_hint=(None, None),
            size=(300, 80),
            pos_hint={'center_x': 0.5},
            background_color=(0.3, 0.6, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=28
        )
        calc_btn.bind(on_press=self.calculer_date)
        principal.add_widget(calc_btn)

        # Résultat
        self.resultat_label = Label(
            text="",
            font_size=120,
            color=(0, 0, 1, 1),
            halign="center",
            valign="middle"
        )
        self.resultat_label.bind(size=self.resultat_label.setter('text_size'))
        principal.add_widget(self.resultat_label)

        return principal

    def update_background(self, instance, value):
        self.background.size = Window.size
        self.background.pos = instance.pos

    def on_product_select(self, spinner, text):
        if text == "LHP":
            self.ajouter_jour_spinner.opacity = 1
        else:
            self.ajouter_jour_spinner.opacity = 0
            self.ajouter_jour_spinner.text = "Ajouter 1 jour ?"

    def calculer_date(self, instance):
        produit = self.produit_spinner.text

        if produit not in ["LHP", "LBEN", "LAF"]:
            self.show_popup("Erreur", "Veuillez choisir un produit.")
            return

        ajouter_jour = False
        if produit == "LHP" and self.ajouter_jour_spinner.text == "Oui":
            self.confirmer_ajout_jour()
        else:
            resultat = calculer_date_expiration(produit, ajouter_jour)
            self.resultat_label.text = resultat

    def confirmer_ajout_jour(self):
        confirmation = Popup(
            title="Confirmation",
            size_hint=(0.7, 0.4)
        )

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        msg = Label(text="Confirmez-vous l'ajout d'un jour ?", font_size=22)
        layout.add_widget(msg)

        boutons = BoxLayout(orientation='horizontal', spacing=20)

        oui_btn = Button(text="Oui", background_color=(0, 0.7, 0, 1))
        non_btn = Button(text="Non", background_color=(0.7, 0, 0, 1))

        boutons.add_widget(oui_btn)
        boutons.add_widget(non_btn)

        layout.add_widget(boutons)
        confirmation.content = layout

        def on_oui(instance):
            confirmation.dismiss()
            resultat = calculer_date_expiration(self.produit_spinner.text, True)
            self.resultat_label.text = resultat

        def on_non(instance):
            confirmation.dismiss()

        oui_btn.bind(on_press=on_oui)
        non_btn.bind(on_press=on_non)

        confirmation.open()

    def show_popup(self, titre, message):
        popup = Popup(
            title=titre,
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    DateExpirationApp().run()
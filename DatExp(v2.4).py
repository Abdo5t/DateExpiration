import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.widget import Widget
from datetime import datetime, timedelta

kivy.require('2.0.0')

# خلفية داكنة
Window.clearcolor = (0.1, 0.1, 0.1, 1)

def calculer_date_expiration(nom_produit: str, ajouter_jour: int = 0) -> str:
    durees = {
        "LHP": 5,
        "LBEN": 20,
        "LAF": 30
    }
    if nom_produit not in durees:
        return "Produit inconnu"

    date_production = datetime.now()
    date_expiration = date_production + timedelta(days=durees[nom_produit] - 1 + ajouter_jour)

    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_latins = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]

    jour_production = jours_fr[date_production.weekday()]
    mois_expiration = mois_latins[date_expiration.month - 1]

    return f"{nom_produit} : {date_expiration.day} {mois_expiration} {jour_production[:2].upper()}"

class DateExpirationApp(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=30)

        # سبينر اختيار المنتج
        self.produit_spinner = Spinner(
            text="Sélectionner le produit",
            values=("LHP", "LBEN", "LAF"),
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.3, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=30
        )
        self.produit_spinner.bind(text=self.on_produit_selected)
        self.main_layout.add_widget(self.produit_spinner)

        # سبينر +1 خاص بـ LHP
        self.plus_one_spinner = Spinner(
            text="+0",
            values=("+0", "+1"),
            size_hint=(None, None),
            size=(200, 80),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(1, 0.5, 0, 1),
            color=(1, 1, 1, 1),
            font_size=25,
            opacity=0,
            disabled=True
        )
        self.main_layout.add_widget(self.plus_one_spinner)

        # زر الحساب
        calc_button = Button(
            text="Calculer",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0, 0.7, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=40
        )
        calc_button.bind(on_press=self.on_calculer_button_click)
        self.main_layout.add_widget(calc_button)

        return self.main_layout

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
            self.confirm_plus_one(nom_produit)
        else:
            self.show_resultat(nom_produit, ajouter_jour)

    def confirm_plus_one(self, nom_produit):
        content = BoxLayout(orientation='horizontal', spacing=20)

        confirm_button = Button(text='Confirmer', size_hint=(0.5, 1), background_color=(0, 0.7, 0.2, 1))
        cancel_button = Button(text='Annuler', size_hint=(0.5, 1), background_color=(0.8, 0, 0, 1))

        popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        content.add_widget(confirm_button)
        content.add_widget(cancel_button)

        confirm_button.bind(on_press=lambda x: (popup.dismiss(), self.show_resultat(nom_produit, 1)))
        cancel_button.bind(on_press=popup.dismiss)

        popup.open()

    def show_resultat(self, nom_produit, ajouter_jour):
        self.main_layout.clear_widgets()

        # حساب النتيجة
        resultat = calculer_date_expiration(nom_produit, ajouter_jour)

        # عرض النتيجة
        resultat_label = Label(
            text=resultat,
            font_size=50,
            color=(0, 1, 0, 1),
            halign="center",
            valign="middle"
        )
        self.main_layout.add_widget(resultat_label)

        # عرض صورة المنتج
        image_path = f"assets/{nom_produit}.png"
        product_image = Image(
            source=image_path,
            size_hint=(None, None),
            size=(400, 400),
            allow_stretch=True
        )
        self.main_layout.add_widget(product_image)

        # زر حساب جديد
        new_calc_button = Button(
            text="Nouveau Calcul",
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.3, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=35
        )
        new_calc_button.bind(on_press=self.reset_app)
        self.main_layout.add_widget(new_calc_button)

    def reset_app(self, instance):
        self.main_layout.clear_widgets()
        self.build()
        
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=25),
            size_hint=(0.7, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    DateExpirationApp().run()
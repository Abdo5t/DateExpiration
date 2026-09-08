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

    return f"{nom_produit} : {date_expiration.day} {mois_expiration} - {jour_production[:2].upper()}"

class DateExpirationApp(App):
    def build(self):
        self.root_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # شعار التطبيق
        self.top_layout = BoxLayout(size_hint=(1, 0.25))
        logo = Image(source='assets/Co.png', allow_stretch=True, keep_ratio=True)
        self.top_layout.add_widget(logo)
        self.root_layout.add_widget(self.top_layout)

        # عنوان كبير فوق
        self.title_label = Label(
            text="Calcul de la date d'expiration",
            font_size=45,
            bold=True,
            color=(0.9, 0.9, 1, 1),
            size_hint=(1, 0.15)
        )
        self.root_layout.add_widget(self.title_label)

        # باقي الواجهة
        self.bottom_layout = BoxLayout(orientation='vertical', spacing=20)
        self.build_bottom_layout()
        self.root_layout.add_widget(self.bottom_layout)

        return self.root_layout

    def build_bottom_layout(self):
        self.bottom_layout.clear_widgets()

        # سبينر اختيار المنتج
        self.produit_spinner = Spinner(
            text="Sélectionner le produit",
            values=("LHP", "LBEN", "LAF"),
            size_hint=(None, None),
            size=(300, 70),
            background_normal='',
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size=25
        )
        self.produit_spinner.bind(text=self.on_produit_selected)
        self.bottom_layout.add_widget(self.produit_spinner)

        # سبينر +0 / +1
        self.plus_one_spinner = Spinner(
            text="+0",
            values=("+0", "+1"),
            size_hint=(None, None),
            size=(150, 60),
            background_normal='',
            background_color=(0.9, 0.5, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=22,
            opacity=0,
            disabled=True
        )
        self.bottom_layout.add_widget(self.plus_one_spinner)

        # زر الحساب
        calc_button = Button(
            text="Calculer",
            size_hint=(None, None),
            size=(280, 75),
            background_normal='',
            background_color=(0.3, 0.8, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=30
        )
        calc_button.bind(on_press=self.on_calculer_button_click)
        self.bottom_layout.add_widget(calc_button)

        # النتيجة
        self.result_label = Label(
            text="",
            font_size=45,
            color=(1, 1, 0, 1),
            size_hint=(1, None),
            height=60,
            halign="center",
            valign="middle"
        )
        self.result_label.bind(size=self.update_text_size)
        self.bottom_layout.add_widget(self.result_label)

        # صورة المنتج تحت النتيجة
        self.product_image = Image(
            source='',
            size_hint=(None, None),
            size=(300, 300),
            allow_stretch=True,
            keep_ratio=True,
            opacity=0
        )
        self.bottom_layout.add_widget(self.product_image)

    def update_text_size(self, *args):
        self.result_label.text_size = (self.result_label.width, None)

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

        if nom_produit == "LHP" and self.plus_one_spinner.text == "+1":
            self.show_confirmation_popup()
        else:
            self.afficher_resultat()

    def afficher_resultat(self):
        nom_produit = self.produit_spinner.text
        ajouter_jour = 1 if self.plus_one_spinner.text == "+1" else 0
        resultat = calculer_date_expiration(nom_produit, ajouter_jour)

        self.result_label.text = resultat
        self.product_image.source = f'assets/{nom_produit}.png'
        self.product_image.opacity = 1

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )
        popup.open()

    def show_confirmation_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        label = Label(text="Êtes-vous sûr d'ajouter un jour ?", font_size=20)
        button_layout = BoxLayout(spacing=20, size_hint_y=None, height=60)

        confirm_button = Button(text="Confirmer", background_color=(0.1, 0.7, 0.1, 1))
        cancel_button = Button(text="Annuler", background_color=(0.8, 0.2, 0.2, 1))

        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(label)
        content.add_widget(button_layout)

        popup = Popup(title="Confirmation", content=content, size_hint=(0.8, 0.5))

        confirm_button.bind(on_release=lambda x: (self.afficher_resultat(), popup.dismiss()))
        cancel_button.bind(on_release=popup.dismiss)

        popup.open()

if __name__ == '__main__':
    DateExpirationApp().run()
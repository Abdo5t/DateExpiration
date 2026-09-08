import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.resources import resource_find
from datetime import datetime, timedelta

kivy.require('2.0.0')

# تغيير خلفية التطبيق
Window.clearcolor = (0.9, 0.9, 0.9, 1)

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

        # شعار الشركة
        logo = Image(
            source=resource_find('assets/Co.png'),
            size_hint=(None, None),
            size=(300, 300),
            pos_hint={'center_x': 0.5}
        )
        layout.add_widget(logo)

        # عنوان التطبيق
        title_label = Label(
            text="Calcul de la date d'expiration",
            font_size=50,
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        layout.add_widget(title_label)

        # BoxLayout أفقي للسبينر وزر الحساب
        selection_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=75, spacing=20)

        # سبينر اختيار المنتج
        self.produit_spinner = Spinner(
            text="Sélectionner le produit",
            values=("LHP", "LBEN", "LAF"),
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=27
        )
        self.produit_spinner.bind(text=self.on_produit_selected)
        selection_layout.add_widget(self.produit_spinner)

        # سبينر +0/+1 (خاص بالحليب LHP فقط)
        self.plus_one_spinner = Spinner(
            text="+0",
            values=("+0", "+1"),
            size_hint=(None, None),
            size=(100, 75),
            background_normal='',
            background_color=(0.8, 0.5, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=25,
            opacity=0,
            disabled=True
        )
        selection_layout.add_widget(self.plus_one_spinner)

        # زر الحساب
        calc_button = Button(
            text="Calculer",
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.4, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=35
        )
        calc_button.bind(on_press=self.on_calculer_button_click)
        selection_layout.add_widget(calc_button)

        layout.add_widget(selection_layout)

        # لابل عرض النتيجة
        self.result_label = Label(
            text="",
            font_size=90,
            color=(0, 0, 1, 1),
            halign="center"
        )
        layout.add_widget(self.result_label)

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
        resultat = calculer_date_expiration(nom_produit, ajouter_jour)
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
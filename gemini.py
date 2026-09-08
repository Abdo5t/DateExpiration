import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup # Make sure Popup is imported
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.metrics import dp, sp
# Remove Builder import if only used for the dynamic popup string
# from kivy.lang import Builder
from datetime import datetime, timedelta
import os
import json

kivy.require('2.0.0')

# --- Configuration Loading (keep as is) ---
DEFAULT_CONFIG = {
    "products": {
        "LHP": {"duration": 5, "image": "assets/LHP.png", "allow_plus_one": True},
        "LBEN": {"duration": 20, "image": "assets/LBEN.png", "allow_plus_one": False},
        "LAF": {"duration": 30, "image": "assets/LAF.png", "allow_plus_one": False}
    },
    "assets_folder": "assets"
}
def load_config(filename="config.json"):
    # ... (keep load_config function as is) ...
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"Configuration loaded from {filename}")
            return config
    except FileNotFoundError:
        print(f"WARNING: {filename} not found. Using default configuration.")
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        print(f"ERROR: {filename} is not valid JSON. Using default configuration.")
        return DEFAULT_CONFIG
    except Exception as e:
        print(f"ERROR: Could not load {filename}: {e}. Using default configuration.")
        return DEFAULT_CONFIG

# --- Core Logic (keep as is) ---
def calculer_date_expiration(nom_produit: str, config: dict, ajouter_jour: int = 0) -> str:
    # ... (keep calculer_date_expiration function as is) ...
    products = config.get("products", {})
    if nom_produit not in products:
        return "Produit inconnu"
    product_info = products[nom_produit]
    duration = product_info.get("duration", 0)
    date_production = datetime.now()
    date_expiration = date_production + timedelta(days=duration - 1 + ajouter_jour)
    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_latins = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]
    jour_expiration_weekday = jours_fr[date_expiration.weekday()]
    mois_expiration = mois_latins[date_expiration.month - 1]
    return f"{nom_produit} : {date_expiration.day} {mois_expiration}\n{jour_expiration_weekday[:2].upper()}"


# --- Kivy UI Classes ---

# Define a Python class for the popup (can be empty if structure is purely in KV)
# This helps Kivy link the KV rule <ConfirmPopup@Popup>
class ConfirmPopup(Popup):
    pass

class RootLayout(BoxLayout):
    product_spinner = ObjectProperty(None)
    plus_one_spinner = ObjectProperty(None)
    result_label = ObjectProperty(None)
    product_image = ObjectProperty(None)
    product_list = ListProperty([])
    default_spinner_text = StringProperty("Sélectionner le produit")

    def __init__(self, app_config, **kwargs):
        # ... (keep __init__ as is) ...
        super().__init__(**kwargs)
        self.config = app_config
        self.product_list = list(self.config.get("products", {}).keys())
        if not self.product_list:
            self.default_spinner_text = "Aucun produit configuré"
        elif self.default_spinner_text in self.product_list:
             self.default_spinner_text = " Sélectionner le produit " # Add space if needed

    def on_produit_selected(self, selected_product_name):
        # ... (keep on_produit_selected as is) ...
        self.result_label.text = ""
        self.product_image.source = ""
        self.product_image.opacity = 0
        products = self.config.get("products", {})
        product_info = products.get(selected_product_name)
        if product_info and product_info.get("allow_plus_one", False):
            self.plus_one_spinner.opacity = 1
            self.plus_one_spinner.disabled = False
        else:
            self.plus_one_spinner.opacity = 0
            self.plus_one_spinner.disabled = True
            self.plus_one_spinner.text = "+0"

    # << --- MODIFY THIS METHOD --- >>
    def on_calculer_button_click(self):
        """Called when the 'Calculer' button is pressed."""
        nom_produit = self.product_spinner.text
        if nom_produit == self.default_spinner_text or nom_produit not in self.config.get("products", {}):
            self.show_popup("Erreur", "Veuillez sélectionner un produit valide.")
            return

        adds_one_day = (
            not self.plus_one_spinner.disabled and
            self.plus_one_spinner.text == "+1"
        )

        if adds_one_day:
            # Instantiate the popup defined in KV
            # Kivy automatically finds the <ConfirmPopup@Popup> rule
            popup = ConfirmPopup()
            # Bind the custom 'on_confirm' event (defined in KV)
            # to the method that should run after confirmation
            popup.bind(on_confirm=self.handle_confirmation)
            popup.open()
        else:
            # No confirmation needed, calculate directly
            self.afficher_resultat()

    # << --- ADD THIS METHOD --- >>
    def handle_confirmation(self, popup_instance):
        """Handles the confirmation event from the popup."""
        print("RootLayout: handle_confirmation called") # Debug print
        popup_instance.dismiss()  # Close the popup
        self.afficher_resultat()  # Proceed with calculation

    def afficher_resultat(self):
        # ... (keep afficher_resultat as is) ...
        print("RootLayout: afficher_resultat called") # Debug print
        nom_produit = self.product_spinner.text
        # Ensure product is still valid (might be overkill but safe)
        if nom_produit == self.default_spinner_text or nom_produit not in self.config.get("products", {}):
             print("RootLayout: Invalid product in afficher_resultat") # Debug print
             return # Don't proceed if product changed while popup was open

        ajouter_jour = 1 if (not self.plus_one_spinner.disabled and self.plus_one_spinner.text == "+1") else 0
        print(f"RootLayout: Calculating for {nom_produit} with ajouter_jour={ajouter_jour}") # Debug print

        resultat = calculer_date_expiration(nom_produit, self.config, ajouter_jour)
        self.result_label.text = resultat

        product_info = self.config.get("products", {}).get(nom_produit)
        if product_info:
            image_path = product_info.get("image", "")
            if image_path and os.path.exists(image_path):
                 self.product_image.source = image_path
                 self.product_image.opacity = 1
                 print(f"RootLayout: Displaying image {image_path}") # Debug print
            else:
                 self.product_image.source = ""
                 self.product_image.opacity = 0
                 if image_path:
                     print(f"Warning: Image not found at {image_path}")
        else:
             self.product_image.source = ""
             self.product_image.opacity = 0

    def show_popup(self, title, message):
        # ... (keep show_popup as is) ...
        popup = Popup(
            title=title,
            content=Label(text=message, font_size=sp(18)),
            size_hint=(0.7, 0.4)
        )
        popup.open()

# --- Main App Class (keep as is) ---
class DateExpirationApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.config = load_config()
        # KV file 'dateexpiration.kv' is automatically loaded
        return RootLayout(app_config=self.config)

if __name__ == '__main__':
    DateExpirationApp().run()
from kivy.uix.datepicker import DatePicker

class DateExpirationApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Logo
        logo = Image(source='assets/Co.png', size_hint=(None, None), size=(140, 140), pos_hint={'center_x': 0.5})
        layout.add_widget(logo)

        # Titre
        title_label = Label(
            text="Calcul de la date d'expiration",
            font_size=22,
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        layout.add_widget(title_label)

        # Spinner
        self.produit_spinner = Spinner(
            text="Sélectionner le produit",
            values=("LHP", "LEBEN", "LAF"),
            size_hint=(None, None),
            size=(220, 45),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.2, 0.4, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=18
        )
        layout.add_widget(self.produit_spinner)

        # Date Picker for production date
        self.date_picker = DatePicker(size_hint=(None, None), size=(220, 45), pos_hint={"center_x": 0.5})
        layout.add_widget(self.date_picker)

        # Bouton
        calc_button = Button(
            text="Calculer",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"center_x": 0.5},
            background_normal='',
            background_color=(0.4, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=20
        )
        calc_button.bind(on_press=self.on_calculer_button_click)
        layout.add_widget(calc_button)

        # Résultat
        self.result_label = Label(
            text="",
            font_size=20,
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

        date_production = self.date_picker.text
        if not date_production:
            self.show_popup("Erreur", "Veuillez sélectionner la date de production.")
            return

        resultat = calculer_date_expiration(nom_produit, date_production)
        self.result_label.text = resultat

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.4)
        )
        popup.open()

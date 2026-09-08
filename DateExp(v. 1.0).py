import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

def calculer_date_expiration(nom_produit: str) -> str:
    durees = {
        "LHP": 5,
        "LEBEN": 20,
        "LAF": 30
    }

    if nom_produit not in durees:
        return "Nom de produit inconnu"

    date_production = datetime.now()
    # حساب تاريخ نهاية الصلاحية بشكل دقيق (اليوم الأخير الصالح)
    date_expiration = date_production + timedelta(days=durees[nom_produit] - 1)

    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois_latins = ["JAN", "FEB", "MAR", "AVR", "MAI", "JUI", "JUL", "AOU", "SEP", "OCT", "NOV", "DEC"]

    jour_production = jours_fr[date_production.weekday()]
    mois_expiration = mois_latins[date_expiration.month - 1]

    return f"{nom_produit} : {date_expiration.day} {mois_expiration} {jour_production[:2].upper()}"

def bouton_calculer_clicked():
    nom_produit = produit_combobox.get()
    if not nom_produit:
        messagebox.showerror("Erreur", "Veuillez sélectionner un produit.")
        return

    resultat = calculer_date_expiration(nom_produit)
    label_resultat.config(text=resultat)

# --- UI améliorée ---
racine = tk.Tk()
racine.title("Date d'expiration")
racine.geometry("350x250")
racine.configure(bg="#f0f0f5")

# Style global
style = ttk.Style()
style.configure("TCombobox", padding=5, font=("Helvetica", 12))
style.configure("TButton", padding=6, font=("Helvetica", 12))

# Titre
titre = tk.Label(racine, text="Calcul de la date d'expiration", font=("Helvetica", 14, "bold"), bg="#f0f0f5", fg="#333")
titre.pack(pady=15)

# Choix du produit
label_choix = tk.Label(racine, text="Produit :", font=("Helvetica", 12), bg="#f0f0f5")
label_choix.pack()

produit_combobox = ttk.Combobox(racine, values=["LHP", "LEBEN", "LAF"], state="readonly", width=15)
produit_combobox.set("LHP")
produit_combobox.pack(pady=5)

# Bouton calcul
bouton_calculer = ttk.Button(racine, text="Calculer", command=bouton_calculer_clicked)
bouton_calculer.pack(pady=10)

# Résultat
label_resultat = tk.Label(racine, text="", font=("Helvetica", 16, "bold"), fg="#006699", bg="#f0f0f5")
label_resultat.pack(pady=20)

racine.mainloop()
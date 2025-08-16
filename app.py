import os
import pandas as pd
from flask import Flask, render_template, request, send_file
import requests

app = Flask(__name__)

# === CONFIGURATION ===
BOT_TOKEN = "8308452247:AAGl-ODQYVZ8G3DrkvsOuussx1HLMNWiB0w"   
CHAT_ID = "-4785620332"      
EXCEL_FILE = "recensement.xlsx"


# === PAGE D’ACCUEIL AVEC FORMULAIRE ===
@app.route('/')
def index():
    return render_template('form.html')


# === TRAITEMENT DU FORMULAIRE ===
@app.route('/submit', methods=['POST'])
def submit():
    # 1. Récupérer les infos envoyées
    nom = request.form.get("nom")
    prenom = request.form.get("prenom")
    ville = request.form.get("ville")
    telephone = request.form.get("telephone")

    # 2. Sauvegarder dans Excel
    new_data = pd.DataFrame([[nom, prenom, ville, telephone]],
                            columns=["Nom", "Prénom", "Ville", "Téléphone"])

    if os.path.exists(EXCEL_FILE):
        old_data = pd.read_excel(EXCEL_FILE)
        df = pd.concat([old_data, new_data], ignore_index=True)
    else:
        df = new_data

    df.to_excel(EXCEL_FILE, index=False)

    # 3. Envoyer notification dans Telegram
    message = f"📝 Nouveau inscrit !\nNom: {nom}\nPrénom: {prenom}\nVille: {ville}\nTéléphone: {telephone}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    requests.get(url, params=params)

    return "✅ Merci, vos informations ont été enregistrées avec succès !"


# === TÉLÉCHARGER LE FICHIER EXCEL ===
@app.route('/download')
def download():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    return "⚠️ Aucun fichier trouvé."


# === LANCER FLASK ===
if __name__ == '__main__':
    app.run(debug=True)

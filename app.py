# app.py
import os
import io
import datetime
from flask import Flask, render_template, request, jsonify, send_file, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import pandas as pd
import config

app = Flask(__name__)
# SQLite file local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    city_russia = db.Column(db.String(100), nullable=False)
    city_senegal = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(60), nullable=False)
    emergency_contact = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "Nom complet": self.full_name,
            "Ville (Russie)": self.city_russia,
            "Ville (Sénégal)": self.city_senegal,
            "Téléphone": self.phone,
            "Contact d'urgence": self.emergency_contact,
            "Date": self.created_at
        }


def init_db():
    db.create_all()


def check_admin_token():
    """Simple check : token dans query param ?token=... ou header X-ADMIN-TOKEN."""
    token = request.args.get("token") or request.headers.get("X-ADMIN-TOKEN")
    if token != config.ADMIN_TOKEN:
        abort(403)


def envoyer_telegram_message(texte):
    """Envoie un message texte simple au chat Telegram configuré."""
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("Telegram non configuré. Message non envoyé.")
        return False, "Telegram non configuré"
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": config.TELEGRAM_CHAT_ID, "text": texte}
    try:
        r = requests.post(url, data=payload, timeout=10)
        return r.ok, r.text
    except Exception as e:
        return False, str(e)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/envoyer", methods=["POST"])
def envoyer():
    """Reçoit les données en JSON du formulaire, les sauvegarde, notifie Telegram."""
    data = request.get_json()
    expected = ["full_name", "city_russia", "city_senegal", "phone", "emergency_contact"]
    # validation simple
    if not data:
        return jsonify({"status": "error", "message": "Aucune donnée reçue"}), 400

    missing = [k for k in expected if k not in data or not str(data[k]).strip()]
    if missing:
        return jsonify({"status": "error", "message": "Champs manquants: " + ", ".join(missing)}), 400

    # create submission
    sub = Submission(
        full_name=data["full_name"].strip(),
        city_russia=data["city_russia"].strip(),
        city_senegal=data["city_senegal"].strip(),
        phone=data["phone"].strip(),
        emergency_contact=data["emergency_contact"].strip()
    )
    db.session.add(sub)
    db.session.commit()

    # Préparer un message lisible pour Telegram
    message = (
        "📌 Nouvelle demande d'adhésion\n"
        f"Nom : {sub.full_name}\n"
        f"Ville (Russie) : {sub.city_russia}\n"
        f"Ville (Sénégal) : {sub.city_senegal}\n"
        f"Téléphone : {sub.phone}\n"
        f"Contact d'urgence : {sub.emergency_contact}\n"
        f"ID en base: {sub.id}"
    )
    ok, resp = envoyer_telegram_message(message)

    return jsonify({
        "status": "success",
        "message": "Inscription reçue. Les admins ont été notifiés via Telegram." if ok else "Inscription enregistrée mais l'envoi Telegram a échoué.",
        "telegram_ok": ok,
        "telegram_resp": resp
    })


@app.route("/admin", methods=["GET"])
def admin():
    """Interface admin (protection par token simple)."""
    check_admin_token()
    subs = Submission.query.order_by(Submission.created_at.desc()).all()
    return render_template("admin.html", submissions=subs, token=config.ADMIN_TOKEN)


@app.route("/export", methods=["GET"])
def export_excel():
    """Retourne un fichier Excel (download) contenant toutes les inscriptions."""
    check_admin_token()
    subs = Submission.query.order_by(Submission.created_at.desc()).all()
    if not subs:
        return jsonify({"status": "error", "message": "Aucune inscription à exporter."}), 400

    records = [s.to_dict() for s in subs]
    df = pd.DataFrame(records)
    # Conversion de la date en string pour Excel si besoin
    if "Date" in df.columns:
        df["Date"] = df["Date"].apply(lambda d: d.strftime("%Y-%m-%d %H:%M:%S"))

    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"recensement_senegalais_russie_{ts}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/send_export_telegram", methods=["GET"])
def send_export_telegram():
    """Génère l'Excel en mémoire et l'envoie au chat Telegram configuré."""
    check_admin_token()
    subs = Submission.query.order_by(Submission.created_at.desc()).all()
    if not subs:
        return jsonify({"status": "error", "message": "Aucune inscription à exporter."}), 400

    records = [s.to_dict() for s in subs]
    df = pd.DataFrame(records)
    if "Date" in df.columns:
        df["Date"] = df["Date"].apply(lambda d: d.strftime("%Y-%m-%d %H:%M:%S"))

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return jsonify({"status": "error", "message": "Telegram non configuré."}), 500

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendDocument"
    files = {
        "document": ("recensement_senegalais_russie.xlsx", buffer)
    }
    data = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "caption": "📥 Export des inscriptions — Association des Sénégalais de Russie"
    }
    try:
        r = requests.post(url, data=data, files=files, timeout=30)
        if r.ok:
            return jsonify({"status": "success", "message": "Fichier envoyé sur Telegram.", "resp": r.text})
        else:
            return jsonify({"status": "error", "message": "Erreur Telegram: " + r.text}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    if not os.path.exists("submissions.db"):
        init_db()
        print("DB initialisée.")
    app.run(host="0.0.0.0", port=5000, debug=True)

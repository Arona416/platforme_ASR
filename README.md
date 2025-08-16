📌 Plateforme d’Inscription - Association des Sénégalais de Russie
🎯 Objectif

Ce projet est une plateforme web simple permettant aux Sénégalais résidant en Russie de s’inscrire afin de rejoindre les groupes WhatsApp et Telegram de l’association.
Les informations collectées servent à :

Ajout rapide dans les groupes après vérification.

Constitution d’un fichier Excel pour le recensement et l’organisation d’événements.

Envoi automatique d’une notification à l’équipe via Telegram Bot.

🛠️ Technologies utilisées

Frontend :

HTML5

CSS3

JavaScript (Validation côté client)

Backend :

Python (Flask)

Pandas (gestion du fichier Excel)

Requests (envoi au bot Telegram)

Base de données :

Fichier Excel (inscriptions.xlsx)

Notification :

Telegram Bot API
plateforme-inscription/
│
├── static/
│   ├── style.css         # Styles CSS
│
├── templates/
│   ├── index.html        # Formulaire d'inscription
│
├── app.py                # Backend Flask
├── inscriptions.xlsx     # Fichier Excel (créé automatiquement)
├── requirements.txt      # Dépendances Python
└── README.md             # Documentation

👨‍💻 Auteur

Projet développé par Barry Arona pour l’Association des Sénégalais de Russie 🇸🇳🇷🇺

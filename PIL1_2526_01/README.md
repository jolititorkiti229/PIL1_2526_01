# IFRI_MentorLink

Application web de mentorat académique pour les étudiants de l'IFRI.

## Technologies
- **Backend** : Python 3 / Flask
- **Frontend** : HTML5 / CSS3 / JavaScript vanilla
- **Base de données** : MySQL 8

## Installation rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/[org]/PIL1_2526_01.git && cd PIL1_2526_01

# 2. Environnement virtuel
python -m venv venv && source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# 3. Dépendances
pip install -r backend/requirements.txt

# 4. Base de données
mysql -u root -p -e "CREATE DATABASE mentorlink CHARACTER SET utf8mb4;"
mysql -u root -p mentorlink < Dump20260605__1_.sql

# 5. Config
cp backend/.env.example backend/.env
# Éditez .env avec vos infos MySQL

# 6. Lancer
cd backend && python app.py
```

Accès : http://127.0.0.1:5000

## Fonctionnalités
- Inscription / Connexion sécurisée (hash SHA-256)
- Profil utilisateur avec compétences et disponibilités
- Algorithme de matching mentor-mentoré (score sur 100)
- Recherche filtrée par matière, filière, niveau, disponibilité
- Offres et demandes de mentorat
- Messagerie privée intégrée
- Système de notifications

## Accès GitHub
Les utilisateurs `ratheilesse`, `primearwyn` et `MaryseGAHOU` ont accès au dépôt.

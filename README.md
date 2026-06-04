PIL1_2526_01 - IFRI MentorLink

Présentation du projet

IFRI MentorLink est une plateforme de mentorat académique destinée aux étudiants de l'IFRI.

L'objectif principal est de mettre en relation des étudiants ayant des compétences dans certaines matières (mentors) avec des étudiants rencontrant des difficultés dans ces mêmes matières (mentorés).

La plateforme permettra :

- La création et la gestion de comptes utilisateurs.
- La gestion des profils étudiants.
- La publication d'offres et de demandes de mentorat.
- La recherche d'offres et de demandes.
- La mise en relation automatique (matching) mentor/mentoré.
- Une messagerie intégrée.
- Un système de notifications.

Technologies utilisées

Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5

Backend

- Python
- Flask

Base de données

- MySQL

Gestion de version

- Git
- GitHub

---

Répartition des tâches

Membre 1 : Aminatou

Responsable

Documentation et gestion du projet

Tâches

- Rédaction du rapport final.
- Rédaction du manuel utilisateur.
- Organisation des réunions.
- Vérification de l'avancement global.
- Préparation de la présentation finale.
- Gestion du dossier :

documentation/

---

Membre 2 : Jimmy

Responsable

Base de données

Tâches

- Conception de la base de données.
- Création du script SQL.
- Gestion des relations entre les tables.
- Maintenance de la base de données.
- Assistance SQL aux autres membres.

Dossier concerné

database/

Contenu attendu :

mentorlink.sql
MCD_MLD_IFRI_MentorLink.txt

---

Membre 3 : Fridolon

Responsable

Authentification

Tâches

- Inscription.
- Connexion.
- Déconnexion.
- Gestion des sessions.
- Hashage des mots de passe.

Dossier concerné

auth/

---

Membre 4 : Farid

Responsable

Gestion du mentorat

Tâches

- Création des offres.
- Création des demandes.
- Recherche d'offres.
- Recherche de demandes.
- Gestion des réponses aux offres.

Dossier concerné

mentorat/

---

Membre 5 : Jean Frédéric

Responsable

Algorithme de matching

Tâches

- Développement de l'algorithme de correspondance.
- Calcul du score de compatibilité.
- Affichage des résultats de matching.

Dossier concerné

matching/

Critères du score :

- Compatibilité des matières.
- Compatibilité des disponibilités.
- Filière.
- Niveau d'étude.

---

Membre 6 : Prielle

Responsable

Messagerie

Tâches

- Gestion des conversations.
- Envoi de messages.
- Réception des messages.
- Historique des conversations.
- Notifications.

Dossier concerné

messagerie/

---

Membre 7 : Hoseas

Responsable

Interface utilisateur (Frontend)

Tâches

- Intégration de la maquette.
- Création des pages HTML.
- CSS et Bootstrap.
- Responsive Design.
- Expérience utilisateur.

Dossier concerné

frontend/

---

Structure du projet

PIL1_2526_01/

├── README.md

├── database/
├── auth/
├── mentorat/
├── matching/
├── messagerie/
├── frontend/
├── documentation/

---

Installation du projet

1. Cloner le dépôt

git clone https://github.com/jolititorkiti229/PIL1_2526_01.git

2. Entrer dans le dossier

cd PIL1_2526_01

---

Règles de travail Git

Chaque membre doit travailler uniquement dans son dossier.

Exemple :

- Fridolon travaille dans "auth/"
- Farid travaille dans "mentorat/"
- Jean Frédéric travaille dans "matching/"
- Prielle travaille dans "messagerie/"
- Hoseas travaille dans "frontend/"
- Aminatou travaille dans "documentation/"
- Jimmy travaille dans "database/"

---

Récupérer les dernières modifications

Avant chaque séance de travail :

git pull origin main

---

Envoyer son travail sur GitHub

Ajouter les fichiers

git add .

Créer un commit

git commit -m "Description du travail effectué"

Exemple :

git commit -m "Ajout de la page de connexion"

Envoyer les modifications

git push origin main

---

Bonnes pratiques

- Faire des commits régulièrement.
- Écrire des messages de commit clairs.
- Ne pas modifier le dossier d'un autre membre sans son accord.
- Toujours effectuer un "git pull" avant de commencer à travailler.
- Tester son code avant de l'envoyer.

---

Objectif final

Développer une plateforme complète de mentorat académique permettant aux étudiants de l'IFRI :

- de trouver un mentor ;
- de devenir mentor ;
- d'échanger via une messagerie ;
- de bénéficier d'un système de matching intelligent ;

tout en respectant les exigences du Projet Intégrateur 2025-2026.

from flask import Blueprint, request, jsonify, session
from backend.utils.db import query
from backend import bcrypt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['nom', 'prenom', 'email', 'telephone', 'password', 'filiere_id', 'niveau']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'Champ manquant: {field}'}), 400

    # Vérifier unicité email
    existing = query("SELECT id FROM users WHERE email=%s OR telephone=%s",
                     (data['email'], data['telephone']), fetchone=True)
    if existing:
        return jsonify({'error': 'Email ou téléphone déjà utilisé'}), 409

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user_id = query(
        """INSERT INTO users (nom, prenom, email, telephone, password, filiere_id, niveau, bio, centre_interet)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (data['nom'], data['prenom'], data['email'], data['telephone'],
         hashed_pw, data['filiere_id'], data['niveau'],
         data.get('bio', ''), data.get('centre_interet', '')),
        commit=True
    )

    # Ajouter les compétences si fournies
    if data.get('competences'):
        for comp in data['competences']:
            query("INSERT INTO competences (user_id, matiere_id, type, niveau) VALUES (%s, %s, %s, %s)",
                  (user_id, comp['matiere_id'], comp['type'], comp.get('niveau', 'intermediaire')),
                  commit=True)

    session['user_id'] = user_id
    user = query("SELECT id, nom, prenom, email, filiere_id, niveau, photo FROM users WHERE id=%s",
                 (user_id,), fetchone=True)
    return jsonify({'message': 'Inscription réussie', 'user': user}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier', '')
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'error': 'Identifiant et mot de passe requis'}), 400

    user = query(
        "SELECT * FROM users WHERE email=%s OR telephone=%s",
        (identifier, identifier), fetchone=True
    )

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Identifiant ou mot de passe incorrect'}), 401

    session['user_id'] = user['id']
    user.pop('password', None)
    return jsonify({'message': 'Connexion réussie', 'user': user}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Déconnecté'}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    user = query(
        """SELECT u.id, u.nom, u.prenom, u.email, u.telephone, u.niveau, u.photo, u.bio,
                  u.centre_interet, u.date_creation, f.nom as filiere
           FROM users u JOIN filieres f ON u.filiere_id = f.id
           WHERE u.id=%s""",
        (session['user_id'],), fetchone=True
    )
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    return jsonify(user), 200


@auth_bp.route('/filieres', methods=['GET'])
def get_filieres():
    filieres = query("SELECT * FROM filieres ORDER BY nom", fetchall=True)
    return jsonify(filieres), 200


@auth_bp.route('/matieres', methods=['GET'])
def get_matieres():
    matieres = query("SELECT * FROM matieres ORDER BY nom", fetchall=True)
    return jsonify(matieres), 200

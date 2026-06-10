from flask import Blueprint, request, jsonify, session, current_app
from backend.utils.db import query
from backend.utils.auth import login_required
import os
import uuid

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    uid = session['user_id']
    user = query(
        """SELECT u.id, u.nom, u.prenom, u.email, u.telephone, u.niveau, u.photo,
                  u.bio, u.centre_interet, u.filiere_id, f.nom as filiere
           FROM users u JOIN filieres f ON u.filiere_id = f.id
           WHERE u.id=%s""",
        (uid,), fetchone=True
    )
    competences = query(
        """SELECT c.id, c.type, c.niveau, m.id as matiere_id, m.nom as matiere
           FROM competences c JOIN matieres m ON c.matiere_id = m.id
           WHERE c.user_id=%s""",
        (uid,), fetchall=True
    )
    disponibilites = query(
        "SELECT * FROM disponibilites WHERE user_id=%s ORDER BY FIELD(jour,'Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche')",
        (uid,), fetchall=True
    )
    # Stats
    offres = query("SELECT COUNT(*) as n FROM mentorat WHERE user_id=%s AND type='offre'", (uid,), fetchone=True)
    demandes = query("SELECT COUNT(*) as n FROM mentorat WHERE user_id=%s AND type='demande'", (uid,), fetchone=True)
    avg_avis = query(
        """SELECT AVG(a.note) as moy, COUNT(*) as total FROM avis a
           JOIN sessions_mentorat s ON a.session_id = s.id
           WHERE s.mentor_id=%s""",
        (uid,), fetchone=True
    )

    user['competences'] = competences
    user['disponibilites'] = disponibilites
    user['stats'] = {
        'offres': offres['n'],
        'demandes': demandes['n'],
        'note_moy': float(avg_avis['moy']) if avg_avis['moy'] else None,
        'nb_avis': avg_avis['total']
    }
    return jsonify(user), 200


@users_bp.route('/profile/<int:uid>', methods=['GET'])
@login_required
def get_user_profile(uid):
    user = query(
        """SELECT u.id, u.nom, u.prenom, u.niveau, u.photo, u.bio,
                  u.centre_interet, u.filiere_id, f.nom as filiere, u.email, u.telephone
           FROM users u JOIN filieres f ON u.filiere_id = f.id
           WHERE u.id=%s""",
        (uid,), fetchone=True
    )
    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    competences = query(
        """SELECT c.type, c.niveau, m.nom as matiere
           FROM competences c JOIN matieres m ON c.matiere_id = m.id
           WHERE c.user_id=%s""",
        (uid,), fetchall=True
    )
    disponibilites = query("SELECT jour, heure_debut, heure_fin FROM disponibilites WHERE user_id=%s", (uid,), fetchall=True)
    avg_avis = query(
        """SELECT AVG(a.note) as moy, COUNT(*) as total FROM avis a
           JOIN sessions_mentorat s ON a.session_id = s.id
           WHERE s.mentor_id=%s""",
        (uid,), fetchone=True
    )
    avis_list = query(
        """SELECT a.note, a.commentaire, a.created_at, u.nom, u.prenom, u.photo
           FROM avis a JOIN users u ON a.auteur_id = u.id
           JOIN sessions_mentorat s ON a.session_id = s.id
           WHERE s.mentor_id=%s ORDER BY a.created_at DESC LIMIT 5""",
        (uid,), fetchall=True
    )
    user['competences'] = competences
    user['disponibilites'] = disponibilites
    user['note_moy'] = float(avg_avis['moy']) if avg_avis['moy'] else None
    user['nb_avis'] = avg_avis['total']
    user['avis'] = avis_list
    return jsonify(user), 200


@users_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    uid = session['user_id']
    data = request.get_json()
    query(
        """UPDATE users SET nom=%s, prenom=%s, telephone=%s, filiere_id=%s,
           niveau=%s, bio=%s, centre_interet=%s WHERE id=%s""",
        (data.get('nom'), data.get('prenom'), data.get('telephone'),
         data.get('filiere_id'), data.get('niveau'),
         data.get('bio', ''), data.get('centre_interet', ''), uid),
        commit=True
    )
    # Mise à jour compétences
    if 'competences' in data:
        query("DELETE FROM competences WHERE user_id=%s", (uid,), commit=True)
        for comp in data['competences']:
            query("INSERT INTO competences (user_id, matiere_id, type, niveau) VALUES (%s,%s,%s,%s)",
                  (uid, comp['matiere_id'], comp['type'], comp.get('niveau', 'intermediaire')), commit=True)
    # Mise à jour disponibilités
    if 'disponibilites' in data:
        query("DELETE FROM disponibilites WHERE user_id=%s", (uid,), commit=True)
        for d in data['disponibilites']:
            query("INSERT INTO disponibilites (user_id, jour, heure_debut, heure_fin) VALUES (%s,%s,%s,%s)",
                  (uid, d['jour'], d['heure_debut'], d['heure_fin']), commit=True)
    return jsonify({'message': 'Profil mis à jour'}), 200


@users_bp.route('/profile/photo', methods=['POST'])
@login_required
def upload_photo():
    uid = session['user_id']
    if 'photo' not in request.files:
        return jsonify({'error': 'Aucun fichier'}), 400
    file = request.files['photo']
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        return jsonify({'error': 'Format non autorisé'}), 400
    filename = f"{uid}_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    url = f"/assets/uploads/{filename}"
    query("UPDATE users SET photo=%s WHERE id=%s", (url, uid), commit=True)
    return jsonify({'photo': url}), 200


@users_bp.route('/disponibilites', methods=['GET', 'POST', 'DELETE'])
@login_required
def disponibilites():
    uid = session['user_id']
    if request.method == 'GET':
        dispos = query("SELECT * FROM disponibilites WHERE user_id=%s", (uid,), fetchall=True)
        return jsonify(dispos), 200
    elif request.method == 'POST':
        data = request.get_json()
        query("INSERT INTO disponibilites (user_id, jour, heure_debut, heure_fin) VALUES (%s,%s,%s,%s)",
              (uid, data['jour'], data['heure_debut'], data['heure_fin']), commit=True)
        return jsonify({'message': 'Disponibilité ajoutée'}), 201
    elif request.method == 'DELETE':
        query("DELETE FROM disponibilites WHERE user_id=%s", (uid,), commit=True)
        return jsonify({'message': 'Disponibilités supprimées'}), 200

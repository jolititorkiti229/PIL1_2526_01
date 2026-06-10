from flask import Blueprint, request, jsonify, session
from backend.utils.db import query
from backend.utils.auth import login_required

mentorat_bp = Blueprint('mentorat', __name__)


@mentorat_bp.route('/', methods=['GET'])
@login_required
def list_mentorat():
    """Lister toutes les offres/demandes avec filtres optionnels."""
    type_filter = request.args.get('type')  # 'offre' ou 'demande'
    matiere_id = request.args.get('matiere_id')
    filiere = request.args.get('filiere')
    niveau = request.args.get('niveau')

    sql = """SELECT m.id, m.type, m.description, m.format, m.statut, m.date_creation,
                    mat.nom as matiere, mat.id as matiere_id,
                    u.id as user_id, u.nom, u.prenom, u.photo, u.niveau,
                    f.nom as filiere
             FROM mentorat m
             JOIN matieres mat ON m.matiere_id = mat.id
             JOIN users u ON m.user_id = u.id
             JOIN filieres f ON u.filiere_id = f.id
             WHERE m.statut = 'ouverte'"""
    params = []

    if type_filter:
        sql += " AND m.type=%s"
        params.append(type_filter)
    if matiere_id:
        sql += " AND m.matiere_id=%s"
        params.append(matiere_id)
    if filiere:
        sql += " AND f.nom=%s"
        params.append(filiere)
    if niveau:
        sql += " AND u.niveau=%s"
        params.append(niveau)

    sql += " ORDER BY m.date_creation DESC"
    results = query(sql, params, fetchall=True)
    return jsonify(results), 200


@mentorat_bp.route('/mes', methods=['GET'])
@login_required
def mes_mentorats():
    uid = session['user_id']
    results = query(
        """SELECT m.id, m.type, m.description, m.format, m.statut, m.date_creation,
                  mat.nom as matiere, mat.id as matiere_id
           FROM mentorat m
           JOIN matieres mat ON m.matiere_id = mat.id
           WHERE m.user_id=%s ORDER BY m.date_creation DESC""",
        (uid,), fetchall=True
    )
    return jsonify(results), 200


@mentorat_bp.route('/', methods=['POST'])
@login_required
def create_mentorat():
    uid = session['user_id']
    data = request.get_json()
    required = ['type', 'matiere_id', 'format']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'Champ manquant: {f}'}), 400

    mid = query(
        """INSERT INTO mentorat (user_id, type, matiere_id, description, format)
           VALUES (%s, %s, %s, %s, %s)""",
        (uid, data['type'], data['matiere_id'], data.get('description', ''), data['format']),
        commit=True
    )

    # Notifier les utilisateurs compatibles
    _notifier_matching(uid, data['type'], data['matiere_id'])

    return jsonify({'message': 'Offre/demande créée', 'id': mid}), 201


@mentorat_bp.route('/<int:mid>', methods=['PUT'])
@login_required
def update_mentorat(mid):
    uid = session['user_id']
    existing = query("SELECT id FROM mentorat WHERE id=%s AND user_id=%s", (mid, uid), fetchone=True)
    if not existing:
        return jsonify({'error': 'Non trouvé'}), 404
    data = request.get_json()
    query(
        "UPDATE mentorat SET statut=%s WHERE id=%s",
        (data.get('statut', 'ouverte'), mid), commit=True
    )
    return jsonify({'message': 'Mis à jour'}), 200


@mentorat_bp.route('/<int:mid>', methods=['DELETE'])
@login_required
def delete_mentorat(mid):
    uid = session['user_id']
    query("DELETE FROM mentorat WHERE id=%s AND user_id=%s", (mid, uid), commit=True)
    return jsonify({'message': 'Supprimé'}), 200


@mentorat_bp.route('/correspondances', methods=['GET'])
@login_required
def mes_correspondances():
    """Les correspondances acceptées pour l'utilisateur connecté."""
    uid = session['user_id']
    results = query(
        """SELECT sm.id, sm.date_session, sm.format, sm.statut,
                  u_mentor.id as mentor_id, u_mentor.nom as mentor_nom,
                  u_mentor.prenom as mentor_prenom, u_mentor.photo as mentor_photo,
                  u_mentore.id as mentore_id, u_mentore.nom as mentore_nom,
                  u_mentore.prenom as mentore_prenom, u_mentore.photo as mentore_photo
           FROM sessions_mentorat sm
           JOIN users u_mentor ON sm.mentor_id = u_mentor.id
           JOIN users u_mentore ON sm.mentore_id = u_mentore.id
           WHERE sm.mentor_id=%s OR sm.mentore_id=%s
           ORDER BY sm.date_session DESC""",
        (uid, uid), fetchall=True
    )
    return jsonify(results), 200


def _notifier_matching(user_id, type_annonce, matiere_id):
    """Notifie les utilisateurs avec compétences complémentaires."""
    if type_annonce == 'offre':
        # Chercher ceux qui ont cette matière en point faible
        cibles = query(
            """SELECT DISTINCT user_id FROM competences
               WHERE matiere_id=%s AND type='faible' AND user_id!=%s""",
            (matiere_id, user_id), fetchall=True
        )
    else:
        # Chercher ceux qui ont cette matière en point fort
        cibles = query(
            """SELECT DISTINCT user_id FROM competences
               WHERE matiere_id=%s AND type='fort' AND user_id!=%s""",
            (matiere_id, user_id), fetchall=True
        )

    auteur = query("SELECT nom, prenom FROM users WHERE id=%s", (user_id,), fetchone=True)
    matiere = query("SELECT nom FROM matieres WHERE id=%s", (matiere_id,), fetchone=True)

    if auteur and matiere:
        for cible in cibles[:20]:  # Max 20 notifications
            contenu = f"{auteur['prenom']} {auteur['nom']} a publié une {'offre' if type_annonce == 'offre' else 'demande'} de mentorat en {matiere['nom']}."
            query(
                "INSERT INTO notifications (user_id, titre, contenu) VALUES (%s,%s,%s)",
                (cible['user_id'], 'Nouvelle offre/demande de mentorat', contenu),
                commit=True
            )

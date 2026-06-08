from flask import Blueprint, request, jsonify, session
from backend.utils.db import query
from backend.utils.auth import login_required

matching_bp = Blueprint('matching', __name__)

# Pondérations de l'algorithme
W_COMPETENCE = 0.50
W_DISPONIBILITE = 0.30
W_FILIERE = 0.20


def calculer_score(mentor_id, mentore_id):
    """
    Calcule un score de compatibilité entre un mentor et un mentoré.
    Score total = 50% compétences + 30% disponibilités + 20% filière
    """
    # --- Score compétences ---
    # Matières fortes du mentor
    forts_mentor = set(
        r['matiere_id'] for r in
        query("SELECT matiere_id FROM competences WHERE user_id=%s AND type='fort'",
              (mentor_id,), fetchall=True)
    )
    # Matières faibles du mentoré
    faibles_mentore = set(
        r['matiere_id'] for r in
        query("SELECT matiere_id FROM competences WHERE user_id=%s AND type='faible'",
              (mentore_id,), fetchall=True)
    )

    if forts_mentor and faibles_mentore:
        intersection = forts_mentor & faibles_mentore
        union = forts_mentor | faibles_mentore
        comp_score = (len(intersection) / len(union)) * 100
    else:
        comp_score = 0.0

    # --- Score disponibilités ---
    dispos_mentor = query(
        "SELECT jour, heure_debut, heure_fin FROM disponibilites WHERE user_id=%s",
        (mentor_id,), fetchall=True
    )
    dispos_mentore = query(
        "SELECT jour, heure_debut, heure_fin FROM disponibilites WHERE user_id=%s",
        (mentore_id,), fetchall=True
    )

    chevauchements = 0
    for dm in dispos_mentor:
        for dme in dispos_mentore:
            if dm['jour'] == dme['jour']:
                debut_max = max(str(dm['heure_debut']), str(dme['heure_debut']))
                fin_min = min(str(dm['heure_fin']), str(dme['heure_fin']))
                if fin_min > debut_max:
                    chevauchements += 1

    total_dispos = max(len(dispos_mentor), len(dispos_mentore), 1)
    dispo_score = min((chevauchements / total_dispos) * 100, 100)

    # --- Score filière ---
    info_mentor = query("SELECT filiere_id, niveau FROM users WHERE id=%s", (mentor_id,), fetchone=True)
    info_mentore = query("SELECT filiere_id, niveau FROM users WHERE id=%s", (mentore_id,), fetchone=True)

    filiere_score = 0.0
    if info_mentor and info_mentore:
        if info_mentor['filiere_id'] == info_mentore['filiere_id']:
            filiere_score = 100.0
        else:
            filiere_score = 30.0  # Filières différentes mais compatibles

    # Score total pondéré
    total = (comp_score * W_COMPETENCE +
             dispo_score * W_DISPONIBILITE +
             filiere_score * W_FILIERE)

    return round(total, 2), round(comp_score, 2), round(dispo_score, 2), round(filiere_score, 2)


@matching_bp.route('/suggestions', methods=['GET'])
@login_required
def get_suggestions():
    """Retourne les meilleurs mentors suggérés pour l'utilisateur connecté."""
    uid = session['user_id']
    role = request.args.get('role', 'mentore')  # 'mentore' ou 'mentor'
    limit = int(request.args.get('limit', 10))
    matiere_id = request.args.get('matiere_id')
    filiere_filter = request.args.get('filiere')
    niveau_filter = request.args.get('niveau')
    dispo_filter = request.args.get('disponibilite')  # 'Toutes' ou jour

    # Récupérer tous les autres utilisateurs
    sql = """SELECT DISTINCT u.id FROM users u
             JOIN filieres f ON u.filiere_id = f.id
             WHERE u.id != %s"""
    params = [uid]

    if filiere_filter and filiere_filter != 'Toutes les filières':
        sql += " AND f.nom=%s"
        params.append(filiere_filter)
    if niveau_filter and niveau_filter != 'Tous les niveaux':
        sql += " AND u.niveau=%s"
        params.append(niveau_filter)

    if role == 'mentore':
        # Je cherche un mentor : l'autre doit avoir des points forts
        sql += """ AND u.id IN (SELECT user_id FROM competences WHERE type='fort')"""
    else:
        sql += """ AND u.id IN (SELECT user_id FROM competences WHERE type='faible')"""

    candidats = query(sql, params, fetchall=True)

    resultats = []
    for c in candidats:
        cid = c['id']
        if role == 'mentore':
            score, cs, ds, fs = calculer_score(cid, uid)
        else:
            score, cs, ds, fs = calculer_score(uid, cid)

        if score < 5:
            continue

        user_info = query(
            """SELECT u.id, u.nom, u.prenom, u.photo, u.niveau, u.bio,
                      f.nom as filiere
               FROM users u JOIN filieres f ON u.filiere_id=f.id
               WHERE u.id=%s""",
            (cid,), fetchone=True
        )
        competences = query(
            """SELECT m.nom as matiere, c.type, c.niveau
               FROM competences c JOIN matieres m ON c.matiere_id=m.id
               WHERE c.user_id=%s""",
            (cid,), fetchall=True
        )
        dispos = query(
            "SELECT jour, heure_debut, heure_fin FROM disponibilites WHERE user_id=%s",
            (cid,), fetchall=True
        )
        avg_note = query(
            """SELECT AVG(a.note) as moy FROM avis a
               JOIN sessions_mentorat s ON a.session_id=s.id
               WHERE s.mentor_id=%s""",
            (cid,), fetchone=True
        )

        # Filtre matière
        matieres_cid = [c['matiere'] for c in competences]
        if matiere_id:
            mat = query("SELECT nom FROM matieres WHERE id=%s", (matiere_id,), fetchone=True)
            if mat and mat['nom'] not in matieres_cid:
                continue

        # Filtre disponibilité
        if dispo_filter and dispo_filter != 'Toutes':
            jours_dispo = [d['jour'] for d in dispos]
            if dispo_filter not in jours_dispo:
                continue

        resultats.append({
            **user_info,
            'score': score,
            'competence_score': cs,
            'disponibilite_score': ds,
            'filiere_score': fs,
            'competences': competences,
            'disponibilites': dispos,
            'note_moy': float(avg_note['moy']) if avg_note['moy'] else None
        })

        # Sauvegarder en base
        if role == 'mentore':
            _save_matching(cid, uid, score, cs, ds, fs)
        else:
            _save_matching(uid, cid, score, cs, ds, fs)

    resultats.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(resultats[:limit]), 200


def _save_matching(mentor_id, mentore_id, score, cs, ds, fs):
    # Mettre à jour ou insérer
    existing = query(
        "SELECT id FROM matching WHERE mentor_id=%s AND mentore_id=%s",
        (mentor_id, mentore_id), fetchone=True
    )
    if existing:
        query(
            """UPDATE matching SET score=%s, competence_score=%s,
               disponibilite_score=%s, filiere_score=%s WHERE id=%s""",
            (score, cs, ds, fs, existing['id']), commit=True
        )
    else:
        query(
            """INSERT INTO matching (mentor_id, mentore_id, score, competence_score,
               disponibilite_score, filiere_score) VALUES (%s,%s,%s,%s,%s,%s)""",
            (mentor_id, mentore_id, score, cs, ds, fs), commit=True
        )

from flask import Blueprint, request, jsonify, session
from .model import db, Mentorat
from datetime import datetime

mentorat_bp = Blueprint('mentorat', __name__)


# ─────────────────────────────────────────
# CREATE — Publier une offre ou une demande
# ─────────────────────────────────────────
@mentorat_bp.route('/mentorat', methods=['POST'])
def creer_mentorat():
    data = request.get_json()
    # On récupère les données envoyées par le frontend

    # Vérification des champs obligatoires
    if not data.get('type') or not data.get('format'):
        return jsonify({'erreur': 'type et format sont obligatoires'}), 400

    nouveau = Mentorat(
        user_id     = session.get('user_id'),
        matiere_id  = data.get('matiere_id'),
        type        = data['type'],
        description = data.get('description', ''),
        format      = data['format'],
        statut      = 'actif',
    )
    db.session.add(nouveau)
    # On ajoute l'objet à la session SQLAlchemy (pas encore en BDD)
    db.session.commit()
    # Maintenant c'est sauvegardé en BDD

    return jsonify(nouveau.to_dict()), 201
    # 201 = Created


# ─────────────────────────────────────────
# READ — Lister les offres et demandes
# ─────────────────────────────────────────
@mentorat_bp.route('/mentorat', methods=['GET'])
def lister_mentorats():
    type_filtre    = request.args.get('type')
    # Ex: /mentorat?type=offre
    format_filtre  = request.args.get('format')
    matiere_filtre = request.args.get('matiere_id')

    # On part des mentorats non supprimés
    query = Mentorat.query.filter_by(is_deleted=False, statut='actif')

    # On applique les filtres si présents
    if type_filtre:
        query = query.filter_by(type=type_filtre)
    if format_filtre:
        query = query.filter_by(format=format_filtre)
    if matiere_filtre:
        query = query.filter_by(matiere_id=matiere_filtre)

    mentorats = query.order_by(Mentorat.date_creation.desc()).all()
    # .all() exécute la requête et retourne une liste

    return jsonify([m.to_dict() for m in mentorats]), 200
    # On convertit chaque objet en dictionnaire JSON


# ─────────────────────────────────────────
# READ — Voir un seul mentorat par son id
# ─────────────────────────────────────────
@mentorat_bp.route('/mentorat/<int:id>', methods=['GET'])
def voir_mentorat(id):
    m = Mentorat.query.filter_by(id=id, is_deleted=False).first()
    # .first() retourne le premier résultat ou None

    if not m:
        return jsonify({'erreur': 'Mentorat introuvable'}), 404

    return jsonify(m.to_dict()), 200


# ─────────────────────────────────────────
# UPDATE — Modifier son mentorat
# ─────────────────────────────────────────
@mentorat_bp.route('/mentorat/<int:id>', methods=['PUT'])
def modifier_mentorat(id):
    m = Mentorat.query.filter_by(id=id, is_deleted=False).first()

    if not m:
        return jsonify({'erreur': 'Mentorat introuvable'}), 404

    # Vérifier que c'est bien l'auteur qui modifie
    if m.user_id != session.get('user_id'):
        return jsonify({'erreur': 'Non autorisé'}), 403

    data = request.get_json()

    # On met à jour uniquement les champs envoyés
    if 'type'        in data: m.type        = data['type']
    if 'description' in data: m.description = data['description']
    if 'format'      in data: m.format      = data['format']
    if 'statut'      in data: m.statut      = data['statut']
    if 'matiere_id'  in data: m.matiere_id  = data['matiere_id']

    db.session.commit()

    return jsonify(m.to_dict()), 200


# ─────────────────────────────────────────
# DELETE — Supprimer son mentorat (soft)
# ─────────────────────────────────────────
@mentorat_bp.route('/mentorat/<int:id>', methods=['DELETE'])
def supprimer_mentorat(id):
    m = Mentorat.query.filter_by(id=id, is_deleted=False).first()

    if not m:
        return jsonify({'erreur': 'Mentorat introuvable'}), 404

    # Vérifier que c'est bien l'auteur qui supprime
    if m.user_id != session.get('user_id'):
        return jsonify({'erreur': 'Non autorisé'}), 403

    m.soft_delete()
    # On ne supprime pas vraiment — on met is_deleted=True
    db.session.commit()

    return jsonify({'message': 'Mentorat supprimé'}), 200
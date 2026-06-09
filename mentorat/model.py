from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Mentorat(db.Model):
    __tablename__ = 'mentorat'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # L'utilisateur qui publie l'offre ou la demande
    matiere_id    = db.Column(db.Integer, db.ForeignKey('matieres.id'), nullable=True)
    # La matière concernée par ce mentorat
    type          = db.Column(db.String(10), nullable=False)
    # 'offre' = je propose mon aide | 'demande' = je cherche de l'aide
    description   = db.Column(db.Text, default='')
    # Description libre écrite par l'utilisateur
    format        = db.Column(db.String(15), nullable=False)
    # 'online', 'presentiel' ou 'les_deux'
    statut        = db.Column(db.String(10), default='actif')
    # 'actif' = visible | 'ferme' = plus disponible | 'en_cours' = mentorat démarré
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    # Rempli automatiquement à la création
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)
    # Mis à jour automatiquement à chaque modification
    is_deleted    = db.Column(db.Boolean, default=False)
    # False = visible | True = supprimé (soft delete)
    deleted_at    = db.Column(db.DateTime, nullable=True)
    # Date de suppression, vide si pas supprimé

    def soft_delete(self):
        """Suppression douce — ne supprime pas vraiment de la BDD"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'envoyer en JSON"""
        return {
            'id':            self.id,
            'user_id':       self.user_id,
            'matiere_id':    self.matiere_id,
            'type':          self.type,
            'description':   self.description,
            'format':        self.format,
            'statut':        self.statut,
            'date_creation': self.date_creation.isoformat(),
        }

    def __repr__(self):
        return f"<Mentorat {self.type} - user:{self.user_id}>"
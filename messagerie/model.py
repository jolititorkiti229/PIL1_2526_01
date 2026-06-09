from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Conversation(db.Model):
    __tablename__ = 'conversations'

    id          = db.Column(db.Integer, primary_key=True)
    user1_id    = db.Column(db.Integer, nullable=False)
    user2_id    = db.Column(db.Integer, nullable=False)
    cree_le     = db.Column(db.DateTime, default=datetime.utcnow)
    #la date est remplie automatiquement au moment de l'enregistrement.

    # Lien vers les messages de cette conversation
    messages    = db.relationship('Message', backref='conversation', lazy=True)
    #depuis une conversation, accéder directement à tous ses messages avec conversation.messages. SQLAlchemy fait la jointure automatiquement.

class Message(db.Model):
    __tablename__ = 'messages'

    id              = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False) #c'est le lien entre les deux tables. Chaque message appartient à une conversation via cet identifiant.
    expediteur_id   = db.Column(db.Integer, nullable=False)
    contenu         = db.Column(db.Text, nullable=False)
    envoye_le       = db.Column(db.DateTime, default=datetime.utcnow)
    lu              = db.Column(db.Boolean, default=False)
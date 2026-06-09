# On importe les fonctions SocketIO dont on a besoin
# emit : envoyer un événement
# join_room : rejoindre une salle
# leave_room : quitter une salle
from flask_socketio import emit, join_room, leave_room

# On importe socketio et db depuis le fichier principal de l'app
# Ce fichier sera créé par le chef de projet (Membre 1)
# Pour l'instant on l'importera lors de l'intégration
from flask_socketio import SocketIO

# On importe nos modèles
from models import db, Message, Conversation

# On importe session pour savoir qui est connecté
from flask import session

# On crée l'instance SocketIO
# cors_allowed_origins="*" autorise les connexions depuis n'importe quelle origine
# utile en développement local
socketio = SocketIO(cors_allowed_origins="*")


# ---------------------------------------------------------------
# ÉVÉNEMENT 1 — Connexion d'un utilisateur
# ---------------------------------------------------------------

# @socketio.on('connect') se déclenche automatiquement
# quand un navigateur établit la connexion WebSocket
@socketio.on('connect')
def handle_connect():

    # On récupère l'ID de l'utilisateur connecté
    user_id = session.get('user_id', 1)

    # On affiche un message dans le terminal du serveur
    # print() en Flask s'affiche dans le terminal où tu as lancé l'app
    # Très utile pour déboguer
    print(f"Utilisateur {user_id} connecté via WebSocket")


# ---------------------------------------------------------------
# ÉVÉNEMENT 2 — Rejoindre une conversation
# ---------------------------------------------------------------

# Cet événement est déclenché par JavaScript quand l'utilisateur
# clique sur une conversation dans la liste
# data contiendra : { 'conversation_id': 1 }
@socketio.on('rejoindre_conversation')
def handle_rejoindre(data):

    user_id = session.get('user_id', 1)

    # On récupère l'ID de la conversation depuis les données reçues
    conv_id = data.get('conversation_id')

    # On vérifie que cet utilisateur a le droit d'être dans cette conversation
    # Sécurité : on ne peut pas rejoindre n'importe quelle room
    conversation = Conversation.query.filter_by(id=conv_id).filter(
        (Conversation.user1_id == user_id) |
        (Conversation.user2_id == user_id)
    ).first()

    # Si la conversation n'existe pas ou ne lui appartient pas, on arrête
    if not conversation:
        # emit sans room envoie uniquement à l'expéditeur
        emit('erreur', {'message': 'Conversation introuvable'})
        return

    # On construit le nom de la room à partir de l'ID de la conversation
    # conv_1, conv_2, conv_3... chaque conversation a sa room unique
    nom_room = f"conv_{conv_id}"

    # join_room ajoute ce client WebSocket à la room
    # À partir de maintenant, il recevra tous les messages émis dans cette room
    join_room(nom_room)

    print(f"Utilisateur {user_id} a rejoint la room {nom_room}")

    # On confirme à l'utilisateur qu'il a bien rejoint la conversation
    emit('conversation_rejointe', {'conversation_id': conv_id})


# ---------------------------------------------------------------
# ÉVÉNEMENT 3 — Quitter une conversation
# ---------------------------------------------------------------

# Déclenché quand l'utilisateur clique sur une autre conversation
# On quitte l'ancienne room avant d'en rejoindre une nouvelle
# data contiendra : { 'conversation_id': 1 }
@socketio.on('quitter_conversation')
def handle_quitter(data):

    user_id = session.get('user_id', 1)
    conv_id = data.get('conversation_id')

    # On construit le nom de la room
    nom_room = f"conv_{conv_id}"

    # leave_room retire ce client de la room
    # Il ne recevra plus les messages émis dans cette room
    leave_room(nom_room)

    print(f"Utilisateur {user_id} a quitté la room {nom_room}")


# ---------------------------------------------------------------
# ÉVÉNEMENT 4 — Envoyer un message (le plus important)
# ---------------------------------------------------------------

# C'est l'événement central de la messagerie
# Déclenché quand l'utilisateur clique sur "Envoyer"
# data contiendra : { 'conversation_id': 1, 'contenu': 'Salut !' }
@socketio.on('envoyer_message')
def handle_message(data):

    user_id = session.get('user_id', 1)
    conv_id = data.get('conversation_id')
    contenu = data.get('contenu', '').strip()

    # strip() supprime les espaces au début et à la fin
    # On vérifie que le message n'est pas vide
    if not contenu:
        emit('erreur', {'message': 'Message vide'})
        return

    # Vérification de sécurité : l'utilisateur appartient à cette conversation
    conversation = Conversation.query.filter_by(id=conv_id).filter(
        (Conversation.user1_id == user_id) |
        (Conversation.user2_id == user_id)
    ).first()

    if not conversation:
        emit('erreur', {'message': 'Accès interdit'})
        return

    # On crée le nouveau message dans la base de données
    nouveau_message = Message(
        conversation_id = conv_id,
        expediteur_id   = user_id,
        contenu         = contenu,
        # lu=False par défaut : le destinataire ne l'a pas encore lu
    )

    # On l'ajoute à la session SQLAlchemy
    db.session.add(nouveau_message)

    # On valide : le message est maintenant en base de données
    db.session.commit()

    # On construit le nom de la room
    nom_room = f"conv_{conv_id}"

    # On émet l'événement "nouveau_message" à TOUS les membres de la room
    # room=nom_room : uniquement les gens dans cette conversation reçoivent le message
    # include_self=True : l'expéditeur lui-même reçoit aussi l'événement
    # (pour que son message apparaisse dans sa propre interface)
    emit('nouveau_message', {
        'id'            : nouveau_message.id,
        'contenu'       : nouveau_message.contenu,
        'expediteur_id' : user_id,
        'envoye_le'     : nouveau_message.envoye_le.strftime('%H:%M'),
        'conversation_id': conv_id
    }, room=nom_room, include_self=True)

    print(f"Message envoyé dans {nom_room} par user {user_id} : {contenu}")


# ---------------------------------------------------------------
# ÉVÉNEMENT 5 — Déconnexion
# ---------------------------------------------------------------

# Déclenché automatiquement quand le navigateur ferme la connexion
# (fermeture d'onglet, déconnexion réseau, etc.)
@socketio.on('disconnect')
def handle_disconnect():

    user_id = session.get('user_id', 1)
    print(f"Utilisateur {user_id} déconnecté")
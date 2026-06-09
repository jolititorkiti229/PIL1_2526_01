# On importe Blueprint depuis Flask
# Blueprint c'est comme un "mini-Flask" pour organiser les routes par module
# Au lieu de tout mettre dans un seul fichier, chaque membre a son Blueprint
from flask import Blueprint, render_template, request, jsonify, session

# On importe les modèles qu'on a définis à l'étape 2
from models import db, Conversation, Message

# On crée le Blueprint pour la messagerie
# "chat" c'est le nom interne de ce Blueprint
# il sera enregistré dans l'application principale par le chef de projet
chat_bp = Blueprint('chat', __name__)


# ---------------------------------------------------------------
# ROUTE 1 — Afficher la page de messagerie
# ---------------------------------------------------------------

# Cette route répond aux requêtes GET sur l'URL /chat
# Autrement dit : quand un utilisateur visite /chat dans son navigateur
@chat_bp.route('/chat')
def messagerie():

    # On récupère l'ID de l'utilisateur connecté depuis la session
    # La session c'est une mémoire temporaire côté serveur
    # Le Membre 3 (authentification) y aura mis user_id lors de la connexion
    # Pour l'instant on met 1 en dur pour tester sans authentification
    user_id = session.get('user_id', 1)

    # On cherche toutes les conversations où cet utilisateur participe
    # filter() c'est le WHERE en SQL
    # | c'est le OR : soit il est user1, soit il est user2
    conversations = Conversation.query.filter(
        (Conversation.user1_id == user_id) |
        (Conversation.user2_id == user_id)
    ).all()

    # On envoie la page HTML en lui passant les conversations trouvées
    # render_template va chercher le fichier dans le dossier templates/
    return render_template('chat/messagerie.html', conversations=conversations)


# ---------------------------------------------------------------
# ROUTE 2 — Retourner la liste des conversations (format JSON)
# ---------------------------------------------------------------

# Cette route est appelée par JavaScript, pas par le navigateur directement
# Elle retourne des données JSON, pas du HTML
@chat_bp.route('/chat/conversations')
def liste_conversations():

    # Même logique : on récupère l'utilisateur connecté
    user_id = session.get('user_id', 1)

    # On récupère toutes ses conversations
    conversations = Conversation.query.filter(
        (Conversation.user1_id == user_id) |
        (Conversation.user2_id == user_id)
    ).all()

    # On transforme chaque conversation en dictionnaire Python
    # parce que JSON ne comprend pas les objets SQLAlchemy directement
    resultat = []
    for conv in conversations:

        # Pour chaque conversation, on cherche le dernier message envoyé
        # order_by trie par date, desc() = du plus récent au plus ancien
        # first() prend uniquement le premier résultat (donc le plus récent)
        dernier_message = Message.query.filter_by(
            conversation_id=conv.id
        ).order_by(Message.envoye_le.desc()).first()

        # On détermine l'ID de l'interlocuteur
        # Si je suis user1, mon interlocuteur est user2, et vice versa
        if conv.user1_id == user_id:
            interlocuteur_id = conv.user2_id
        else:
            interlocuteur_id = conv.user1_id

        # On compte les messages non lus dans cette conversation
        # filter_by filtre par conversation_id
        # filter filtre en plus sur lu=False et expediteur != moi
        # (pas besoin de compter mes propres messages comme non lus)
        non_lus = Message.query.filter_by(
            conversation_id=conv.id,
            lu=False
        ).filter(Message.expediteur_id != user_id).count()

        # On ajoute ce dictionnaire à la liste des résultats
        resultat.append({
            'id'                : conv.id,
            'interlocuteur_id'  : interlocuteur_id,
            'dernier_message'   : dernier_message.contenu if dernier_message else '',
            'date'              : dernier_message.envoye_le.strftime('%H:%M') if dernier_message else '',
            'non_lus'           : non_lus
        })

    # jsonify transforme le dictionnaire Python en réponse JSON
    # c'est ce que JavaScript recevra de l'autre côté
    return jsonify(resultat)


# ---------------------------------------------------------------
# ROUTE 3 — Retourner les messages d'une conversation
# ---------------------------------------------------------------

# <int:conv_id> est une variable dans l'URL
# Si l'URL est /chat/conversation/5/messages, alors conv_id vaudra 5
# int: signifie que Flask vérifie que c'est bien un entier
@chat_bp.route('/chat/conversation/<int:conv_id>/messages')
def messages_conversation(conv_id):

    user_id = session.get('user_id', 1)

    # On vérifie que l'utilisateur a le droit de voir cette conversation
    # Un utilisateur ne doit voir QUE ses propres conversations
    # C'est une règle de sécurité fondamentale
    conversation = Conversation.query.filter_by(id=conv_id).filter(
        (Conversation.user1_id == user_id) |
        (Conversation.user2_id == user_id)
    ).first()

    # Si la conversation n'existe pas ou n'appartient pas à cet utilisateur
    # on retourne une erreur 403 (accès interdit)
    if not conversation:
        return jsonify({'erreur': 'Accès interdit'}), 403

    # On récupère tous les messages, triés du plus ancien au plus récent
    # C'est l'ordre naturel d'une conversation : on lit du haut vers le bas
    messages = Message.query.filter_by(
        conversation_id=conv_id
    ).order_by(Message.envoye_le.asc()).all()

    # On marque tous les messages reçus comme lus
    # filter() : uniquement les messages qui ne viennent pas de moi
    # update() met à jour tous les résultats en une seule requête SQL
    Message.query.filter_by(
        conversation_id=conv_id,
        lu=False
    ).filter(
        Message.expediteur_id != user_id
    ).update({'lu': True})

    # On valide les changements dans la base de données
    # Sans ce commit(), les modifications sont perdues
    db.session.commit()

    # On transforme chaque message en dictionnaire
    resultat = []
    for msg in messages:

        # strftime formate la date en texte lisible
        # %H:%M donne l'heure au format 14:35
        resultat.append({
            'id'            : msg.id,
            'contenu'       : msg.contenu,
            'expediteur_id' : msg.expediteur_id,
            'envoye_le'     : msg.envoye_le.strftime('%H:%M'),
            # True si c'est moi qui ai envoyé ce message
            # utile côté HTML pour aligner mes messages à droite
            'est_moi'       : msg.expediteur_id == user_id
        })

    return jsonify(resultat)


# ---------------------------------------------------------------
# ROUTE 4 — Créer une nouvelle conversation
# ---------------------------------------------------------------

# methods=['POST'] : cette route n'accepte que les requêtes POST
# On ne crée pas une conversation en visitant une URL (GET)
# On la crée en envoyant des données (POST)
@chat_bp.route('/chat/conversation/new', methods=['POST'])
def nouvelle_conversation():

    user_id = session.get('user_id', 1)

    # On récupère les données envoyées en JSON par JavaScript
    # request.json lit le corps de la requête POST
    data = request.get_json()

    # L'ID de la personne avec qui on veut ouvrir une conversation
    interlocuteur_id = data.get('interlocuteur_id')

    # Sécurité : on ne peut pas ouvrir une conversation avec soi-même
    if interlocuteur_id == user_id:
        return jsonify({'erreur': 'Action impossible'}), 400

    # On vérifie si une conversation existe déjà entre ces deux personnes
    # Peu importe l'ordre : (moi, lui) ou (lui, moi) c'est pareil
    conversation_existante = Conversation.query.filter(
        ((Conversation.user1_id == user_id) & (Conversation.user2_id == interlocuteur_id)) |
        ((Conversation.user1_id == interlocuteur_id) & (Conversation.user2_id == user_id))
    ).first()

    # Si elle existe déjà, on la retourne directement sans en créer une nouvelle
    if conversation_existante:
        return jsonify({'conversation_id': conversation_existante.id})

    # Sinon on crée une nouvelle conversation
    nouvelle_conv = Conversation(
        user1_id=user_id,
        user2_id=interlocuteur_id
    )

    # On l'ajoute à la session SQLAlchemy (pas encore en base)
    db.session.add(nouvelle_conv)

    # On valide : c'est maintenant que l'INSERT SQL est exécuté
    db.session.commit()

    # On retourne l'ID de la nouvelle conversation
    # JavaScript en aura besoin pour rediriger l'utilisateur
    return jsonify({'conversation_id': nouvelle_conv.id}), 201
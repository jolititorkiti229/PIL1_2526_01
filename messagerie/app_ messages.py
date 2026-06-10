from flask import Blueprint, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from backend.utils.db import query
from backend.utils.auth import login_required
from backend import socketio

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    uid = session['user_id']
    convs = query(
        """SELECT c.id, c.created_at,
                  u.id as interlocuteur_id, u.nom, u.prenom, u.photo,
                  (SELECT message FROM messages WHERE conversation_id=c.id ORDER BY date_envoi DESC LIMIT 1) as dernier_message,
                  (SELECT date_envoi FROM messages WHERE conversation_id=c.id ORDER BY date_envoi DESC LIMIT 1) as derniere_date,
                  (SELECT COUNT(*) FROM messages WHERE conversation_id=c.id AND sender_id!=%s AND lu=0) as non_lus
           FROM conversations c
           JOIN conversation_users cu1 ON c.id=cu1.conversation_id AND cu1.user_id=%s
           JOIN conversation_users cu2 ON c.id=cu2.conversation_id AND cu2.user_id!=%s
           JOIN users u ON cu2.user_id=u.id
           ORDER BY derniere_date DESC""",
        (uid, uid, uid), fetchall=True
    )
    return jsonify(convs), 200


@messages_bp.route('/conversations/<int:cid>/messages', methods=['GET'])
@login_required
def get_messages(cid):
    uid = session['user_id']
    # Vérifier que l'user est dans la conversation
    member = query("SELECT id FROM conversation_users WHERE conversation_id=%s AND user_id=%s", (cid, uid), fetchone=True)
    if not member:
        return jsonify({'error': 'Accès refusé'}), 403

    msgs = query(
        """SELECT m.id, m.message, m.date_envoi, m.lu,
                  u.id as sender_id, u.nom, u.prenom, u.photo
           FROM messages m JOIN users u ON m.sender_id = u.id
           WHERE m.conversation_id=%s ORDER BY m.date_envoi ASC""",
        (cid,), fetchall=True
    )
    # Marquer comme lus
    query("UPDATE messages SET lu=1 WHERE conversation_id=%s AND sender_id!=%s AND lu=0",
          (cid, uid), commit=True)
    return jsonify(msgs), 200


@messages_bp.route('/conversations/start/<int:other_uid>', methods=['POST'])
@login_required
def start_conversation(other_uid):
    uid = session['user_id']
    if uid == other_uid:
        return jsonify({'error': 'Impossible'}), 400

    # Chercher conv existante
    existing = query(
        """SELECT cu1.conversation_id as id FROM conversation_users cu1
           JOIN conversation_users cu2 ON cu1.conversation_id=cu2.conversation_id
           WHERE cu1.user_id=%s AND cu2.user_id=%s""",
        (uid, other_uid), fetchone=True
    )
    if existing:
        return jsonify({'conversation_id': existing['id']}), 200

    # Créer nouvelle conv
    cid = query("INSERT INTO conversations () VALUES ()", commit=True)
    query("INSERT INTO conversation_users (conversation_id, user_id) VALUES (%s,%s)", (cid, uid), commit=True)
    query("INSERT INTO conversation_users (conversation_id, user_id) VALUES (%s,%s)", (cid, other_uid), commit=True)
    return jsonify({'conversation_id': cid}), 201


@messages_bp.route('/conversations/<int:cid>/send', methods=['POST'])
@login_required
def send_message_http(cid):
    uid = session['user_id']
    data = request.get_json()
    msg_text = data.get('message', '').strip()
    if not msg_text:
        return jsonify({'error': 'Message vide'}), 400

    member = query("SELECT id FROM conversation_users WHERE conversation_id=%s AND user_id=%s", (cid, uid), fetchone=True)
    if not member:
        return jsonify({'error': 'Accès refusé'}), 403

    mid = query(
        "INSERT INTO messages (conversation_id, sender_id, message) VALUES (%s,%s,%s)",
        (cid, uid, msg_text), commit=True
    )

    # Notifier l'autre user
    other = query(
        "SELECT user_id FROM conversation_users WHERE conversation_id=%s AND user_id!=%s",
        (cid, uid), fetchone=True
    )
    sender = query("SELECT nom, prenom FROM users WHERE id=%s", (uid,), fetchone=True)
    if other and sender:
        query(
            "INSERT INTO notifications (user_id, titre, contenu) VALUES (%s,%s,%s)",
            (other['user_id'], 'Nouveau message',
             f"{sender['prenom']} {sender['nom']} vous a envoyé un message."),
            commit=True
        )

    msg = query(
        """SELECT m.id, m.message, m.date_envoi, m.lu,
                  u.id as sender_id, u.nom, u.prenom, u.photo
           FROM messages m JOIN users u ON m.sender_id=u.id
           WHERE m.id=%s""",
        (mid,), fetchone=True
    )

    # Émettre via Socket.IO
    socketio.emit('new_message', msg, room=f'conv_{cid}')
    return jsonify(msg), 201


# === Socket.IO Events ===
@socketio.on('join_conversation')
def on_join(data):
    cid = data.get('conversation_id')
    join_room(f'conv_{cid}')


@socketio.on('leave_conversation')
def on_leave(data):
    cid = data.get('conversation_id')
    leave_room(f'conv_{cid}')

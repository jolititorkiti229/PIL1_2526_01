from flask import Blueprint, jsonify, session
from backend.utils.db import query
from backend.utils.auth import login_required

notif_bp = Blueprint('notifications', __name__)


@notif_bp.route('/', methods=['GET'])
@login_required
def get_notifications():
    uid = session['user_id']
    notifs = query(
        "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 50",
        (uid,), fetchall=True
    )
    return jsonify(notifs), 200


@notif_bp.route('/non-lues', methods=['GET'])
@login_required
def count_non_lues():
    uid = session['user_id']
    result = query(
        "SELECT COUNT(*) as count FROM notifications WHERE user_id=%s AND lu=0",
        (uid,), fetchone=True
    )
    return jsonify({'count': result['count']}), 200


@notif_bp.route('/marquer-lues', methods=['POST'])
@login_required
def marquer_lues():
    uid = session['user_id']
    query("UPDATE notifications SET lu=1 WHERE user_id=%s", (uid,), commit=True)
    return jsonify({'message': 'Notifications marquées comme lues'}), 200


@notif_bp.route('/<int:nid>/lue', methods=['POST'])
@login_required
def marquer_une_lue(nid):
    uid = session['user_id']
    query("UPDATE notifications SET lu=1 WHERE id=%s AND user_id=%s", (nid, uid), commit=True)
    return jsonify({'message': 'Notification lue'}), 200

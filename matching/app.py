"""
IFRI_MentorLink - Application Flask
Projet intégrateur L1 IFRI 2025-2026
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
import mysql.connector
import hashlib
import os
import secrets
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mentorlink_secret_key_ifri_2026')

# Dossier upload photos
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─── CONFIG DB ────────────────────────────────────────────────────────────────
# Après
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DB', 'mentorlink'),
    'charset': 'utf8mb4',
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
        g.db.autocommit = True
    else:
        try:
            g.db.ping(reconnect=True, attempts=3, delay=1)
        except mysql.connector.Error:
            g.db = mysql.connector.connect(**DB_CONFIG)
            g.db.autocommit = True
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query(sql, args=(), one=False, commit=False):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, args)
    if commit:
        db.commit()
        return cur.lastrowid
    rv = cur.fetchone() if one else cur.fetchall()
    cur.close()
    return rv

def hash_password(pwd):
    return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

# ─── AUTH DECORATOR ───────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' not in session:
        return None
    user = query("SELECT u.*, f.nom as filiere FROM users u JOIN filieres f ON u.filiere_id=f.id WHERE u.id=%s",
                 (session['user_id'],), one=True)
    return user

def get_unread_counts(user_id):
    msgs = query("SELECT COUNT(*) as c FROM messages m JOIN conversation_users cu ON m.conversation_id=cu.conversation_id WHERE cu.user_id=%s AND m.sender_id!=%s AND m.lu=0",
                 (user_id, user_id), one=True)
    notifs = query("SELECT COUNT(*) as c FROM notifications WHERE user_id=%s AND lu=0", (user_id,), one=True)
    return msgs['c'] if msgs else 0, notifs['c'] if notifs else 0

# ─── ALGORITHME DE MATCHING ──────────────────────────────────────────────────
def calc_score(user_id, mentor_id):
    user_faibles = {r['matiere_id'] for r in query("SELECT matiere_id FROM competences WHERE user_id=%s AND type='faible'", (user_id,))}
    mentor_forts = {r['matiere_id'] for r in query("SELECT matiere_id FROM competences WHERE user_id=%s AND type='fort'", (mentor_id,))}
    comp_score = 0
    if user_faibles and mentor_forts:
        match = user_faibles & mentor_forts
        comp_score = (len(match) / max(len(user_faibles), 1)) * 50
    user_dispos = query("SELECT jour FROM disponibilites WHERE user_id=%s", (user_id,))
    mentor_dispos = query("SELECT jour FROM disponibilites WHERE user_id=%s", (mentor_id,))
    dispo_score = 0
    if user_dispos and mentor_dispos:
        user_jours = {d['jour'] for d in user_dispos}
        mentor_jours = {d['jour'] for d in mentor_dispos}
        jours_communs = user_jours & mentor_jours
        if jours_communs:
            dispo_score = min(30, len(jours_communs) * 10)
    u1 = query("SELECT filiere_id FROM users WHERE id=%s", (user_id,), one=True)
    u2 = query("SELECT filiere_id FROM users WHERE id=%s", (mentor_id,), one=True)
    filiere_score = 20 if u1 and u2 and u1['filiere_id'] == u2['filiere_id'] else 10
    total = round(comp_score + dispo_score + filiere_score)
    return min(total, 100), round(comp_score), round(dispo_score), round(filiere_score)

# ─── ROUTES PUBLIQUES ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifiant = request.form['identifiant'].strip()
        password = hash_password(request.form['password'])
        user = query("SELECT * FROM users WHERE (email=%s OR telephone=%s) AND password=%s",
                     (identifiant, identifiant, password), one=True)
        if user:
            session['user_id'] = user['id']
            session['user_nom'] = f"{user['prenom']} {user['nom']}"
            flash(f"Bienvenue, {user['prenom']} !", 'success')
            return redirect(url_for('dashboard'))
        flash('Identifiant ou mot de passe incorrect.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    filieres = query("SELECT * FROM filieres ORDER BY nom")
    matieres = query("SELECT * FROM matieres ORDER BY nom")
    if request.method == 'POST':
        nom = request.form['nom'].strip()
        prenom = request.form['prenom'].strip()
        email = request.form['email'].strip().lower()
        telephone = request.form['telephone'].strip()
        filiere_id = request.form['filiere_id']
        niveau = request.form['niveau']
        pwd = request.form['password']
        pwd2 = request.form['password2']
        if pwd != pwd2:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('register.html', filieres=filieres, matieres=matieres)
        exists = query("SELECT id FROM users WHERE email=%s OR telephone=%s", (email, telephone), one=True)
        if exists:
            flash('Email ou téléphone déjà utilisé.', 'error')
            return render_template('register.html', filieres=filieres, matieres=matieres)
        hashed = hash_password(pwd)
        uid = query("INSERT INTO users (nom,prenom,email,telephone,password,filiere_id,niveau) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (nom, prenom, email, telephone, hashed, filiere_id, niveau), commit=True)
        for mid in request.form.getlist('forts'):
            query("INSERT IGNORE INTO competences (user_id,matiere_id,type) VALUES (%s,%s,'fort')", (uid, mid), commit=True)
        for mid in request.form.getlist('faibles'):
            query("INSERT IGNORE INTO competences (user_id,matiere_id,type) VALUES (%s,%s,'faible')", (uid, mid), commit=True)
        session['user_id'] = uid
        session['user_nom'] = f"{prenom} {nom}"
        flash('Compte créé avec succès ! Bienvenue sur IFRI_MentorLink 🎉', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html', filieres=filieres, matieres=matieres)

@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnecté avec succès.', 'info')
    return redirect(url_for('login'))

# ─── MOT DE PASSE OUBLIÉ ─────────────────────────────────────────────────────

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        identifiant = request.form['identifiant'].strip()
        user = query("SELECT * FROM users WHERE email=%s OR telephone=%s", (identifiant, identifiant), one=True)
        if user:
            # Générer un token unique
            token = secrets.token_urlsafe(32)
            # Stocker le token en session (simple, sans email)
            session['reset_token'] = token
            session['reset_user_id'] = user['id']
            flash('Compte trouvé ! Vous pouvez maintenant choisir un nouveau mot de passe.', 'success')
            return redirect(url_for('reset_password', token=token))
        else:
            flash('Aucun compte trouvé avec cet email ou téléphone.', 'error')
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if session.get('reset_token') != token or 'reset_user_id' not in session:
        flash('Lien invalide ou expiré.', 'error')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        pwd = request.form['password']
        pwd2 = request.form['password2']
        if pwd != pwd2:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('reset_password.html', token=token)
        if len(pwd) < 6:
            flash('Le mot de passe doit faire au moins 6 caractères.', 'error')
            return render_template('reset_password.html', token=token)
        hashed = hash_password(pwd)
        uid = session['reset_user_id']
        query("UPDATE users SET password=%s WHERE id=%s", (hashed, uid), commit=True)
        session.pop('reset_token', None)
        session.pop('reset_user_id', None)
        flash('Mot de passe modifié avec succès ! Connectez-vous.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

# ─── ROUTES PROTÉGÉES ────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    uid = user['id']
    unread_m, unread_n = get_unread_counts(uid)
    stats = {
        'offres': query("SELECT COUNT(*) as c FROM mentorat WHERE user_id=%s AND type='offre'", (uid,), one=True)['c'],
        'demandes': query("SELECT COUNT(*) as c FROM mentorat WHERE user_id=%s AND type='demande'", (uid,), one=True)['c'],
        'correspondances': query("SELECT COUNT(*) as c FROM conversation_users WHERE user_id=%s", (uid,), one=True)['c'],
    }
    all_users = query("SELECT u.id, u.nom, u.prenom, f.nom as filiere, u.niveau, u.photo FROM users u JOIN filieres f ON u.filiere_id=f.id WHERE u.id!=%s LIMIT 20", (uid,))
    suggestions = []
    for u in all_users:
        score, _, _, _ = calc_score(uid, u['id'])
        if score > 20:
            suggestions.append({**u, 'score': score})
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    suggestions = suggestions[:3]
    notifs = query("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 5", (uid,))
    activites = []
    for n in notifs:
        activites.append({
            'icon': '💬' if 'message' in n['contenu'].lower() else '🔔',
            'couleur': 'blue',
            'contenu': n['contenu'],
            'temps': n['created_at'].strftime('%d/%m à %H:%M') if n['created_at'] else ''
        })
    return render_template('dashboard.html', user=user, stats=stats, suggestions=suggestions,
                           activites=activites, unread_messages=unread_m, unread_notifications=unread_n,
                           active_page='dashboard')

@app.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    user = get_current_user()
    uid = user['id']
    unread_m, unread_n = get_unread_counts(uid)
    filieres = query("SELECT * FROM filieres ORDER BY nom")
    matieres = query("SELECT * FROM matieres ORDER BY nom")

    if request.method == 'POST':
        nom = request.form['nom'].strip()
        prenom = request.form['prenom'].strip()
        email = request.form['email'].strip().lower()
        telephone = request.form['telephone'].strip()
        filiere_id = request.form['filiere_id']
        niveau = request.form['niveau']
        bio = request.form.get('bio', '').strip()
        centre = request.form.get('centre_interet', '').strip()

        # Gestion photo de profil
        photo_filename = user.get('photo')
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                photo_filename = f"user_{uid}_{secrets.token_hex(6)}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, photo_filename))

        exists = query("SELECT id FROM users WHERE (email=%s OR telephone=%s) AND id!=%s", (email, telephone, uid), one=True)
        if exists:
            flash('Email ou téléphone déjà utilisé par un autre compte.', 'error')
        else:
            query("UPDATE users SET nom=%s,prenom=%s,email=%s,telephone=%s,filiere_id=%s,niveau=%s,bio=%s,centre_interet=%s,photo=%s WHERE id=%s",
                  (nom, prenom, email, telephone, filiere_id, niveau, bio, centre, photo_filename, uid), commit=True)
            # Mise à jour compétences
            query("DELETE FROM competences WHERE user_id=%s", (uid,), commit=True)
            forts = set(request.form.getlist('forts'))
            faibles = set(request.form.getlist('faibles')) - forts

            for mid in forts:
                query("INSERT IGNORE INTO competences (user_id,matiere_id,type) VALUES (%s,%s,'fort')", (uid, mid), commit=True)
            for mid in faibles:
                query("INSERT IGNORE INTO competences (user_id,matiere_id,type) VALUES (%s,%s,'faible')", (uid, mid), commit=True)
            flash('Profil mis à jour avec succès !', 'success')
            return redirect(url_for('profil'))
    forts_raw = query("SELECT matiere_id FROM competences WHERE user_id=%s AND type='fort'", (uid,))
    forts_ids = [r['matiere_id'] for r in forts_raw]
    faibles_raw = query("SELECT matiere_id FROM competences WHERE user_id=%s AND type='faible'", (uid,))
    faibles_ids = [r['matiere_id'] for r in faibles_raw]
    forts_noms = query("SELECT m.nom FROM competences c JOIN matieres m ON c.matiere_id=m.id WHERE c.user_id=%s AND c.type='fort'", (uid,))
    faibles_noms = query("SELECT m.nom FROM competences c JOIN matieres m ON c.matiere_id=m.id WHERE c.user_id=%s AND c.type='faible'", (uid,))
    dispos = query("SELECT * FROM disponibilites WHERE user_id=%s ORDER BY FIELD(jour,'Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche')", (uid,))

    return render_template('profil.html', user=user, filieres=filieres, matieres=matieres,
                           forts=[r['nom'] for r in forts_noms],
                           faibles=[r['nom'] for r in faibles_noms],
                           forts_ids=forts_ids, faibles_ids=faibles_ids,
                           disponibilites=dispos,
                           unread_messages=unread_m, unread_notifications=unread_n,
                           active_page='profil')

@app.route('/profil/dispo', methods=['POST'])
@login_required
def ajouter_dispo():
    uid = session['user_id']
    jour = request.form['jour']
    hd = request.form['heure_debut']
    hf = request.form['heure_fin']
    query("INSERT INTO disponibilites (user_id,jour,heure_debut,heure_fin) VALUES (%s,%s,%s,%s)", (uid, jour, hd, hf), commit=True)
    flash('Disponibilité ajoutée.', 'success')
    return redirect(url_for('profil'))

@app.route('/profil/dispo/<int:dispo_id>/supprimer', methods=['POST'])
@login_required
def supprimer_dispo(dispo_id):
    uid = session['user_id']
    query("DELETE FROM disponibilites WHERE id=%s AND user_id=%s", (dispo_id, uid), commit=True)
    flash('Disponibilité supprimée.', 'success')
    return redirect(url_for('profil'))

@app.route('/recherche')
@login_required
def recherche():
    user = get_current_user()
    uid = user['id']
    unread_m, unread_n = get_unread_counts(uid)
    matieres = query("SELECT * FROM matieres ORDER BY nom")
    filieres = query("SELECT * FROM filieres ORDER BY nom")
    matiere_id = request.args.get('matiere')
    filiere_id = request.args.get('filiere')
    niveau = request.args.get('niveau')
    jour = request.args.get('jour')
    mentors = []
    if any([matiere_id, filiere_id, niveau, jour]):
        sql = """SELECT DISTINCT u.id, u.nom, u.prenom, u.niveau, u.photo, f.nom as filiere
                 FROM users u JOIN filieres f ON u.filiere_id=f.id
                 LEFT JOIN competences c ON u.id=c.user_id
                 LEFT JOIN disponibilites d ON u.id=d.user_id
                 WHERE u.id != %s AND c.type='fort' """
        args = [uid]
        if matiere_id:
            sql += " AND c.matiere_id=%s"; args.append(matiere_id)
        if filiere_id:
            sql += " AND u.filiere_id=%s"; args.append(filiere_id)
        if niveau:
            sql += " AND u.niveau=%s"; args.append(niveau)
        if jour:
            sql += " AND d.jour=%s"; args.append(jour)
        sql += " LIMIT 30"
        raw_mentors = query(sql, args)
        for m in raw_mentors:
            score, _, _, _ = calc_score(uid, m['id'])
            comps = query("SELECT mat.nom FROM competences c JOIN matieres mat ON c.matiere_id=mat.id WHERE c.user_id=%s AND c.type='fort' LIMIT 3", (m['id'],))
            dispos = query("SELECT jour, heure_debut FROM disponibilites WHERE user_id=%s LIMIT 2", (m['id'],))
            dispo_str = ', '.join([f"{d['jour']} {d['heure_debut']}" for d in dispos])
            mentors.append({**m, 'score': score, 'competences': [c['nom'] for c in comps], 'disponibilites': dispo_str})
        mentors.sort(key=lambda x: x['score'], reverse=True)
    return render_template('recherche.html', user=user, matieres=matieres, filieres=filieres,
                           mentors=mentors, unread_messages=unread_m, unread_notifications=unread_n,
                           active_page='recherche')

@app.route('/offres')
@login_required
def offres():
    user = get_current_user()
    uid = user['id']
    unread_m, unread_n = get_unread_counts(uid)
    matieres = query("SELECT * FROM matieres ORDER BY nom")
    offres_raw = query("""SELECT m.*, mat.nom as matiere FROM mentorat m
                          JOIN matieres mat ON m.matiere_id=mat.id
                          WHERE m.user_id=%s AND m.type='offre' ORDER BY m.date_creation DESC""", (uid,))
    demandes_raw = query("""SELECT m.*, mat.nom as matiere FROM mentorat m
                            JOIN matieres mat ON m.matiere_id=mat.id
                            WHERE m.user_id=%s AND m.type='demande' ORDER BY m.date_creation DESC""", (uid,))
    return render_template('offres.html', user=user, offres=offres_raw, demandes=demandes_raw,
                           matieres=matieres, unread_messages=unread_m, unread_notifications=unread_n,
                           active_page='offres')

@app.route('/mentorat/creer', methods=['POST'])
@login_required
def creer_mentorat():
    uid = session['user_id']
    type_ = request.form['type']
    matiere_id = request.form['matiere_id']
    description = request.form.get('description', '').strip()
    format_ = request.form['format']
    query("INSERT INTO mentorat (user_id,type,matiere_id,description,format) VALUES (%s,%s,%s,%s,%s)",
          (uid, type_, matiere_id, description, format_), commit=True)
    query("INSERT INTO notifications (user_id,titre,contenu) VALUES (%s,%s,%s)",
          (uid, 'Publication réussie', f'Votre {type_} de mentorat a été publiée.'), commit=True)
    flash('Publication créée avec succès !', 'success')
    return redirect(url_for('offres'))

@app.route('/mentorat/<int:mentorat_id>/supprimer', methods=['POST'])
@login_required
def supprimer_mentorat(mentorat_id):
    uid = session['user_id']
    query("DELETE FROM mentorat WHERE id=%s AND user_id=%s", (mentorat_id, uid), commit=True)
    flash('Supprimé avec succès.', 'success')
    return redirect(url_for('offres'))

@app.route('/messagerie')
@app.route('/messagerie/<int:conv_id>')
@login_required
def messagerie(conv_id=None):
    user = get_current_user()
    uid = user['id']
    unread_m, unread_n = get_unread_counts(uid)
    conv_ids = query("SELECT conversation_id FROM conversation_users WHERE user_id=%s", (uid,))
    conversations = []
    for c in conv_ids:
        cid = c['conversation_id']
        other = query("""SELECT u.id,u.nom,u.prenom,u.photo,f.nom as filiere,u.niveau
                         FROM conversation_users cu JOIN users u ON cu.user_id=u.id
                         JOIN filieres f ON u.filiere_id=f.id
                         WHERE cu.conversation_id=%s AND cu.user_id!=%s LIMIT 1""", (cid, uid), one=True)
        if not other:
            continue
        last_msg = query("SELECT message, date_envoi FROM messages WHERE conversation_id=%s ORDER BY date_envoi DESC LIMIT 1", (cid,), one=True)
        unread = query("SELECT COUNT(*) as c FROM messages WHERE conversation_id=%s AND sender_id!=%s AND lu=0", (cid, uid), one=True)
        conversations.append({
            'id': cid,
            'other_user': other,
            'last_message': last_msg['message'][:40] + '...' if last_msg and len(last_msg['message']) > 40 else (last_msg['message'] if last_msg else ''),
            'last_time': last_msg['date_envoi'].strftime('%H:%M') if last_msg and last_msg['date_envoi'] else '',
            'unread': unread['c'] if unread else 0,
        })
    active_conv = None
    messages = []
    if conv_id:
        access = query("SELECT * FROM conversation_users WHERE conversation_id=%s AND user_id=%s", (conv_id, uid), one=True)
        if access:
            other = query("""SELECT u.id,u.nom,u.prenom,u.photo,f.nom as filiere,u.niveau
                             FROM conversation_users cu JOIN users u ON cu.user_id=u.id
                             JOIN filieres f ON u.filiere_id=f.id
                             WHERE cu.conversation_id=%s AND cu.user_id!=%s LIMIT 1""", (conv_id, uid), one=True)
            active_conv = {'id': conv_id, 'other_user': other}
            messages = query("SELECT * FROM messages WHERE conversation_id=%s ORDER BY date_envoi ASC", (conv_id,))
            query("UPDATE messages SET lu=1 WHERE conversation_id=%s AND sender_id!=%s", (conv_id, uid), commit=True)
    return render_template('messagerie.html', user=user, conversations=conversations,
                           active_conv=active_conv, messages=messages, active_conv_id=conv_id,
                           unread_messages=unread_m, unread_notifications=unread_n,
                           active_page='messagerie')

@app.route('/messagerie/<int:conv_id>/envoyer', methods=['POST'])
@login_required
def envoyer_message(conv_id):
    uid = session['user_id']
    message = request.form['message'].strip()
    if message:
        query("INSERT INTO messages (conversation_id,sender_id,message) VALUES (%s,%s,%s)", (conv_id, uid, message), commit=True)
        other = query("SELECT user_id FROM conversation_users WHERE conversation_id=%s AND user_id!=%s LIMIT 1", (conv_id, uid), one=True)
        if other:
            user = get_current_user()
            query("INSERT INTO notifications (user_id,titre,contenu) VALUES (%s,%s,%s)",
                  (other['user_id'], 'Nouveau message', f"{user['prenom']} {user['nom']} vous a envoyé un message."), commit=True)
    return redirect(url_for('messagerie', conv_id=conv_id))

@app.route('/contacter/<int:user_id>')
@login_required
def contacter(user_id):
    uid = session['user_id']
    existing = query("""SELECT cu1.conversation_id FROM conversation_users cu1
                        JOIN conversation_users cu2 ON cu1.conversation_id=cu2.conversation_id
                        WHERE cu1.user_id=%s AND cu2.user_id=%s LIMIT 1""", (uid, user_id), one=True)
    if existing:
        return redirect(url_for('messagerie', conv_id=existing['conversation_id']))
    cid = query("INSERT INTO conversations () VALUES ()", commit=True)
    query("INSERT INTO conversation_users (conversation_id,user_id) VALUES (%s,%s)", (cid, uid), commit=True)
    query("INSERT INTO conversation_users (conversation_id,user_id) VALUES (%s,%s)", (cid, user_id), commit=True)
    return redirect(url_for('messagerie', conv_id=cid))

@app.route('/profil/<int:user_id>')
@login_required
def profil_user(user_id):
    user = get_current_user()
    uid = user['id']
    unread_m, unread_n = get_unread_counts(uid)
    mentor = query("SELECT u.*, f.nom as filiere FROM users u JOIN filieres f ON u.filiere_id=f.id WHERE u.id=%s", (user_id,), one=True)
    if not mentor:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('dashboard'))
    forts_raw = query("SELECT m.nom FROM competences c JOIN matieres m ON c.matiere_id=m.id WHERE c.user_id=%s AND c.type='fort'", (user_id,))
    dispos = query("SELECT * FROM disponibilites WHERE user_id=%s ORDER BY FIELD(jour,'Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche')", (user_id,))
    avis_list = query("""SELECT av.note, av.commentaire, u.prenom, u.nom
                         FROM avis av JOIN users u ON av.auteur_id=u.id
                         WHERE av.session_id IN (SELECT id FROM sessions_mentorat WHERE mentor_id=%s OR mentore_id=%s)
                         ORDER BY av.created_at DESC LIMIT 5""", (user_id, user_id))
    avis_moyen = query("SELECT AVG(a.note) as moy, COUNT(*) as nb FROM avis a WHERE a.session_id IN (SELECT id FROM sessions_mentorat WHERE mentor_id=%s OR mentore_id=%s)", (user_id, user_id), one=True)
    for av in avis_list:
        av['auteur'] = f"{av['prenom']} {av['nom']}"
    score_compat, _, _, _ = calc_score(uid, user_id)
    return render_template('profil_user.html', user=user, mentor=mentor,
                           forts=[r['nom'] for r in forts_raw], disponibilites=dispos,
                           avis_list=avis_list,
                           avis_moyen=avis_moyen['moy'] if avis_moyen and avis_moyen['moy'] else None,
                           nb_avis=avis_moyen['nb'] if avis_moyen else 0,
                           score_compat=score_compat,
                           unread_messages=unread_m, unread_notifications=unread_n,
                           active_page='')

@app.route('/correspondances')
@login_required
def correspondances():
    return redirect(url_for('messagerie'))

@app.route('/demande/<int:mentor_id>', methods=['POST'])
@login_required
def creer_demande(mentor_id):
    uid = session['user_id']
    mat = query("SELECT id FROM matieres LIMIT 1", one=True)
    if mat:
        query("INSERT INTO mentorat (user_id,type,matiere_id,format) VALUES (%s,'demande',%s,'hybride')", (uid, mat['id']), commit=True)
    user = get_current_user()
    query("INSERT INTO notifications (user_id,titre,contenu) VALUES (%s,%s,%s)",
          (mentor_id, 'Nouvelle demande de mentorat', f"{user['prenom']} {user['nom']} vous a envoyé une demande de mentorat."), commit=True)
    flash('Demande de mentorat envoyée !', 'success')
    return redirect(url_for('profil_user', user_id=mentor_id))

@app.route('/notifications')
@login_required
def notifications():
    user = get_current_user()
    uid = user['id']
    unread_m, unread_n = get_unread_counts(uid)
    notifs = query("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 50", (uid,))
    return render_template('notifications.html', user=user, notifs=notifs,
                           unread_messages=unread_m, unread_notifications=unread_n,
                           active_page='notifications')

@app.route('/notifications/marquer', methods=['POST'])
@login_required
def marquer_notifs_lues():
    uid = session['user_id']
    query("UPDATE notifications SET lu=1 WHERE user_id=%s", (uid,), commit=True)
    flash('Toutes les notifications marquées comme lues.', 'success')
    return redirect(url_for('notifications'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

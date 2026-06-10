-- CREATE DATABASE mentorlink CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE mentorlink;

CREATE TABLE filieres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE matieres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telephone VARCHAR(20) NOT NULL UNIQUE,
    password TEXT NOT NULL,

    filiere_id INT NOT NULL,

    niveau ENUM(
        'Licence1',
        'Licence2',
        'Licence3',
        'Master1',
        'Master2'
    ) NOT NULL,

    photo VARCHAR(255),
    bio TEXT,
    centre_interet TEXT,

    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (filiere_id)
    REFERENCES filieres(id)
);

CREATE TABLE competences (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,
    matiere_id INT NOT NULL,

    type ENUM('fort','faible') NOT NULL,

    niveau ENUM(
        'debutant',
        'intermediaire',
        'avance'
    ) DEFAULT 'intermediaire',

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    FOREIGN KEY (matiere_id)
    REFERENCES matieres(id)
    ON DELETE CASCADE
);

CREATE TABLE disponibilites (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    jour ENUM(
        'Lundi',
        'Mardi',
        'Mercredi',
        'Jeudi',
        'Vendredi',
        'Samedi',
        'Dimanche'
    ) NOT NULL,

    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE mentorat (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    type ENUM(
        'offre',
        'demande'
    ) NOT NULL,

    matiere_id INT NOT NULL,

    description TEXT,

    format ENUM(
        'presentiel',
        'ligne',
        'hybride'
    ) NOT NULL,

    statut ENUM(
        'ouverte',
        'en_cours',
        'terminee',
        'annulee'
    ) DEFAULT 'ouverte',

    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    FOREIGN KEY (matiere_id)
    REFERENCES matieres(id)
);

CREATE TABLE matching (
    id INT AUTO_INCREMENT PRIMARY KEY,

    mentor_id INT NOT NULL,
    mentore_id INT NOT NULL,

    score DECIMAL(5,2) NOT NULL,

    competence_score DECIMAL(5,2),
    disponibilite_score DECIMAL(5,2),
    filiere_score DECIMAL(5,2),

    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (mentor_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    FOREIGN KEY (mentore_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    conversation_id INT NOT NULL,
    user_id INT NOT NULL,

    UNIQUE(conversation_id, user_id),

    FOREIGN KEY (conversation_id)
    REFERENCES conversations(id)
    ON DELETE CASCADE,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,

    conversation_id INT NOT NULL,
    sender_id INT NOT NULL,

    message TEXT NOT NULL,

    lu BOOLEAN DEFAULT FALSE,

    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id)
    REFERENCES conversations(id)
    ON DELETE CASCADE,

    FOREIGN KEY (sender_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    titre VARCHAR(255),
    contenu TEXT NOT NULL,

    lu BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE sessions_mentorat (
    id INT AUTO_INCREMENT PRIMARY KEY,

    mentor_id INT NOT NULL,
    mentore_id INT NOT NULL,

    date_session DATETIME NOT NULL,

    format ENUM(
        'presentiel',
        'ligne'
    ) NOT NULL,

    statut ENUM(
        'planifiee',
        'terminee',
        'annulee'
    ) DEFAULT 'planifiee',

    commentaire TEXT,

    FOREIGN KEY (mentor_id)
    REFERENCES users(id),

    FOREIGN KEY (mentore_id)
    REFERENCES users(id)
);

CREATE TABLE avis (
    id INT AUTO_INCREMENT PRIMARY KEY,

    session_id INT NOT NULL,
    auteur_id INT NOT NULL,

    note INT NOT NULL,

    commentaire TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id)
    REFERENCES sessions_mentorat(id)
    ON DELETE CASCADE,

    FOREIGN KEY (auteur_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

INSERT INTO filieres (nom) VALUES
('IA'),
('IM'),
('GL'),
('SI'),
('SE&IoT');

INSERT INTO matieres (nom) VALUES
('Logique'),
('Algèbre linéaire '),
('Analyse et Application'),
('Analyse combinatoir et Probabilité'),
('Statistique'),
('Architecture et Topologie des réseaux informaitique'),
('Utilisation et Administration sous Windows'),
('Outils de base en informatique'),
('Algorithme'),
('Language C'),
('Déontologie'),
('TEEO'),
('Administration des réseaux sous linux'),
('Suites et série numérique'),
('Equation différentielles'),
('Projet intégrateur'),
('Théorie des graphes'),
('Recherche Opérationnelle'),
('Développement Web'),
('Infographie'),
('Algèbre relationnelle'),
('SGBD et language SQL'),
('Programation python'),
('Anglais technique');

CREATE INDEX idx_competence_user ON competences(user_id);
CREATE INDEX idx_competence_matiere ON competences(matiere_id);
CREATE INDEX idx_mentorat_user ON mentorat(user_id);
CREATE INDEX idx_mentorat_matiere ON mentorat(matiere_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
show table status ;


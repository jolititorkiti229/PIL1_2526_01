// ============================================================
// INITIALISATION
// ============================================================

// On attend que tout le HTML soit chargé avant d'exécuter quoi que ce soit
// Sans ça, getElementById() ne trouverait rien car le HTML n'est pas encore là
document.addEventListener('DOMContentLoaded', function() {


    // On récupère l'ID de l'utilisateur connecté
    // depuis la div cachée qu'on a mise dans le HTML
    // parseInt() convertit le texte "1" en nombre entier 1
    const userId = parseInt(
        document.getElementById('donnees-utilisateur').dataset.userId
    );

    // Variable qui stocke l'ID de la conversation actuellement ouverte
    // null = aucune conversation ouverte pour l'instant
    let conversationActiveId = null;


    // ============================================================
    // CONNEXION WEBSOCKET
    // ============================================================

    // On établit la connexion WebSocket avec le serveur
    // io() est fourni par la bibliothèque socket.io.min.js chargée dans le HTML
    // Sans argument, il se connecte automatiquement au même serveur
    const socket = io();

    // Cet événement se déclenche quand la connexion WebSocket est établie
    socket.on('connect', function() {
        console.log('Connecté au serveur WebSocket');
    });

    // Cet événement se déclenche si la connexion échoue ou est perdue
    socket.on('disconnect', function() {
        console.log('Déconnecté du serveur WebSocket');
    });


    // ============================================================
    // CHARGER LES CONVERSATIONS AU DÉMARRAGE
    // ============================================================

    // On appelle notre route Flask /chat/conversations
    // fetch() fait une requête HTTP depuis JavaScript sans recharger la page
    // C'est ce qu'on appelle une requête AJAX
    fetch('/chat/conversations')
        .then(function(reponse) {
            // .then() s'exécute quand le serveur répond
            // reponse.json() convertit la réponse JSON en objet JavaScript
            return reponse.json();
        })
        .then(function(conversations) {
            // conversations est maintenant un tableau d'objets JavaScript
            // On met à jour l'affichage avec ces données
            mettreAJourListeConversations(conversations);
        })
        .catch(function(erreur) {
            // .catch() s'exécute si une erreur se produit
            console.error('Erreur chargement conversations :', erreur);
        });


    // ============================================================
    // CLIC SUR UNE CONVERSATION
    // ============================================================

    // On écoute les clics sur toute la liste des conversations
    // On utilise la délégation d'événements : on écoute sur le parent
    // plutôt que sur chaque item individuellement
    // Pourquoi ? Parce que les items sont créés dynamiquement par JS
    // et n'existent pas encore au chargement de la page
    document.getElementById('conversations-liste').addEventListener('click', function(e) {

        // e.target : l'élément exact sur lequel l'utilisateur a cliqué
        // closest() remonte dans le DOM jusqu'à trouver un .conversation-item
        // Utile si l'utilisateur clique sur le texte à l'intérieur de l'item
        const item = e.target.closest('.conversation-item');

        // Si le clic n'était pas sur un item de conversation, on ignore
        if (!item) return;

        // On lit l'ID de la conversation depuis l'attribut data-conv-id
        // dataset.convId lit l'attribut data-conv-id (camelCase automatique)
        const convId = parseInt(item.dataset.convId);

        // Si on clique sur la conversation déjà ouverte, rien à faire
        if (convId === conversationActiveId) return;

        // Si une conversation était déjà ouverte, on quitte sa room
        if (conversationActiveId !== null) {
            socket.emit('quitter_conversation', {
                conversation_id: conversationActiveId
            });
        }

        // On ouvre la nouvelle conversation
        ouvrirConversation(convId);
    });


    // ============================================================
    // OUVRIR UNE CONVERSATION
    // ============================================================

    function ouvrirConversation(convId) {

        // On mémorise quelle conversation est maintenant active
        conversationActiveId = convId;

        // On masque l'état vide et on affiche la zone de chat
        document.getElementById('etat-vide').style.display = 'none';
        document.getElementById('zone-chat-active').style.display = 'flex';

        // On met en surbrillance l'item cliqué dans la liste
        // D'abord on retire la surbrillance de tous les items
        document.querySelectorAll('.conversation-item').forEach(function(item) {
            item.classList.remove('active');
        });
        // Puis on l'ajoute uniquement à celui qui vient d'être cliqué
        const itemActif = document.querySelector(`[data-conv-id="${convId}"]`);
        if (itemActif) itemActif.classList.add('active');

        // On rejoint la room SocketIO de cette conversation
        // Le serveur nous ajoutera à la room "conv_X"
        socket.emit('rejoindre_conversation', { conversation_id: convId });

        // On charge l'historique des messages via notre route Flask
        fetch(`/chat/conversation/${convId}/messages`)
            .then(function(reponse) {
                return reponse.json();
            })
            .then(function(messages) {

                // On vide la zone des messages avant d'afficher les nouveaux
                const zoneMessages = document.getElementById('zone-messages');
                zoneMessages.innerHTML = '';

                // On affiche chaque message de l'historique
                messages.forEach(function(msg) {
                    afficherMessage(msg);
                });

                // On fait défiler vers le bas pour voir les messages les plus récents
                faireDefilerVersBas();

                // On vide le badge de messages non lus pour cette conversation
                const badge = document.getElementById(`badge-${convId}`);
                if (badge) badge.textContent = '';
            })
            .catch(function(erreur) {
                console.error('Erreur chargement messages :', erreur);
            });
    }


    // ============================================================
    // RECEVOIR UN MESSAGE EN TEMPS RÉEL
    // ============================================================

    // Cet événement est déclenché par le serveur quand quelqu'un
    // envoie un message dans une room dont on est membre
    socket.on('nouveau_message', function(msg) {

        // Si le message appartient à la conversation actuellement ouverte
        // on l'affiche directement dans la zone de chat
        if (msg.conversation_id === conversationActiveId) {
            afficherMessage({
                contenu         : msg.contenu,
                expediteur_id   : msg.expediteur_id,
                envoye_le       : msg.envoye_le,
                // est_moi : vrai si c'est moi qui ai envoyé ce message
                est_moi         : msg.expediteur_id === userId
            });

            // On fait défiler vers le bas pour voir le nouveau message
            faireDefilerVersBas();

        } else {
            // Le message est dans une autre conversation (pas celle ouverte)
            // On met à jour le badge de messages non lus
            const badge = document.getElementById(`badge-${msg.conversation_id}`);
            if (badge) {
                // On récupère le nombre actuel et on ajoute 1
                const actuel = parseInt(badge.textContent) || 0;
                badge.textContent = actuel + 1;
            }
        }
    });


    // ============================================================
    // ENVOYER UN MESSAGE
    // ============================================================

    // On écoute le clic sur le bouton Envoyer
    document.getElementById('btn-envoyer').addEventListener('click', function() {
        envoyerMessage();
    });

    // On écoute aussi la touche Entrée dans le champ de texte
    // Pour envoyer sans cliquer sur le bouton
    document.getElementById('input-message').addEventListener('keypress', function(e) {
        // e.key : la touche pressée
        // 'Enter' : touche Entrée
        if (e.key === 'Enter') {
            envoyerMessage();
        }
    });

    function envoyerMessage() {

        // On récupère le texte écrit dans le champ
        const input = document.getElementById('input-message');
        const contenu = input.value.trim();

        // trim() supprime les espaces inutiles
        // Si le champ est vide ou qu'aucune conversation n'est ouverte, on arrête
        if (!contenu || conversationActiveId === null) return;

        // On envoie l'événement au serveur via SocketIO
        // Le serveur va sauvegarder le message et le diffuser à la room
        socket.emit('envoyer_message', {
            conversation_id : conversationActiveId,
            contenu         : contenu
        });

        // On vide le champ de saisie après l'envoi
        input.value = '';

        // On remet le focus sur le champ pour que l'utilisateur
        // puisse continuer à taper sans re-cliquer
        input.focus();
    }


    // ============================================================
    // FONCTIONS UTILITAIRES
    // ============================================================

    // Crée et affiche un message dans la zone de chat
    function afficherMessage(msg) {

        const zoneMessages = document.getElementById('zone-messages');

        // On crée un nouveau div pour ce message
        const div = document.createElement('div');

        // On lui donne une classe selon si c'est moi ou l'autre
        // message-moi : aligné à droite (mes messages)
        // message-autre : aligné à gauche (messages reçus)
        div.classList.add('message');
        div.classList.add(msg.est_moi ? 'message-moi' : 'message-autre');

        // On construit le contenu HTML du message
        // textContent est plus sûr que innerHTML pour afficher du texte
        // car il empêche les injections de code malveillant
        const spanContenu = document.createElement('span');
        spanContenu.classList.add('contenu-message');
        spanContenu.textContent = msg.contenu;

        const spanHeure = document.createElement('span');
        spanHeure.classList.add('heure-message');
        spanHeure.textContent = msg.envoye_le;

        // On assemble les éléments
        div.appendChild(spanContenu);
        div.appendChild(spanHeure);

        // On ajoute le message à la zone
        zoneMessages.appendChild(div);
    }

    // Met à jour la liste des conversations dans la colonne gauche
    function mettreAJourListeConversations(conversations) {

        const liste = document.getElementById('conversations-liste');
        liste.innerHTML = '';

        // Si aucune conversation, on affiche un message
        if (conversations.length === 0) {
            liste.innerHTML = '<p id="aucune-conversation">Aucune conversation.</p>';
            return;
        }

        conversations.forEach(function(conv) {

            // On crée un div pour chaque conversation
            const div = document.createElement('div');
            div.classList.add('conversation-item');
            // On stocke l'ID dans l'attribut data-conv-id
            div.dataset.convId = conv.id;

            // On construit le contenu
            div.innerHTML = `
                <div class="avatar-placeholder">
                    ${conv.interlocuteur_id}
                </div>
                <div class="conversation-info">
                    <span class="nom-interlocuteur">
                        Utilisateur ${conv.interlocuteur_id}
                    </span>
                    <span class="apercu-message">
                        ${conv.dernier_message || 'Nouvelle conversation'}
                    </span>
                </div>
                <span class="badge-non-lus" id="badge-${conv.id}">
                    ${conv.non_lus > 0 ? conv.non_lus : ''}
                </span>
            `;

            liste.appendChild(div);
        });
    }

    // Fait défiler la zone de messages vers le bas
    // Appelée après chaque nouveau message pour toujours voir le dernier
    function faireDefilerVersBas() {
        const zone = document.getElementById('zone-messages');
        // scrollTop : position de défilement actuelle
        // scrollHeight : hauteur totale du contenu
        // En mettant scrollTop = scrollHeight, on va tout en bas
        zone.scrollTop = zone.scrollHeight;
    }


// Fermeture du DOMContentLoaded
});
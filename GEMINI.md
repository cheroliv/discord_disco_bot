# Projet : Bot Discord Musical "DiscoBot"

Ce document sert de feuille de route pour le développement du bot Discord musical. Il est basé sur le document de conception initial `0084_musicbot_discord_python_post.adoc`.

## Principes Directeurs

Suite à nos échanges, le développement suivra rigoureusement les principes suivants :

1.  **Programmation Fonctionnelle** : Le cœur de la logique métier sera développé en suivant un style fonctionnel.
2.  **Gestion d'Erreurs avec Monades** : Nous utiliserons la bibliothèque `PyMonad`, en privilégiant la monade `Either` pour gérer les cas de succès et d'erreur de manière explicite et sûre, plutôt que de lever des exceptions.
3.  **Test-Driven Development (TDD/LDD)** : Chaque fonctionnalité sera précédée par des tests (unitaires et d'intégration) qui valideront le comportement attendu, y compris les logs émis.

## Objectif du Projet

Créer un bot Discord musical robuste, maintenable et évolutif, capable d'interagir avec les APIs de Spotify et YouTube. Le développement suivra une approche **Log Driven Development (LDD)** dans un paradigme fonctionnel en Python.

## Stack Technique Principale

*   **Langage :** Python
*   **Paradigme :** Programmation Fonctionnelle
*   **Librairies Clés :**
    *   `discord.py` (ou une alternative asynchrone)
    *   `PyMonade` pour la gestion des effets de bord et des erreurs.
    *   `Pydantic` pour la validation des données.
    *   `Asyncio` pour la programmation asynchrone.
    *   `Structlog` pour le logging structuré.
    *   `aiohttp` (ou `httpx`) pour les clients API asynchrones.

## Feuille de Route (Backlog)

Le projet est divisé en plusieurs épopées (Epics) et récits utilisateurs (User Stories).

### Epic 1 : Infrastructure du Bot Discord

*Valeur métier :* Mettre en place une base solide et extensible pour le bot.

*   **US 1.1 : Initialisation du Bot**
    *   [x] Le bot se connecte automatiquement au démarrage.
    *   [x] Les logs structurés documentent chaque étape de la connexion.
    *   [x] Le bot gère la reconnexion automatique en cas de déconnexion.
    *   [x] Des tests d'intégration valident la connexion et la reconnexion.
    *   [x] Mettre en place un système de commandes modulaire.
    *   [x] Centraliser la gestion des erreurs.

### Epic 2 : Intégration de Spotify

*Valeur métier :* Permettre l'accès aux métadonnées musicales de Spotify.

*   **US 2.1 : Recherche Spotify Intelligente**
    *   [x] Implémenter une commande `/search` fonctionnelle.
    *   [x] La recherche retourne des résultats pertinents avec les métadonnées (nom, artiste, durée).
    *   [x] Mettre en place un cache local (ou en mémoire) pour optimiser les requêtes répétées.
    *   [x] Gérer gracieusement les erreurs de l'API Spotify (ex: quota atteint, morceau non trouvé).
    *   [x] Sécuriser l'authentification OAuth2.
    *   [ ] Gérer les quotas de l'API.
    *   [ ] Prévoir un mécanisme de fallback en cas d'erreur réseau.

### Epic 3 : Intégration de YouTube

*Valeur métier :* Fournir l'accès au contenu audio pour la lecture.

*   **US 3.1 : Extraction YouTube Résiliente**
    *   [ ] Implémenter une méthode d'extraction audio qui respecte les ToS de YouTube.
    *   [ ] Assurer une qualité audio optimale.
    *   [ ] Gérer les cas de vidéos privées, supprimées ou avec des restrictions géographiques.
    *   [ ] Détailler les opérations d'extraction dans les logs.

### Epic 4 : Fonctionnalités Musicales

*Valeur métier :* Offrir une expérience utilisateur complète et interactive.

*   **US 4.1 : Lecture Audio**
    *   [ ] Implémenter la lecture audio dans un canal vocal Discord en haute qualité.
    *   [ ] Créer une file d'attente (queue) pour gérer les morceaux.
    *   [ ] Ajouter des commandes de base : `/play`, `/pause`, `/skip`, `/queue`.
    *   [ ] Assurer la synchronisation entre l'état du bot et les commandes utilisateurs.

## Plan de Développement Itératif

Le développement suivra des sprints de 2 semaines (estimation).

*   **Sprint 1-2 :** Infrastructure et Discord Bot Core (Epic 1)
*   **Sprint 3-4 :** Intégration Spotify avec LDD (Epic 2)
*   **Sprint 5-6 :** Intégration YouTube et stratégies de contournement (Epic 3)
*   **Sprint 7-8 :** Fonctionnalités musicales avancées (Epic 4)
*   **Sprint 9-10 :** Optimisation, déploiement et monitoring.

Ce document sera mis à jour au fur et à mesure de l'avancement du projet.

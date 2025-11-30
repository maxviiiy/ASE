# Projet : Système Distribué Client / Scheduler / Serveurs (Architecture Master–Slave)

## 🎯 Objectif Général

Développer une application réseau distribuée basée sur **sockets TCP**, exploitant :

* un **Scheduler** (Master) chargé de la coordination ;
* plusieurs **Serveurs esclaves (Slaves)** contenant des fichiers texte ;
* des **Clients** qui choisissent un fichier et comptent les occurrences d’un mot.

Le système doit illustrer :

* le fonctionnement d’un **scheduler** (planification, routage, coordination des tâches) ;
* l’architecture **Master–Slave** ;
* la gestion de connexions **concurrentes** ;
* la communication **multi-noeuds**.

---

# 🧩 Architecture Générale

```
          +--------------+
          |   Scheduler  |
          |   (Master)   |
          +-------+------+
                  ^
                  |  Réception des résultats
                  |
 Liste des fichiers     Choix du fichier
                  |
                  v
           +------+------+
           |   Client    |
           +------+------+
                  |
                  | Téléchargement du fichier
                  |
                  v
    +-------------+-------------+
    |   Serveur de Fichiers 1   |
    +---------------------------+
    |   Serveur de Fichiers 2   |
    +---------------------------+
    |   Serveur de Fichiers N   |
    +---------------------------+
```

---

# 📌 **1. Rôle du Scheduler (Master)**

Le scheduler est l’élément central :

### ✔ Il maintient une **table de routage** contenant :

* le nom de chaque fichier disponible ;
* le serveur où se trouve le fichier (IP + port) ;
* la taille du fichier (optionnel) ;

### ✔ Il accepte plusieurs connexions clients simultanément.

### ✔ Pour chaque client :

1. **Envoie la liste des fichiers disponibles**.
2. Attend que le client **choisisse un fichier**.
3. Sélectionne un **mot aléatoire** (ou envoyé par le client).
4. Transmet au client :

   * l’adresse IP & port du serveur contenant le fichier ;
   * le mot à rechercher.
5. Attend le résultat final (nombre d’occurrences).
6. **Enregistre dans history.txt** :

   ```
   [timestamp] Client X → fichier.txt → serveur 2 → mot="..." → occurrences=N
   ```

### ✔ Le scheduler doit être multi-threads.

---

# 📌 **2. Serveurs Slaves**

Chaque serveur :

* contient un sous-ensemble de fichiers texte ;
* accepte plusieurs clients en parallèle ;
* envoie **uniquement le contenu du fichier demandé** ;
* ne connaît rien des autres serveurs.

### Fonctionnement :

1. Attendre une connexion client.
2. Recevoir le nom du fichier.
3. Vérifier son existence.
4. Envoyer le contenu au client.
5. Fermer la connexion.

Chaque serveur peut charger ses fichiers dans un dictionnaire ou les lire à la demande.

---

# 📌 **3. Client**

Le client joue deux rôles :

### 🔹 Étape 1 : Interaction avec le Scheduler

1. Se connecter au scheduler.
2. Recevoir la liste des fichiers disponibles.
3. Afficher la liste à l’utilisateur.
4. Choisir un fichier.
5. Recevoir du scheduler :
   * adresse IP/port du serveur cible ;
   * un mot à rechercher.

### 🔹 Étape 2 : Interaction avec le Serveur Slave

6. Se connecter au serveur donné.
7. Envoyer le nom du fichier choisi.
8. Recevoir le contenu du fichier.
9. Compter les occurrences du mot.

### 🔹 Étape 3 : Retour vers le Scheduler

10. Envoyer le résultat au scheduler.
11. Afficher un message de fin.

---

# 📦 **4. Fichier history.txt (géré par le scheduler)**

Format recommandé :

```
[2025-01-10 12:44:21] client=192.168.1.5 fichier=data-03.txt serveur=10.0.0.12:6000 mot=\"AI\" occurrences=14
```

---

# 🇹🇬 Pipeline Big Data - Services Publics du Togo

Pipeline de données automatisé pour l'ingestion, le traitement et l'analyse des demandes de services publics au Togo.

**Version**: 2.0.0  
**Date**: Décembre 2025  
**Technologies**: Apache Airflow, Apache Spark, MongoDB, PostgreSQL, Docker

---

## 📋 Table des matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Architecture](#-architecture)
3. [Prérequis](#-prérequis)
4. [Installation rapide](#-installation-rapide-3-minutes)
5. [Installation détaillée](#-installation-détaillée)
6. [Utilisation du pipeline](#-utilisation-du-pipeline)
7. [Vérification des données](#-vérification-des-données)
8. [Requêtes SQL utiles](#-requêtes-sql-utiles)
9. [Commandes de gestion](#-commandes-de-gestion)
10. [Dépannage](#-dépannage)
11. [Structure du projet](#-structure-du-projet)
12. [Flux de données détaillé](#-flux-de-données-détaillé)
13. [Configuration avancée](#-configuration-avancée)
14. [Limites et améliorations](#-limites-et-améliorations)

---

## 🎯 Vue d'ensemble

Ce pipeline permet de :
- ✅ **Ingérer** des données hétérogènes depuis MongoDB
- ✅ **Harmoniser** 3 structures de données différentes en un schéma unique
- ✅ **Nettoyer** et enrichir les données (dates, coordonnées GPS, statuts)
- ✅ **Agréger** des statistiques par commune, type et période
- ✅ **Stocker** dans PostgreSQL pour l'analyse
- ✅ **Automatiser** l'exécution quotidienne via Airflow

### Cas d'usage
- Analyse des demandes de services publics (éclairage, voirie, assainissement)
- Tableaux de bord pour la prise de décision
- Suivi des taux de résolution par commune
- Identification des zones à forte demande

---

## 🏗️ Architecture

### Schéma global

```
┌─────────────────┐
│   Fichier JSON  │  
│  (8829 demandes)│  
└────────┬────────┘
         │ Script Python
         ↓
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    MongoDB      │ --> │   Apache Spark   │ --> │   Data Lake      │
│  (Source NoSQL) │     │   (Ingestion)    │     │  (Parquet/RAW)   │
└─────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                            │
                                                            ↓
                        ┌──────────────────┐     ┌──────────────────┐
                        │  Apache Spark    │ --> │   PostgreSQL     │
                        │  (Processing)    │     │  (Data Warehouse)│
                        └──────────────────┘     └──────────────────┘
                                                           │
                                                           ↓
                        ┌────────────────────────────────────────────┐
                        │    Tables Analytiques                      │
                        │  • demandes_cleaned (8829 lignes)         │
                        │  • stats_type_localisation                │
                        │  • stats_temporelles                      │
                        └────────────────────────────────────────────┘

                    🔄 Orchestration : Apache Airflow
                    📊 Monitoring : Interface Web Airflow
```

### Composants du système

| Composant | Image Docker | Port | Rôle |
|-----------|-------------|------|------|
| **MongoDB** | mongo:7.0 | 27017 | Base de données source (NoSQL) |
| **PostgreSQL** | postgres:15 | 5432 | Data Warehouse (analytics) |
| **Airflow Webserver** | Custom (Spark+Airflow) | 8080 | Interface d'orchestration |
| **Airflow Scheduler** | Custom (Spark+Airflow) | - | Exécution des tâches |
| **Spark** | Intégré dans Airflow | - | Traitement distribué (mode local) |

### Architecture technique

**Mode de déploiement** : Docker Compose avec 5 conteneurs
- ✅ Mode Spark **local[*]** (simplifié, sans cluster standalone)
- ✅ Tous les services sur le même réseau Docker
- ✅ Volumes persistants pour MongoDB et PostgreSQL
- ✅ Connexions sécurisées entre services

---

## 📦 Prérequis

### Obligatoire

- **Docker Desktop** >= 20.10
  - [Télécharger pour Windows](https://www.docker.com/products/docker-desktop)
  - [Télécharger pour Mac](https://www.docker.com/products/docker-desktop)
  - [Télécharger pour Linux](https://docs.docker.com/desktop/install/linux-install/)
  
- **Docker Compose** >= 2.0 (inclus dans Docker Desktop)

- **Minimum 8 Go de RAM** disponible pour Docker
  - Configuration : Docker Desktop → Settings → Resources → Memory

- **10 Go d'espace disque** libre

### Optionnel (pour développement)

- Python 3.10+ avec pip
- Git
- Un client SQL (DBeaver, pgAdmin) ou un IDE avec support PostgreSQL

### Vérification des prérequis

```bash
# Vérifier Docker
docker --version
# Attendu: Docker version 20.10.x ou plus

# Vérifier Docker Compose
docker-compose --version
# Attendu: Docker Compose version 2.x.x

# Vérifier que Docker fonctionne
docker ps
# Doit afficher les en-têtes de colonnes (peut être vide)

# Vérifier la RAM allouée
docker system info | grep "Total Memory"
# Doit afficher au moins 8 Go
```

---

## 🚀 Installation rapide (3 minutes)

### Étape 1 : Télécharger le projet

```bash
# Option A : Avec Git
git clone <URL_DU_REPO>
cd pipeline-services-publics

# Option B : Télécharger le ZIP
# Décompresser et ouvrir le terminal dans le dossier
```

### Étape 2 : Placer les données

```bash
# Copier votre fichier JSON dans le dossier data/
cp /chemin/vers/demandes_services_publics_togo.json data/

# Vérifier que le fichier est bien là
ls -lh data/demandes_services_publics_togo.json
```

**⏱️ Durée : 3-5 minutes**

Le script va automatiquement :
1. ✓ Vérifier Docker et Docker Compose
2. ✓ Nettoyer les anciens conteneurs
3. ✓ Créer la structure de dossiers
4. ✓ Télécharger le driver PostgreSQL (si absent)
5. ✓ Construire les images Docker
6. ✓ Démarrer PostgreSQL et MongoDB
7. ✓ Initialiser Airflow (base de données + utilisateur)
8. ✓ Démarrer Airflow (webserver + scheduler)
9. ✓ Charger les données dans MongoDB

### Étape 3 : Accéder à l'interface

Ouvrez votre navigateur : **http://localhost:8080**

- **Username** : `admin`
- **Password** : `admin`

---

## 🔧 Installation détaillée

### 1. Préparer l'environnement

```bash
# Créer le dossier du projet
mkdir pipeline-services-publics
cd pipeline-services-publics

# Créer la structure des sous-dossiers
mkdir -p dags logs plugins spark_jobs scripts jars data/{raw,processed} init-mongo init-postgres
```

### 2. docker-compose.yml


#### Dockerfile


#### requirements.txt

### 3. Télécharger le driver PostgreSQL

```bash
# Créer le dossier jars
mkdir -p jars

# Télécharger le driver JDBC PostgreSQL
curl -L -o jars/postgresql-42.6.0.jar \
  https://jdbc.postgresql.org/download/postgresql-42.6.0.jar
```

### 4. Placer vos fichiers

Copiez tous les fichiers fournis (DAG, scripts Spark, scripts d'initialisation) dans leurs dossiers respectifs :

```
pipeline-services-publics/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── dags/
│   └── pipeline_services_publics.py
├── spark_jobs/
│   ├── ingestion.py
│   └── processing.py
├── scripts/
│   └── load_data_to_mongo.py
├── init-mongo/
│   └── init.js
├── init-postgres/
│   └── 01_create_db.sql
└── data/
    └── demandes_services_publics_togo.json
```

### 5. Démarrer les services

```bash
# Construire les images
docker-compose build

# Démarrer tous les services
docker-compose up -d

# Vérifier que tout est démarré
docker-compose ps
```

## 📊 Utilisation du pipeline

### Accéder à Airflow

1. Ouvrir **http://localhost:8080** dans votre navigateur
2. Se connecter :
   - **Username** : `admin`
   - **Password** : `admin`

### Activer le DAG

1. Dans la liste des DAGs, trouver `pipeline_services_publics_togo`
2. Cliquer sur le **toggle** (interrupteur) pour l'activer
3. Le DAG est maintenant programmé pour s'exécuter tous les jours à 2h00

### Déclencher manuellement

#### Depuis l'interface Web

1. Cliquer sur le DAG `pipeline_services_publics_togo`
2. Cliquer sur le bouton **"Play"** (▶️) en haut à droite
3. Sélectionner **"Trigger DAG"**
4. Confirmer

#### Depuis la ligne de commande

```bash
# Méthode 1 : Via Make (recommandé)
make trigger-dag

# Méthode 2 : Commande directe
docker exec -it $(docker ps -q -f name=airflow-scheduler) \
  airflow dags trigger pipeline_services_publics_togo
```

### Suivre l'exécution

Dans l'interface Airflow :

1. **Vue "Graph"** : Visualise les dépendances entre tâches
2. **Vue "Tree"** : Affiche l'historique des exécutions
3. **Vue "Gantt"** : Montre la durée de chaque tâche
4. **Logs** : Cliquer sur une tâche → "Logs" pour voir les détails

### Étapes du pipeline (7 tâches)

| Ordre | Tâche | Durée | Description |
|-------|-------|-------|-------------|
| 1 | `load_data_to_mongo` | 10-20s | Charge le JSON dans MongoDB |
| 2 | `check_mongodb` | 5s | Vérifie la connexion et compte les documents |
| 3 | `create_directories` | 2s | Crée les dossiers de travail |
| 4 | `ingestion_mongodb` | 1-2min | Extrait depuis MongoDB → Parquet (RAW) |
| 5 | `processing_spark` | 2-3min | Nettoie, harmonise, agrège → PostgreSQL |
| 6 | `check_output` | 3s | Valide la présence des fichiers Parquet |
| 7 | `generate_report` | 1s | Affiche un rapport de succès |

**Durée totale : 4-6 minutes**

### État des tâches (codes couleur)

- 🟢 **Vert (success)** : Tâche réussie
- 🔴 **Rouge (failed)** : Tâche en échec (voir les logs)
- 🟡 **Jaune (running)** : Tâche en cours
- ⚪ **Gris (queued)** : Tâche en attente
- 🔵 **Bleu clair (upstream_failed)** : Échec d'une tâche précédente

---
## ✅ Vérification des données

### Méthode 1 : Script de vérification automatique

```bash
# Exécuter le script de vérification
chmod +x check_status.sh
./check_status.sh

# Ou avec Make
make status
```

**Sortie attendue :**
```
═══════════════════════════════════════════════════════════════
  VÉRIFICATION DU PIPELINE
═══════════════════════════════════════════════════════════════

ℹ 1. État des conteneurs Docker
mongodb  Up 5 minutes
postgres Up 5 minutes
airflow-webserver Up 5 minutes
airflow-scheduler Up 5 minutes

✓ Services Docker opérationnels

ℹ 2. Vérification MongoDB
✓ MongoDB : 8829 documents

ℹ 3. Vérification PostgreSQL
✓ PostgreSQL : 8829 lignes dans demandes_cleaned

ℹ 4. Vérification des fichiers Parquet
✓ Fichiers Parquet : 5 fichiers trouvés

═══════════════════════════════════════════════════════════════
  RÉSUMÉ
═══════════════════════════════════════════════════════════════
📊 Statistiques :
   • MongoDB    : 8829 documents
   • PostgreSQL : 8829 lignes
   • Parquet    : 5 fichiers

✓ Pipeline opérationnel ! 🎉
```

### Méthode 2 : Vérifier PostgreSQL

```bash
# Compter les enregistrements
docker exec -it $(docker ps -q -f name=postgres) \
  psql -U airflow -d airflow -c \
  "SELECT COUNT(*) FROM demandes_cleaned;"

# Voir un échantillon
docker exec -it $(docker ps -q -f name=postgres) \
  psql -U airflow -d airflow -c \
  "SELECT * FROM demandes_cleaned LIMIT 5;"

# Ou avec Make
make check-pg
```

### Méthode 3 : Vérifier MongoDB

```bash
# Compter les documents
docker exec -i $(docker ps -q -f name=mongodb) \
  mongosh -u admin -p admin123 --authenticationDatabase admin \
  --quiet --eval \
  "db.getSiblingDB('services_publics').demandes.countDocuments()"

# Ou avec Make
make check-mongo
```

### Méthode 4 : Connexion SQL interactive

```bash
# Se connecter à PostgreSQL
docker exec -it $(docker ps -q -f name=postgres) \
  psql -U airflow -d airflow

# Ou avec Make
make shell-pg
```

Dans psql :
```sql
-- Lister les tables
\dt

-- Voir le schéma de la table
\d demandes_cleaned

-- Compter les lignes
SELECT COUNT(*) FROM demandes_cleaned;

-- Quitter
\q
```

---

## 🔍 Requêtes SQL utiles

### Statistiques de base

```sql
-- Nombre total de demandes
SELECT COUNT(*) as total_demandes FROM demandes_cleaned;

-- Nombre de demandes par type de service
SELECT type_service, COUNT(*) as nb_demandes
FROM demandes_cleaned
GROUP BY type_service
ORDER BY nb_demandes DESC;

-- Top 10 des communes avec le plus de demandes
SELECT commune, COUNT(*) as nb_demandes
FROM demandes_cleaned
WHERE commune IS NOT NULL
GROUP BY commune
ORDER BY nb_demandes DESC
LIMIT 10;
```

### Analyse par statut

```sql
-- Répartition par statut
SELECT statut, COUNT(*) as nb_demandes,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pourcentage
FROM demandes_cleaned
GROUP BY statut
ORDER BY nb_demandes DESC;

-- Demandes ouvertes vs fermées par commune
SELECT commune,
       COUNT(*) as total,
       SUM(CASE WHEN statut IN ('ouverte', 'open', 'pending') THEN 1 ELSE 0 END) as ouvertes,
       SUM(CASE WHEN statut IN ('closed', 'fermée', 'resolu') THEN 1 ELSE 0 END) as fermees
FROM demandes_cleaned
WHERE commune IS NOT NULL
GROUP BY commune
ORDER BY total DESC
LIMIT 10;
```

### Analyse temporelle

```sql
-- Demandes par année
SELECT annee, COUNT(*) as nb_demandes
FROM demandes_cleaned
GROUP BY annee
ORDER BY annee DESC;

-- Demandes par mois (2025)
SELECT annee, mois, COUNT(*) as nb_demandes
FROM demandes_cleaned
WHERE annee = 2025
GROUP BY annee, mois
ORDER BY mois;

-- Demandes par jour de la semaine
SELECT jour_semaine, COUNT(*) as nb_demandes
FROM demandes_cleaned
GROUP BY jour_semaine
ORDER BY nb_demandes DESC;
```

### Tables d'agrégation

```sql
-- Statistiques par type et localisation
SELECT * FROM stats_type_localisation
ORDER BY nombre_demandes DESC
LIMIT 10;

-- Taux de résolution par commune
SELECT type_service, commune, nombre_demandes, taux_resolution
FROM stats_type_localisation
WHERE nombre_demandes > 10
ORDER BY taux_resolution DESC
LIMIT 10;

-- Évolution temporelle par type de service
SELECT annee, mois, type_service, nombre_demandes
FROM stats_temporelles
WHERE annee = 2025
ORDER BY annee DESC, mois DESC, nombre_demandes DESC;
```

---

## 🛠️ Commandes de gestion

### Avec Make (recommandé)

```bash
# Voir toutes les commandes disponibles
make help

# Démarrer les services
make start

# Arrêter les services
make stop

# Redémarrer les services
make restart

# Voir les logs en temps réel
make logs

# Voir les logs Airflow
make logs-airflow

# Vérifier l'état du pipeline
make status

# Vérifier PostgreSQL
make check-pg

# Vérifier MongoDB
make check-mongo

# Charger les données dans MongoDB
make load-data

# Déclencher le DAG manuellement
make trigger-dag

# Exécuter manuellement l'ingestion Spark
make run-ingestion

# Exécuter manuellement le processing Spark
make run-processing

# Accéder au shell Airflow
make shell-airflow

# Accéder au shell PostgreSQL
make shell-pg

# Accéder au shell MongoDB
make shell-mongo

# Backup PostgreSQL
make backup-pg

# Backup MongoDB
make backup-mongo

# Nettoyer complètement (⚠️ supprime les données)
make clean
```

### Sans Make

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f airflow-scheduler

# Redémarrer un service
docker-compose restart airflow-scheduler

# État des conteneurs
docker-compose ps

# Ressources utilisées
docker stats
```

---

### Problème : MongoDB vide après installation

```bash
# Vérifier si les données sont chargées
make check-mongo

# Recharger manuellement
make load-data

# Ou
docker exec -it $(docker ps -q -f name=airflow-scheduler) \
  python /opt/airflow/scripts/load_data_to_mongo.py \
  /opt/data/demandes_services_publics_togo.json
```

### Problème : PostgreSQL vide

```bash
# Vérifier les logs du DAG
docker-compose logs airflow-scheduler | grep ERROR

# Relancer le processing manuellement
make run-processing
```

### Problème : Airflow ne démarre pas

```bash
# Vérifier les logs
docker-compose logs airflow-init
docker-compose logs airflow-webserver

# Réinitialiser complètement
docker-compose down -v
docker-compose up -d
```

### Problème : Job Spark échoue

```bash
# Voir les logs détaillés
docker-compose logs airflow-scheduler | grep -A 50 "ingestion_mongodb"

# Vérifier les ressources
docker stats

# Augmenter la mémoire Docker (Settings → Resources)
```

### Problème : Erreur "Cannot connect to Docker daemon"

```bash
# Démarrer Docker Desktop
# Attendre qu'il soit complètement lancé (icône verte)

# Vérifier
docker ps
```

### Problème : Port 8080 déjà utilisé

```bash
# Changer le port dans docker-compose.yml
# Ligne : "8080:8080" → "8081:8080"

# Redémarrer
docker-compose down
docker-compose up -d

# Accéder via http://localhost:8081
```

### Logs utiles pour diagnostic

```bash
# Tous les logs
docker-compose logs --tail=100

# Logs Airflow Scheduler
docker-compose logs --tail=50 airflow-scheduler

# Logs d'une tâche spécifique
docker exec -it $(docker ps -q -f name=airflow-scheduler) \
  tail -100 /opt/airflow/logs/dag_id=pipeline_services_publics_togo/*/task_id=ingestion_mongodb/attempt=1.log
```

---

## 📁 Structure du projet

```
pipeline-services-publics/
│
├── README.md                           # Cette documentation
├── docker-compose.yml                  # Configuration Docker Compose
├── Dockerfile                          # Image Airflow + Spark
├── requirements.txt                    # Dépendances Python
│
├── dags/                               # DAGs Airflow
│   └── pipeline_services_publics.py    # DAG principal (7 tâches)
│
├── spark_jobs/                         # Jobs Spark PySpark
│   ├── ingestion.py                    # MongoDB → Parquet (RAW)
│   └── processing.py                   # Nettoyage → PostgreSQL
│
├── scripts/                            # Scripts utilitaires
│   └── load_data_to_mongo.py          # Chargement initial dans MongoDB
│
├── init-mongo/                         # Scripts d'initialisation MongoDB
│   └── init.js                         # Création de la base et index
│
├── init-postgres/                      # Scripts d'initialisation
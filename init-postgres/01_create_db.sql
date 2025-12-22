-- init-postgres/01_create_db.sql
-- Création de la base de données pour les données traitées
CREATE DATABASE services_publics_analytics;

-- Connexion à la nouvelle base
\c services_publics_analytics;

-- Table des demandes nettoyées et harmonisées
CREATE TABLE IF NOT EXISTS demandes_cleaned (
    id VARCHAR(255) PRIMARY KEY,
    date_demande TIMESTAMP NOT NULL,
    type_service VARCHAR(100) NOT NULL,
    commune VARCHAR(100),
    quartier VARCHAR(100),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    statut VARCHAR(50),
    source_donnees VARCHAR(50),
    date_ingestion TIMESTAMP,
    annee INTEGER,
    mois INTEGER,
    jour_semaine VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des agrégations par type et localisation
CREATE TABLE IF NOT EXISTS stats_type_localisation (
    id SERIAL PRIMARY KEY,
    type_service VARCHAR(100),
    commune VARCHAR(100),
    nombre_demandes INTEGER,
    demandes_ouvertes INTEGER,
    demandes_fermees INTEGER,
    taux_resolution DECIMAL(5, 2),
    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des agrégations temporelles
CREATE TABLE IF NOT EXISTS stats_temporelles (
    id SERIAL PRIMARY KEY,
    annee INTEGER,
    mois INTEGER,
    type_service VARCHAR(100),
    nombre_demandes INTEGER,
    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(annee, mois, type_service)
);

-- Index pour optimiser les requêtes
CREATE INDEX idx_demandes_date ON demandes_cleaned(date_demande);
CREATE INDEX idx_demandes_type ON demandes_cleaned(type_service);
CREATE INDEX idx_demandes_commune ON demandes_cleaned(commune);
CREATE INDEX idx_demandes_statut ON demandes_cleaned(statut);
CREATE INDEX idx_stats_type_commune ON stats_type_localisation(type_service, commune);
CREATE INDEX idx_stats_temporelles_date ON stats_temporelles(annee, mois);
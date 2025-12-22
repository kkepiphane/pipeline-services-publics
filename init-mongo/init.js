// int-mongo/init.js
db = db.getSiblingDB('services_publics');

// Création de la collection
db.createCollection('demandes');

// Création d'index pour améliorer les performances
db.demandes.createIndex({ "event.timestamp": 1 });
db.demandes.createIndex({ "created_at": 1 });
db.demandes.createIndex({ "date": 1 });
db.demandes.createIndex({ "type": 1 });
db.demandes.createIndex({ "category": 1 });

print('MongoDB initialisé avec succès');
# scripts/load_data_to_mongo.py
import json
import sys
from pymongo import MongoClient, UpdateOne
import hashlib


def generate_id(doc):
    """Génère un ID unique pour un document"""
    # Si _id existe, l'utiliser
    if "_id" in doc and doc["_id"]:
        return str(doc["_id"])

    # Si event.id existe
    if "event" in doc and isinstance(doc["event"], dict) and "id" in doc["event"]:
        return str(doc["event"]["id"])

    # Si request_id existe
    if "request_id" in doc:
        return str(doc["request_id"])

    # Sinon, générer un hash unique basé sur le contenu
    content = json.dumps(doc, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def load_data_to_mongodb(json_file_path):
    print("=" * 80)
    print("CHARGEMENT DES DONNÉES DANS MONGODB")
    print("=" * 80)

    try:
        print("\n[1/3] Connexion à MongoDB...")
        client = MongoClient(
            "mongodb://admin:admin123@mongodb:27017/services_publics?authSource=admin",
            serverSelectionTimeoutMS=5000
        )
        client.admin.command("ping")
        print("✓ Connexion établie")

        db = client["services_publics"]
        collection = db["demandes"]

        print(f"\n[2/3] Lecture du fichier: {json_file_path}")
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Le fichier JSON doit contenir un tableau")

        print(f"✓ {len(data)} documents lus")

        print("\n[3/3] Upsert des documents dans MongoDB...")
        operations = []

        for doc in data:
            # Générer un ID pour chaque document
            doc_id = generate_id(doc)
            doc["_id"] = doc_id

            operations.append(
                UpdateOne(
                    {"_id": doc_id},
                    {"$set": doc},
                    upsert=True
                )
            )

        if operations:
            result = collection.bulk_write(operations)

            print("✓ Chargement terminé")
            print(f"  - Insertés   : {result.upserted_count}")
            print(f"  - Modifiés   : {result.modified_count}")
            print(f"  - Matchés    : {result.matched_count}")
        else:
            print("⚠ Aucun document à charger")

        count = collection.count_documents({})
        print(f"\n✓ Total documents en base: {count}")

        client.close()
        return True

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    json_file = "/opt/data/demandes_services_publics_togo.json"

    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    print(f"\nFichier source: {json_file}")

    success = load_data_to_mongodb(json_file)
    sys.exit(0 if success else 1)

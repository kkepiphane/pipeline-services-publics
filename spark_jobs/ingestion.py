# spark_jobs/ingestion.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    lit, current_timestamp, col, coalesce,
    from_unixtime, to_timestamp, when
)
from pyspark.sql.types import StringType

spark = (
    SparkSession.builder
    .appName("Ingestion_MongoDB_Raw")
    .config(
        "spark.mongodb.read.connection.uri",
        "mongodb://admin:admin123@mongodb:27017/services_publics?authSource=admin"
    )
    .config("spark.mongodb.read.database", "services_publics")
    .config("spark.mongodb.read.collection", "demandes")
    .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
    .getOrCreate()
)

df = spark.read.format("mongodb").load()

print(f"📥 Nombre de documents MongoDB : {df.count()}")
print("\n📋 Schéma MongoDB :")
df.printSchema()

# Transformation avec gestion des types mixtes
df_raw = (
    df
    .withColumn(
        "id",
        coalesce(
            col("event.id"),
            col("request_id"),
            col("_id"),
            col("ref"),
            col("id")
        )
    )

    .withColumn(
        "type",
        coalesce(
            col("event.payload.type"),
            col("type"),
            col("type_demande"),
            col("service"),
            col("category"),
            col("service_type")
        )
    )

    .withColumn(
        "commune_temp",
        when(col("localisation").isNotNull(),
             col("localisation").cast(StringType())
             ).otherwise(None)
    )
    .withColumn(
        "commune",
        coalesce(
            col("event.payload.commune"),
            col("city"),
            col("location.commune"),
            when(col("commune_temp").rlike(
                "^[A-Za-zÀ-ÿ ]+$"), col("commune_temp"))
        )
    )

    .withColumn(
        "quartier",
        coalesce(
            col("event.payload.quartier"),
            col("district")
        )
    )

    .withColumn(
        "date",
        coalesce(
            # Timestamp Unix
            from_unixtime(col("event.timestamp")),
            # Format dd/MM/yyyy
            to_timestamp(col("created_at"), "dd/MM/yyyy"),
            # Format yyyy-MM-dd
            to_timestamp(col("date_creation"), "yyyy-MM-dd"),
            # Format yyyy/MM/dd
            to_timestamp(col("event_date"), "yyyy/MM/dd"),
            # Format yyyy-MM-dd
            to_timestamp(col("created"), "yyyy-MM-dd"),
            # Format yyyy-MM-dd
            to_timestamp(col("date_signalement"), "yyyy-MM-dd")
        )
    )

    .withColumn(
        "statut",
        coalesce(
            col("status"),
            col("statut"),
            col("state"),
            lit("ouverte")
        )
    )

    # Champs supplémentaires
    .withColumn("latitude", lit(None).cast("double"))
    .withColumn("longitude", lit(None).cast("double"))
    .withColumn("source_donnees", lit("mongodb"))
    .withColumn("date_ingestion", current_timestamp())
)

# Sélectionner uniquement les colonnes finales
df_final = df_raw.select(
    "id",
    "type",
    "commune",
    "quartier",
    "date",
    "latitude",
    "longitude",
    "statut",
    "source_donnees",
    "date_ingestion"
)

print("\n📄 Aperçu des données transformées (10 premières lignes) :")
df_final.show(10, truncate=False)

print("\n📊 Statistiques :")
total = df_final.count()
print(f"  - Total documents : {total}")
print(f"  - Avec type : {df_final.filter(col('type').isNotNull()).count()}")
print(
    f"  - Avec commune : {df_final.filter(col('commune').isNotNull()).count()}")
# ⚠️ Ne pas compter les dates pour éviter l'erreur de parsing

# Écriture en zone RAW (Parquet)
output_path = "/opt/data/raw/demandes"

df_final.write \
    .mode("overwrite") \
    .parquet(output_path)

print(f"\n✅ Ingestion MongoDB → RAW terminée")
print(f"✅ {total} lignes écrites dans {output_path}")

spark.stop()

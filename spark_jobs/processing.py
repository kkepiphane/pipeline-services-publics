# spark_jobs/processing.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, year, month, date_format, when, count, sum as spark_sum
)

# Session Spark
spark = (
    SparkSession.builder
    .appName("Processing_Demandes")
    .getOrCreate()
)

# Lecture des données RAW
input_path = "/opt/data/raw/demandes"

df = spark.read.parquet(input_path)
print(f"📦 Données RAW chargées : {df.count()} lignes")

# Afficher le schéma
print("\n📋 Schéma des données RAW :")
df.printSchema()

# =========================
# 1. NETTOYAGE & ENRICHISSEMENT
# =========================
df_clean = (
    df
    .withColumn("date_demande", col("date").cast("timestamp"))
    .withColumn("annee", year(col("date_demande")))
    .withColumn("mois", month(col("date_demande")))
    .withColumn("jour_semaine", date_format(col("date_demande"), "EEEE"))
    # Filtrer les lignes sans date ou sans type
    .filter(col("date_demande").isNotNull())
    .filter(col("type").isNotNull())
)

print(f"✅ Données nettoyées : {df_clean.count()} lignes")

# =========================
# 2. ÉCRITURE TABLE demandes_cleaned
# =========================
jdbc_url = "jdbc:postgresql://postgres:5432/services_publics_analytics"
jdbc_properties = {
    "user": "airflow",
    "password": "airflow",
    "driver": "org.postgresql.Driver"
}

(
    df_clean.select(
        "id",
        "date_demande",
        col("type").alias("type_service"),
        "commune",
        "quartier",
        "latitude",
        "longitude",
        "statut",
        "source_donnees",
        "date_ingestion",
        "annee",
        "mois",
        "jour_semaine"
    )
    .write
    .mode("overwrite")
    .jdbc(jdbc_url, "demandes_cleaned", properties=jdbc_properties)
)

print("✅ Table demandes_cleaned alimentée")

# =========================
# 3. STATS PAR TYPE & LOCALISATION
# =========================
stats_localisation = (
    df_clean
    .filter(col("commune").isNotNull())  # Filtrer les lignes sans commune
    .groupBy(
        col("type").alias("type_service"),
        col("commune")
    )
    .agg(
        count("*").alias("nombre_demandes"),
        spark_sum(
            when(col("statut").isin(
                ["ouverte", "open", "ouvert", "pending", "en_cours"]), 1)
            .otherwise(0)
        ).alias("demandes_ouvertes"),
        spark_sum(
            when(col("statut").isin(
                ["fermée", "closed", "resolu", "terminé"]), 1)
            .otherwise(0)
        ).alias("demandes_fermees")
    )
    .withColumn(
        "taux_resolution",
        when(col("nombre_demandes") > 0,
             (col("demandes_fermees") / col("nombre_demandes")) * 100
             ).otherwise(0)
    )
)

stats_localisation.write \
    .mode("overwrite") \
    .jdbc(jdbc_url, "stats_type_localisation", properties=jdbc_properties)

print("✅ Table stats_type_localisation alimentée")

# =========================
# 4. STATS TEMPORELLES
# =========================
stats_temporelles = (
    df_clean
    .groupBy(
        "annee",
        "mois",
        col("type").alias("type_service")
    )
    .agg(
        count("*").alias("nombre_demandes")
    )
)

stats_temporelles.write \
    .mode("overwrite") \
    .jdbc(jdbc_url, "stats_temporelles", properties=jdbc_properties)

print("✅ Table stats_temporelles alimentée")

print("\n" + "=" * 80)
print("🎉 PROCESSING TERMINÉ AVEC SUCCÈS")
print("=" * 80)

spark.stop()

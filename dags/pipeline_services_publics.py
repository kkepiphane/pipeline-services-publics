"""
DAG Airflow - Pipeline Services Publics du Togo
MongoDB → Spark → PostgreSQL
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import timedelta
from airflow.utils.dates import days_ago

# ============================================================================
# CONFIGURATION
# ============================================================================

default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="pipeline_services_publics_togo",
    default_args=default_args,
    description="Pipeline MongoDB → Spark → PostgreSQL",
    schedule_interval="0 2 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["mongodb", "spark", "etl", "datatogolab", "Service", "togo"],
)

# ============================================================================
# FONCTIONS PYTHON
# ============================================================================


def check_mongodb_connection():
    from pymongo import MongoClient

    client = MongoClient(
        "mongodb://admin:admin123@mongodb:27017/?authSource=admin",
        serverSelectionTimeoutMS=5000,
    )

    client.admin.command("ping")
    count = client["services_publics"]["demandes"].count_documents({})

    if count == 0:
        raise ValueError("La collection MongoDB est vide")

    print(f"✓ MongoDB OK ({count} documents)")
    client.close()


def check_processed_data():
    import os
    processed_path = "/opt/data/raw/demandes"

    if not os.path.exists(processed_path):
        raise Exception("Dossier RAW introuvable")

    files = os.listdir(processed_path)
    parquet_parts = [f for f in files if f.startswith("part-")]

    if not parquet_parts:
        raise Exception("Aucun fichier Parquet généré")

    print(f"✓ {len(parquet_parts)} fichiers Parquet trouvés")


def generate_report():
    print("""
    ==========================================
    PIPELINE SERVICES PUBLICS - SUCCÈS
    ==========================================
    - MongoDB vérifié
    - Ingestion Spark OK
    - Processing Spark OK
    - PostgreSQL alimenté
    ==========================================
    """)


# ============================================================================
# TÂCHES
# ============================================================================
load_mongo = BashOperator(
    task_id="load_data_to_mongo",
    bash_command="""
    python /opt/airflow/scripts/load_data_to_mongo.py \
    /opt/data/demandes_services_publics_togo.json
    """,
    dag=dag,
)

check_mongodb = PythonOperator(
    task_id="check_mongodb",
    python_callable=check_mongodb_connection,
    dag=dag,
)

create_directories = BashOperator(
    task_id="create_directories",
    bash_command="""
    mkdir -p /opt/data/raw/demandes
    echo "✓ Dossiers créés"
    """,
    dag=dag,
)

# Remplacer la tâche ingestion_mongodb par :
ingestion = BashOperator(
    task_id="ingestion_mongodb",
    bash_command="""
    /opt/spark/bin/spark-submit \
      --master local[*] \
      --packages org.mongodb.spark:mongo-spark-connector_2.12:10.5.0 \
      --executor-memory 2G \
      --driver-memory 1G \
      /opt/airflow/spark_jobs/ingestion.py
    """,
    dag=dag,
)

# Remplacer la tâche processing_spark par :
processing = BashOperator(
    task_id="processing_spark",
    bash_command="""
    /opt/spark/bin/spark-submit \
      --master local[*] \
      --jars /opt/spark-jars/postgresql-42.6.0.jar \
      --executor-memory 2G \
      --driver-memory 1G \
      /opt/airflow/spark_jobs/processing.py
    """,
    dag=dag,
)

check_output = PythonOperator(
    task_id="check_output",
    python_callable=check_processed_data,
    dag=dag,
)

report = PythonOperator(
    task_id="generate_report",
    python_callable=generate_report,
    dag=dag,
)

# ============================================================================
# DÉPENDANCES
# ============================================================================

load_mongo >> check_mongodb >> create_directories >> ingestion >> processing >> check_output >> report

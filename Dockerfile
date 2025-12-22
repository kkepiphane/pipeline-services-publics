FROM apache/airflow:2.8.0-python3.10

USER root

# Java + Spark
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk gcc wget procps && \
    apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Téléchargement Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz && \
    tar -xzf spark-3.5.1-bin-hadoop3.tgz -C /opt/ && \
    mv /opt/spark-3.5.1-bin-hadoop3 /opt/spark && \
    rm spark-3.5.1-bin-hadoop3.tgz && \
    chown -R airflow:root /opt/spark

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYSPARK_PYTHON=python3

USER airflow

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
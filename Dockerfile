FROM apache/airflow:2.3.0
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir apache-airflow-providers-mongo pymongo
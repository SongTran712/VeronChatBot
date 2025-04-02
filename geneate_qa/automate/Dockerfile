FROM apache/airflow:2.2.0
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip uninstall  --yes azure-storage && pip install -U azure-storage-blob apache-airflow-providers-microsoft-azure==1.1.0
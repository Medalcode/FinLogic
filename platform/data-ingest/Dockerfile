FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY producer.py /app/producer.py
COPY consumer.py /app/consumer.py

RUN pip install --no-cache-dir -r /app/requirements.txt

VOLUME ["/data"]

CMD ["python", "/app/consumer.py"]

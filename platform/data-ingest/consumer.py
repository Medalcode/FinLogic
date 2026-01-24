"""Consumidor de ejemplo para leer `market.prices` desde Kafka y escribir raw ndjson.
"""
import os
import time
import json
from kafka import KafkaConsumer

BROKER = os.getenv('BROKER', 'kafka:9092')
TOPIC = os.getenv('TOPIC', 'market.prices')
OUT_DIR = os.getenv('OUT_DIR', '/data/raw')

os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, 'market_prices.ndjson')

from kafka.errors import NoBrokersAvailable


def make_consumer(retries: int = 10, delay: float = 1.0):
    for attempt in range(retries):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BROKER,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            return consumer
        except NoBrokersAvailable:
            print(f'Kafka not available, retrying in {delay} s (attempt {attempt+1}/{retries})')
            time.sleep(delay)
            delay = min(delay * 2, 10)
    raise RuntimeError('Could not connect to Kafka broker')


consumer = make_consumer()

print(f"Consumer listening on {BROKER}, topic={TOPIC}")

try:
    with open(OUT_FILE, 'a') as fh:
        for msg in consumer:
            record = msg.value
            record['received_ts'] = int(time.time())
            fh.write(json.dumps(record) + '\n')
            fh.flush()
            print('wrote', record)
except KeyboardInterrupt:
    print('stopped by user')

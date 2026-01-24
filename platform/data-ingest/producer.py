"""Productor de ejemplo para enviar precios de mercado a Kafka.
Usa `kafka-python`.
"""
import os
import time
import json
import random
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

BROKER = os.getenv('BROKER', 'localhost:9092')
TOPIC = os.getenv('TOPIC', 'market.prices')


def make_producer(retries: int = 10, delay: float = 1.0):
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            return producer
        except NoBrokersAvailable:
            print(f'Kafka not available, retrying in {delay} s (attempt {attempt+1}/{retries})')
            time.sleep(delay)
            delay = min(delay * 2, 10)
    raise RuntimeError('Could not connect to Kafka broker')


def produce_sample(n: int = 20, symbol: str = 'USDCLP'):
    producer = make_producer()
    for i in range(n):
        msg = {
            'symbol': symbol,
            'ts': int(time.time()),
            'price': round(800 + random.uniform(-5, 5), 2)
        }
        producer.send(TOPIC, msg)
        producer.flush()
        print('sent', msg)
        time.sleep(0.3)


if __name__ == '__main__':
    produce_sample()

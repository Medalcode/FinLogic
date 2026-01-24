Productor de ejemplo para ingest de precios (Kafka)

Instrucciones:

1. Levantar servicios con Docker Compose:

```bash
docker-compose up -d
```

2. Instalar dependencias (opcional fuera de contenedor):

```bash
pip install -r platform/data-ingest/requirements.txt
```

3. Ejecutar productor local (usa BROKER y TOPIC por variables de entorno si es necesario):

```bash
python platform/data-ingest/producer.py
```

Topic por defecto: `market.prices`

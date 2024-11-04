import json
import logging
import os
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from concurrent.futures import ThreadPoolExecutor
import time
from prometheus_client import start_http_server, Counter, Summary

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kafka_pipeline")

# Kafka configuration
KAFKA_BROKER_URL = os.getenv('KAFKA_BROKER_URL', 'localhost:9092')
KAFKA_CONSUMER_TOPIC = os.getenv('KAFKA_CONSUMER_TOPIC', 'input_topic')
KAFKA_PRODUCER_TOPIC = os.getenv('KAFKA_PRODUCER_TOPIC', 'output_topic')
CONSUMER_GROUP = os.getenv('CONSUMER_GROUP', 'data-pipeline-group')

# Prometheus metrics
REQUEST_COUNT = Counter('requests_total', 'Total number of requests')
REQUEST_LATENCY = Summary('request_latency_seconds', 'Latency of requests in seconds')
ERROR_COUNT = Counter('errors_total', 'Total number of errors')

# Initialize Prometheus HTTP server
start_http_server(8000)

# Kafka Producer configuration
def create_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

# Kafka Consumer configuration
def create_kafka_consumer():
    return KafkaConsumer(
        KAFKA_CONSUMER_TOPIC,
        group_id=CONSUMER_GROUP,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

# Process message
@REQUEST_LATENCY.time()
def process_message(message):
    try:
        # Message processing logic
        logger.info(f"Processing message: {message}")
        result = {
            "key": message["key"],
            "value": message["value"] * 2 
        }
        return result
    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Error processing message: {e}")
        return None

# Produce message to output Kafka topic
def produce_message(producer, topic, message):
    try:
        producer.send(topic, value=message)
        producer.flush()
        logger.info(f"Produced message: {message}")
    except KafkaError as e:
        ERROR_COUNT.inc()
        logger.error(f"Failed to produce message: {e}")

# Kafka message consuming
def consume_and_process(consumer, producer):
    for message in consumer:
        REQUEST_COUNT.inc()
        data = message.value
        processed_data = process_message(data)
        if processed_data:
            produce_message(producer, KAFKA_PRODUCER_TOPIC, processed_data)

# Multi-threaded consumer
def multi_thread_consumer():
    producer = create_kafka_producer()
    consumer = create_kafka_consumer()

    with ThreadPoolExecutor(max_workers=4) as executor:
        for _ in range(4):
            executor.submit(consume_and_process, consumer, producer)

# Graceful shutdown
def shutdown_handler(signum, frame):
    logger.info("Shutting down Kafka pipeline")
    exit(0)

if __name__ == "__main__":
    logger.info("Starting Kafka data pipeline")
    try:
        multi_thread_consumer()
    except KeyboardInterrupt:
        shutdown_handler(None, None)

# Retry Mechanism
def retry_produce(producer, message, retries=5, delay=1):
    attempt = 0
    while attempt < retries:
        try:
            producer.send(KAFKA_PRODUCER_TOPIC, value=message)
            producer.flush()
            logger.info(f"Produced message after {attempt} retries: {message}")
            break
        except KafkaError as e:
            ERROR_COUNT.inc()
            attempt += 1
            logger.error(f"Retry {attempt}/{retries} failed with error: {e}")
            time.sleep(delay)

# Batch Consumer
def batch_consumer(consumer, batch_size=100):
    buffer = []
    for message in consumer:
        buffer.append(message.value)
        if len(buffer) >= batch_size:
            process_batch(buffer)
            buffer = []

def process_batch(batch):
    producer = create_kafka_producer()
    results = [process_message(msg) for msg in batch]
    for result in results:
        if result:
            retry_produce(producer, result)

# Monitoring System Metrics
def monitor_metrics():
    logger.info("Prometheus metrics server started on port 8000")
    while True:
        logger.info("Current metrics state:")
        logger.info(f"Request count: {REQUEST_COUNT._value.get()}")
        logger.info(f"Error count: {ERROR_COUNT._value.get()}")
        time.sleep(60)

if __name__ == "__main__":
    logger.info("Kafka pipeline is running")
    try:
        multi_thread_consumer()
        monitor_metrics()
    except Exception as e:
        logger.error(f"Error in Kafka pipeline: {e}")
        ERROR_COUNT.inc()
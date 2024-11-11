from confluent_kafka import Producer

# Kafka producer configuration
conf = {
    'bootstrap.servers': 'pkc-921jm.us-east-2.aws.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'R3EWHOYZP6OLQJSS',
    'sasl.password': 'sy9qkEqd64wX+B5su9AxQUtigfInBYSFr/xg+0Xkeg7tqC5WZ9L7Pm4ysVsvJvFS',
}

producer = Producer(conf)

def produce_event(topic, message):
    """Send a message to the Kafka topic."""
    try:
        producer.produce(topic, value=message)
        producer.flush()
        print(f"Message sent to topic '{topic}': {message}")
    except Exception as e:
        print(f"Error producing message: {e}")

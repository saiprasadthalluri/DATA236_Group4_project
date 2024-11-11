from confluent_kafka import Consumer

# Kafka consumer configuration
conf = {
    'bootstrap.servers': 'pkc-921jm.us-east-2.aws.confluent.cloud:9092',
    'group.id': 'taxi_booking_group',
    'auto.offset.reset': 'earliest',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'R3EWHOYZP6OLQJSS',
    'sasl.password': 'sy9qkEqd64wX+B5su9AxQUtigfInBYSFr/xg+0Xkeg7tqC5WZ9Pm4ysVsvJvFS',
}

consumer = Consumer(conf)

def consume_events(topic):
    """Listen to messages on the Kafka topic."""
    try:
        consumer.subscribe([topic])
        print(f"Listening to topic '{topic}'...")
        while True:
            msg = consumer.poll(1.0)
            if msg is not None and not msg.error():
                print(f"Received message: {msg.value().decode('utf-8')}")
    except Exception as e:
        print(f"Error consuming messages: {e}")
    finally:
        consumer.close()

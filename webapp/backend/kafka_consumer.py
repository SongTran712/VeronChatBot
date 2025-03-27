import json
import logging
from aiokafka import AIOKafkaConsumer


async def consume_tokens_from_kafka(id):
    # Initialize the consumer
    consumer = AIOKafkaConsumer(
        'response',  # Kafka topic to consume from
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        enable_auto_commit=False,  # Disable auto commit to commit offsets manually
        max_poll_records=100,  # Limit the number of records per poll
    )
    print("Starting consuming...")
    # Start the consumer
    await consumer.start()

    try:
        # Consume messages from Kafka
        async for message in consumer:
            print(f"{message.topic}:{message.partition}:{message.offset}: key={message.key} value={message.value}")
            
            # Decode the key (assumed to be bytes, converting to string)
            key = message.key.decode() if message.key else None

            if id != key:  # Only process messages that match the provided id
                print("Passing")
                continue

            # Get the token from the message value
            token = message.value.get('token')  # Ensure 'token' exists in the message
            if token:
                yield token  # Yield token as an event-stream message
            
            # Manually commit the offset for the message
            consumer.commit()

    except Exception as e:
        logging.error(f"Error while consuming tokens: {e}")
    finally:
        # Stop the consumer gracefully
        await consumer.stop()

# # Example usage in an async function
# async def main():
#     async for token in consume_tokens_from_kafka('some-id'):
#         print(f"Received token: {token}")

# # Running the event loop
# import asyncio
# asyncio.run(main())

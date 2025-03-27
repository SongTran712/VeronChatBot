import logging
import asyncio
from json import loads
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from langchain_ollama import ChatOllama
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import HumanMessage
import json

async def data_stream(content):
    callback = AsyncIteratorCallbackHandler()
    llm = model  
    task = asyncio.create_task(
        llm.agenerate(messages=[[HumanMessage(content=content)]], callbacks=[callback])
    )
    try:
        # Yield tokens as they come in
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f"Caught exception: {e}")
    finally:
        await callback.done.wait()  # Ensure the task completes
        callback.done.set()
        await task

# The function that sends the stream of messages to Kafka
async def send_stream_of_messages(content, key):
    # Initialize the Kafka producer
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: str(k).encode('utf-8')  # Serialize the key
    )

    # Start the producer
    await producer.start()

    try:
        # Get the token stream from data_stream
        async for token in data_stream(content):
            # Send each token as a message to the Kafka topic 'response'
            await producer.send_and_wait('response', value={'token': token}, key=key)
            logging.info(f"Sent token: {token}")  # Logging for debugging

    except Exception as e:
        logging.error(f"Error sending messages: {e}")
    finally:
        # Stop the producer gracefully
        await producer.stop()

# Function to consume messages from Kafka
async def consume_messages():
    # Initialize the consumer
    consumer = AIOKafkaConsumer(
        'hello',  # Topic to consume from
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda x: loads(x.decode('utf-8')),  # Deserialize JSON values
        enable_auto_commit=False,  # Disable auto commit to manually commit offsets
        max_poll_records=100  # Maximum number of records to fetch in a single poll
    )

    # Start the consumer
    await consumer.start()

    try:
        # Consume messages
        async for message in consumer:
            print(f"{message.topic}:{message.partition}:{message.offset}: key={message.key} value={message.value}")
            # Decode the key if present
            id = message.key.decode() if message.key else None
            print("ID: ", id)

            # # Call send_stream_of_messages to process tokens
            await send_stream_of_messages(message.value, id)

            # # Manually commit the offset after processing the message
            # consumer.commit_offsets({message.partition: message.offset + 1})
            # logging.info(f"Committed offset {message.offset + 1} for partition {message.partition}")
    except Exception as e:
        logging.error(f"Error consuming message: {e}")
    finally:
        # Stop the consumer gracefully
        await consumer.stop()

if __name__ == '__main__':
    model = ChatOllama(
        model="llama3.2:1b",
        temperature=0,
        streaming=True,
        verbose=True,
        base_url="http://localhost:11434",
    )

    model.invoke("Hello, I am a language model. How can I help you?")
    
    try:
        asyncio.run(consume_messages())
    except Exception as e:
        logging.error(f'Connection failed: {e}')

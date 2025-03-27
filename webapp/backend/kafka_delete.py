from kafka.admin import KafkaAdminClient
from kafka.errors import KafkaError

def delete_all_kafka_topics(bootstrap_servers: str = 'localhost:9092'):
    try:
        # Create an instance of KafkaAdminClient
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

        # Get the list of all topics
        topics = admin_client.list_topics()
        
        if topics:
            # Delete all topics
            admin_client.delete_topics(topics)
            print(f"Deleted all topics: {topics}")
        else:
            print("No topics found.")
    except KafkaError as e:
        print(f"Error while deleting topics: {e}")
    finally:
        # Close the admin client
        admin_client.close()

# Example: Delete all topics in the Kafka cluster
if __name__ == '__main__':
    delete_all_kafka_topics('localhost:9092')

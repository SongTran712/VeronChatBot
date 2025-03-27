from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError


def create_kafka_topic(server, topic):
    bootstrap_servers = server
    topic_name = topic

    # Initialize Kafka AdminClient
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    # List existing topics
    existing_topics = admin_client.list_topics()

    if topic_name not in existing_topics:
        try:
            # Create new topic
            topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
            admin_client.create_topics(new_topics=[topic], validate_only=False)
            print(f"Topic {topic_name} created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic {topic_name} already exists.")
    else:
        print(f"Topic {topic_name} already exists.")
        

if __name__ == '__main__':
    create_kafka_topic('localhost:9092', 'hello')
    create_kafka_topic('localhost:9092', 'response')
    # create_kafka_topic('localhost:9092', 'hello

import os
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.avroencoder import AvroEncoder
from shared.schema_utils.schema_registry_singleton import SchemaRegistrySingleton

EVENTHUB_NAME = "energy-application-eh-ns"
SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = "energy-application-eh-ns.servicebus.windows.net"
GROUP_NAME = "datacapture"

avro_encoder = AvroEncoder(
    SchemaRegistrySingleton.get_instance(),
    group_name=GROUP_NAME,
    auto_register=True
)

def send_event(event_data):
    producer = EventHubProducerClient(EVENTHUB_NAME, credential=DefaultAzureCredential())
    with producer:
        producer.send_batch(event_data)

def main(req: func.HttpRequest):
    req_body = req.get_json()

    # Assuming req_body is a list of dictionaries, each representing an event
    event_data_list = []
    for data in req_body:
        # Use the encode method to encode the data using the Avro schema
        avro_encoded_data = avro_encoder.encode(data, message_type=EventData)
        event_data_list.append(avro_encoded_data)

    # Send the event data to the Event Hub
    send_event(event_data_list)

    return func.HttpResponse("Data sent to Event Hub successfully.", status_code=200)

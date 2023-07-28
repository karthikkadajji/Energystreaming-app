import logging
from  shared.schema_utils.schema_registry_singleton import SchemaRegistrySingleton
import azure.functions as func
from azure.schemaregistry import SchemaRegistryClient, SchemaFormat
from azure.identity import DefaultAzureCredential
import json
from shared.schema_format.Spotmarktpreis_schema import SCHEMA_JSON
from azure.eventhub import EventHubProducerClient, EventData

def get_or_register_schema(schema_registry_client):
    # Define your Avro schema here
    schema_definition = json.dumps(SCHEMA_JSON, separators=(",", ":"))
    schema_properties = schema_registry_client.register_schema("datacapture", "spotmarktpreis", schema_definition, "Avro")
    return schema_properties

def send_data_to_eventhub(connection_string, eventhub_name, client, schema_id, data):
    producer = EventHubProducerClient.from_connection_string(connection_string, eventhub_name)

    for line in data.strip().split("\n"):
        event_data = EventData(body=line.encode("utf-8"))
        event_data.properties = {"$schema": schema_id}  # Attach the schema ID to the event
        with producer:
            producer.send(event_data)

def main(req: func.HttpRequest) -> func.HttpResponse:

    client = SchemaRegistrySingleton.get_instance()
    schema_properties = get_or_register_schema(client)
    send_data_to_eventhub()
    schema_properties.id
    return func.HttpResponse(f"Schema properties are {schema_properties}")

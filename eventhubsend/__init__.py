from shared.schema_utils.schema_registry_singleton import SchemaRegistrySingleton
import azure.functions as func
from azure.identity import DefaultAzureCredential
import json
from shared.schema_format.Spotmarktpreis_schema import SCHEMA_JSON
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry.encoder.avroencoder import AvroEncoder

EVENTHUB_NAME = "energy-application-eh-ns"
SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = "energy-application-eh-ns.servicebus.windows.net"
GROUP_NAME = "datacapture"


def get_or_register_schema(schema_registry_client):
    # Define your Avro schema here
    schema_definition = json.dumps(SCHEMA_JSON, separators=(",", ":"))
    schema_properties = schema_registry_client.register_schema("datacapture", "spotmarktpreis", schema_definition,
                                                               "Avro")
    return schema_properties


avro_encoder = AvroEncoder(
    SchemaRegistrySingleton.get_instance(),
    group_name=GROUP_NAME,
    auto_register=True
)


def send_data_to_eventhub():
    data = {
        "Datum": "31.12.2020",
        "von": "23:00",
        "Zeitzone_von": "UTC",
        "bis": "00:00",
        "Zeitzone_bis": "UTC",
        "Spotmarktpreis_in_ct_kWh": "5,087",
    }
    avro_encoded_data = avro_encoder.encode(data, message_type=EventData)

    producer = EventHubProducerClient(EVENTHUB_NAME, credential=DefaultAzureCredential())
    with producer:
        producer.send_batch(avro_encoded_data)
    # for line in data.strip().split("\n"):
    #     event_data = EventData(body=line.encode("utf-8"))
    #     event_data.properties = {"$schema": schema_id}  # Attach the schema ID to the event
    #     with producer:
    #         producer.send(event_data)


def main(req: func.HttpRequest) -> func.HttpResponse:
    # create singleton client connection
    client = SchemaRegistrySingleton.get_instance()
    schema_properties = get_or_register_schema(client)
    send_data_to_eventhub()
    schema_properties.id
    send_data_to_eventhub()
    return func.HttpResponse(f"Schema properties are {schema_properties}")

import logging
from azure.identity import DefaultAzureCredential
from azure.eventhub import EventHubConsumerClient
import azure.functions as func
from shared.schema_utils.schema_registry_singleton import SchemaRegistrySingleton
from azure.schemaregistry.encoder.avroencoder import AvroEncoder
import os

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.getenv("SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE")
GROUP_NAME = os.getenv("GROUP_NAME")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
SPOT_PREIS_SCHEMA_NAME = os.getenv("SPOT_PREIS_SCHEMA_NAME")


def on_event(partition_context, event):
    decoded_content = avro_encoder.decode(event)
    logging.info(f'The dict content after decoding is {decoded_content}')


# create an EventHubConsumerClient instance
eventhub_consumer = EventHubConsumerClient(
    consumer_group='$Default',
    fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
                                                   eventhub_name=EVENTHUB_NAME,
                                                   credential=DefaultAzureCredential()
)
avro_encoder = AvroEncoder(
    client=SchemaRegistrySingleton.get_instance(),
    group_name=GROUP_NAME,
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    # create a AvroEncoder instance

    try:
        with eventhub_consumer, avro_encoder:
            eventhub_consumer.receive(
                on_event=on_event
            )
            return func.HttpResponse("Stopped receiving")
    except Exception as eh_error:
        return func.HttpResponse("Stopped receiving")

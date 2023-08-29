from shared.schema_utils.schema_registry_singleton import SchemaRegistrySingleton
import azure.functions as func
from azure.identity import DefaultAzureCredential
from shared.schema_format.Spotmarktpreis_schema import SCHEMA_JSON
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry.encoder.avroencoder import AvroEncoder
import os
import logging
from shared.auth_api.access_token_handler import NetzTransparenzAccessTokenHandler
from shared.auth_api.api_client import NetzTransparenzAPIClient
from azure.keyvault.secrets import SecretClient

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.getenv("SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE")
GROUP_NAME = os.getenv("GROUP_NAME")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
SPOT_PREIS_SCHEMA_NAME = os.getenv("SPOT_PREIS_SCHEMA_NAME")
KEY_VAULT_URL = os.getenv("KEY_VAULT_URL")

def get_secret_from_keyvault(secret_name):
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
    secret = secret_client.get_secret(secret_name)
    return secret.value


def get_or_register_schema(schema_registry_client):
    return schema_registry_client.register_schema(GROUP_NAME, SPOT_PREIS_SCHEMA_NAME, SCHEMA_JSON,
                                                  "Avro")


def encode_data_eventhub(data):
    avro_encoder = AvroEncoder(
        client=SchemaRegistrySingleton.get_instance(),
        group_name=GROUP_NAME,
    )
    avro_encoded_data = avro_encoder.encode(data, schema=SCHEMA_JSON, message_type=EventData)

    return avro_encoded_data


def get_data_from_netztransparenz():
    try:
        logging.info('Python HTTP trigger function processed a request.')
        IPNT_CLIENT_SECRET = get_secret_from_keyvault("IPNTCLIENTSECRET")
        IPNT_CLIENT_ID = get_secret_from_keyvault("IPNTCLIENTID")
        token_handler = NetzTransparenzAccessTokenHandler(IPNT_CLIENT_ID, IPNT_CLIENT_SECRET)
        access_token = token_handler.get_access_token()

        if access_token:
            api_client = NetzTransparenzAPIClient(access_token)
            response = api_client.make_api_request(endpoint="data/Spotmarktpreise", method="GET",
                                                   headers={'accept': '*/*'})
            return response.text
    except Exception as e:
        logging.error(e)


def transform_net_data(data):
    lines = data.split("\n")
    data_without_header = lines[1:]

    header = lines[0].split("; ")
    keys = [key.strip() for key in header]
    # Join the lines back into a single string
    data_list = []

    for line in data_without_header:
        values = line.split("; ")
        data_dict = dict(zip(keys, values))
        data_list.append(data_dict)

    return data_list

def main(req: func.HttpRequest) -> func.HttpResponse:
    schema_registry_client = SchemaRegistrySingleton.get_instance()
    get_or_register_schema(schema_registry_client)
    data_net = get_data_from_netztransparenz()
    data_net_transformed = transform_net_data(data_net)
    num_record = 0
    try:
        eventhub_producer = EventHubProducerClient(fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
                                                   eventhub_name=EVENTHUB_NAME,
                                                   credential=DefaultAzureCredential())
        with eventhub_producer:
            event_data_batch = eventhub_producer.create_batch()

            for time_point in data_net_transformed:
                num_record+=1
                avro_encoded_data = encode_data_eventhub(time_point)
                event_data_batch.add(avro_encoded_data)
                if num_record == 10:
                    break # Send only 10 messages for now
            eventhub_producer.send_batch(event_data_batch)
        return func.HttpResponse(f"sent data")
    except Exception as e:
        return func.HttpResponse(f"Exception occured {e.message}")

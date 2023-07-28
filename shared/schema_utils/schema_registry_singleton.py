import os
import json
from azure.schemaregistry import SchemaRegistryClient
from azure.identity import DefaultAzureCredential
import azure.functions as func

class SchemaRegistrySingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls._create_instance()
        return cls._instance

    @classmethod
    def _create_instance(cls):
        SCHEMAREGISTRY_FQN = "energy-application-eh-ns.servicebus.windows.net"
        token_credential = DefaultAzureCredential()
        return SchemaRegistryClient(
            fully_qualified_namespace=SCHEMAREGISTRY_FQN, credential=token_credential
        )
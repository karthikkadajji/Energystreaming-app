import os
import json
from azure.schemaregistry import SchemaRegistryClient
from azure.identity import DefaultAzureCredential
import azure.functions as func
SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.getenv("SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE")

class SchemaRegistrySingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls._create_instance()
        return cls._instance

    @classmethod
    def _create_instance(cls):
        token_credential = DefaultAzureCredential()
        return SchemaRegistryClient(
            fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE, credential=token_credential
        )
import logging
from shared.auth_api.access_token_handler import NetzTransparenzAccessTokenHandler
from shared.auth_api.api_client import NetzTransparenzAPIClient
import azure.functions as func
import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

KEY_VAULT_URL = os.getenv("KEY_VAULT_URL")
def get_secret_from_keyvault(secret_name):
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
    secret = secret_client.get_secret(secret_name)
    return secret.value

def main(req: func.HttpRequest) -> func.HttpResponse:
  try:

    logging.info('Python HTTP trigger function processed a request.')
    IPNT_CLIENT_SECRET = get_secret_from_keyvault("IPNTCLIENTSECRET")
    IPNT_CLIENT_ID = get_secret_from_keyvault("IPNTCLIENTID")
    token_handler = NetzTransparenzAccessTokenHandler(IPNT_CLIENT_ID, IPNT_CLIENT_SECRET)
    access_token = token_handler.get_access_token()

    if access_token:
      api_client = NetzTransparenzAPIClient(access_token)
      response = api_client.make_api_request(endpoint="data/Spotmarktpreise", method="GET", headers={'accept': '*/*'})
      return func.HttpResponse(response.text)
  except Exception as e:
     return func.HttpResponse(e)
import logging
from shared.auth_api.access_token_handler import AccessTokenHandler
from shared.auth_api.api_client import APIClient
import azure.functions as func


IPNT_CLIENT_ID = "cm_app_ntp_id_50f4fef580ee4803ac84f79df5339a5d"

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_from_keyvault(secret_name):
    vault_url = "https://energy-poc-vault.vault.azure.net/"
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    secret = secret_client.get_secret(secret_name)
    return secret.value

def main(req: func.HttpRequest) -> func.HttpResponse:
  try:

    logging.info('Python HTTP trigger function processed a request.')
    IPNT_CLIENT_SECRET = get_secret_from_keyvault("IPNTCLIENTSECRET")
# Create an instance of AccessTokenHandler and get the access token
    token_handler = AccessTokenHandler(IPNT_CLIENT_ID, IPNT_CLIENT_SECRET)
    access_token = token_handler.get_access_token()

    if access_token:
  # Create an instance of APIClient and make the API request
      api_client = APIClient(access_token)
      response = api_client.make_api_request(endpoint="data/Spotmarktpreise", method="GET", headers={'accept': '*/*'})
      return func.HttpResponse(response.text)
  except Exception as e:
     return func.HttpResponse(e)
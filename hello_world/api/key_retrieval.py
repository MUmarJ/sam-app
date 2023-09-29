import os
import openai
import requests
import json
from retry import retry
from msal import ClientApplication
import time

def lambda_handler(event, context):
    return getapikey()

@retry (tries=3, delay=2)
def getapikey():
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    endpoint = os.getenv("AZURE_ENDPOINT")

    scopes = [os.getenv("AZURE_APPLICATION_SCOPE")]

    app = ClientApplication(
        client_id=client_id,
        authority="https://login.microsoftonline.com/" + tenant_id
    )

    acquire_tokens_result = app.acquire_token_by_username_password(username=os.getenv("SVC_ACCOUNT"),
        password=os.getenv("SVC_PASSWORD"),
        scopes=scopes)

    if 'error' in acquire_tokens_result:
        print("Error: " + acquire_tokens_result['error'])
        print("Description: " + acquire_tokens_result['error_description'])
        return(2)
    else:
        header_token = {"Authorization": "Bearer {}".format(acquire_tokens_result['access_token'])}
        rt = requests.post(url=endpoint, headers=header_token, data=b'{"key":"openaikey2"}')
        return(rt.json())
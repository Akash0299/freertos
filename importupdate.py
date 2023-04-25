import os
import base64
import hashlib
import json

from azure.iot.deviceupdate import DeviceUpdateClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

from azure.core.pipeline.transport import RequestsTransport
import requests

transport = RequestsTransport()
if not transport.session:
    transport.session = requests.Session()
transport.session.verify = False


# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
os.environ["AZURE_IOTHUB_CONNECTION_STRING"] = 'HostName=adu-poc-iothub.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=3vPGTQZSlr+HjHaQ/A8DFEpAftgEjs+P+mLCJENBZP0='
os.environ["DEVICE_ID"] = 'rtos-adu'
os.environ["AZURE_TENANT_ID"] = 'df7b3572-e484-4fcf-a072-6edd5d73f11f'
os.environ["AZURE_CLIENT_ID"] = 'd253e2e1-965a-43be-a9b4-6d5e3942959e'
os.environ["AZURE_CLIENT_SECRET"] = 'oKZ8Q~tsLxCMGQnOJ.LAWnR4oHDRvyD-VRoJFa0C'

# Set the following environment variables for this particular sample:
# DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID,
# DEVICEUPDATE_PAYLOAD_FILE, DEVICEUPDATE_PAYLOAD_URL, DEVICEUPDATE_MANIFEST_FILE, DEVICEUPDATE_MANIFEST_URL
try:
    endpoint = 'adu-poc-iothub.api.adu.microsoft.com'
    instance = 'adu-poc-iothub'
    payload_file = 'firmware.bin'
    payload_url = 'https://adupocstorage.blob.core.windows.net/aducont1/firmware.bin'
    manifest_file = 'adu.importmanifest.json'
    manifest_url = 'https://adupocstorage.blob.core.windows.net/aducont1/adu.importmanifest.json'
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, "
          "DEVICEUPDATE_PAYLOAD_FILE, DEVICEUPDATE_PAYLOAD_URL, DEVICEUPDATE_MANIFEST_FILE, DEVICEUPDATE_MANIFEST_URL")
    exit()


def get_file_size(file_path):
    return os.path.getsize(file_path)


def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        return base64.b64encode(hashlib.sha256(bytes).digest()).decode("utf-8")


# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(),endpoint=endpoint, instance_id=instance, transport=transport)

try:
    content = [{
        "importManifest": {
            "url": manifest_url,
            "sizeInBytes": get_file_size(manifest_file),
            "hashes": {
                "sha256": get_file_hash(manifest_file)
            }
        },
        "files": [{
            "fileName": os.path.basename(payload_file),
            "url": payload_url
        }]
    }]

    response = client.device_update.begin_import_update(content)
    response.wait
    print(response.result())

except HttpResponseError as e:
    print('Failed to import update: {}'.format(e))
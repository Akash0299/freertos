import json
import os
import uuid
from datetime import datetime, timezone

from azure.iot.deviceupdate import DeviceUpdateClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

# Set the following environment variables for this particular sample:
# DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, DEVICEUPDATE_DEVICE_GROUP,
# DEVICEUPDATE_UPDATE_PROVIDER, DEVICEUPDATE_UPDATE_NAME, DEVICEUPDATE_UPDATE_VERSION
try:
    os.environ["AZURE_IOTHUB_CONNECTION_STRING"] = 'HostName=adu-poc-iothub.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=3vPGTQZSlr+HjHaQ/A8DFEpAftgEjs+P+mLCJENBZP0='
    os.environ["DEVICE_ID"] = 'rtos-adu'
    os.environ["AZURE_TENANT_ID"] = 'df7b3572-e484-4fcf-a072-6edd5d73f11f'
    os.environ["AZURE_CLIENT_ID"] = 'd253e2e1-965a-43be-a9b4-6d5e3942959e'
    os.environ["AZURE_CLIENT_SECRET"] = 'oKZ8Q~tsLxCMGQnOJ.LAWnR4oHDRvyD-VRoJFa0C'
    endpoint = 'adu-poc-iothub.api.adu.microsoft.com'
    instance = 'adu-poc-iothub'
    update_provider = ''
    update_name = ''
    update_version = ''
    group = ''
except KeyError:
    print("Missing one of environment variables: DEVICEUPDATE_ENDPOINT, DEVICEUPDATE_INSTANCE_ID, ")
    print("DEVICEUPDATE_DEVICE_GROUP, DEVICEUPDATE_UPDATE_PROVIDER, DEVICEUPDATE_UPDATE_NAME, DEVICEUPDATE_UPDATE_VERSION")
    exit()

# Build a client through AAD
client = DeviceUpdateClient(credential=DefaultAzureCredential(), endpoint=endpoint, instance_id=instance)

try:
    deployment_id = uuid.uuid4().hex
    deployment = {
        "deploymentId": deployment_id,
        "startDateTime": str(datetime.now(timezone.utc)),
        "update": {
            "updateId": {
                "provider": update_provider,
                "name": update_name,
                "version": update_version
            }
        },
        "groupId": group
    }

    response = client.device_management.create_or_update_deployment(group, deployment_id, deployment)
    response = client.device_management.get_deployment_status(group, deployment_id)
    print(response)
except HttpResponseError as e:
    print('Failed to deploy update: {}'.format(e))
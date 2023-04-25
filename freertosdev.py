import simpy
import asyncio
import random
from azure.iot.device import IoTHubDeviceClient, Message

# Define async task function for lighting device
async def lighting_task(env, client):
    while True:
        # Get command from Azure IoT Hub
        command = await client.receive_method_request("lightingCommand")
        print("Command received: ", command.name)

        # Process command and update lighting state
        if command.name == "turnOn":
            print("Turning on the lighting device")
        elif command.name == "turnOff":
            print("Turning off the lighting device")

        # Send response back to Azure IoT Hub
        response = command.create_response(200, "OK")
        await client.send_method_response(response)

        # Wait for next task execution
        await env.timeout(5)

# Define async interrupt function for lighting device
async def lighting_interrupt(env, client):
    while True:
        # Check for new messages from Azure IoT Hub
        message = await client.receive_message()
        print("Message received: ", message.data)

        # Process message and update lighting state
        if message.data == b"motionDetected":
            print("Motion detected. Turning on the lighting device")
        elif message.data == b"noMotionDetected":
            print("No motion detected. Turning off the lighting device")

        # Wait for next interrupt
        await env.timeout(0.1)

async def send_telemetry(env, device_client):
    # Define the JSON message to send to IoT Hub.
    TEMPERATURE = 20.0
    LIGHT_LEVEL = 10
    MSG_TXT = '{{"temperature": {temperature},"light_level": {light_level}}}'

    print(TEMPERATURE,LIGHT_LEVEL,MSG_TXT)
    
    # Simulate sending telemetry data
    while True:
        # Build the message with simulated telemetry values.
        temp = TEMPERATURE + (random.random() * 15)
        light = LIGHT_LEVEL + (random.random() * 20)
        msg_txt_formatted = MSG_TXT.format(temperature=temp, light_level=light)
        message = Message(msg_txt_formatted)
        print(message)

        # Add a custom application property to the message.
        # An IoT hub can filter on these properties without access to the message body.
        if temp > 30:
            message.custom_properties["temperatureAlert"] = "true"
        else:
            message.custom_properties["temperatureAlert"] = "false"

        # Send the message.
        print("Sending message: {}".format(message))
        device_client.send_message(message)
        await asyncio.sleep(5)

async def main():
    try:
        conn_str = 'HostName=adu-poc-iothub.azure-devices.net;DeviceId=rtos-adu;SharedAccessKey=rLQBuR3tJgfvrzm4VzyLVSetsUmk6tO+NM59sYoh/bE='

        # Create an instance of the IoTHubDeviceClient
        device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

        # Connect the device client
        device_client.connect()

        print(device_client)

        print('Azure IoTHub Connected')
        
        # Create simulation environment
        env = simpy.Environment()
        
        print('Scheduling tasks')
        # Schedule lighting task and interrupt processes
        await send_telemetry(env, device_client)
        env.process(lighting_task(env, device_client))
        env.process(lighting_interrupt(env, device_client))

        # Run simulation for 100 time units
        await asyncio.sleep(100)

    except Exception as ex:
        print(f"Unexpected error: {ex}")
        raise

    finally:
        # Disconnect the device client
        device_client.disconnect()
    
if __name__ == '__main__':
    asyncio.run(main())

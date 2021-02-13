# Remote Roller
# Allen Snook
# February 13, 2021

import os
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

async def main():
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the client.
    await device_client.connect()
    print("Connected!")

    # Finally, shut down the client
    await device_client.shutdown()
    print("Disonnected!")

if __name__ == "__main__":
    asyncio.run(main())


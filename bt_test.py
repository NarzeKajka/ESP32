import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct

# org.bluetooth.service.generic_access
_ENV_SENSE_UUID = bluetooth.UUID(0x1800)

# print(_ENV_SENSE_UUID)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A00)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 5000

_FILE_SERVICE_UUID = bluetooth.UUID("bd7d2ba5-94e8-4227-8c60-a460ec990161")
_CONTROL_CHARACTERISTIC_UUID = bluetooth.UUID("62df3986-cb47-4e03-9f48-634ae9fb426c")

# Register GATT server.
# service = aioble.Service(_ENV_SENSE_UUID)
# characteristic = aioble.Characteristic(
#     service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
# )
service = aioble.Service(_FILE_SERVICE_UUID)
characteristic = aioble.Characteristic(
    service, _CONTROL_CHARACTERISTIC_UUID, read=True, notify=True, write=True, write_no_response=True, indicate=True,
    capture=True
)
aioble.register_services(service)


async def write_task(connection):
    try:
        with connection.timeout(None):
            while True:
                # print("waiting for write")
                # await characteristic.written()
                # msg = characteristic.read()
                # characteristic.write(b"")
                connection, data = await characteristic.written()

                # if len(msg) < 3:
                #     continue

                print("received:", data)

    except Exception as e:
        print("Error write:", e)


# Serially wait for connections. Don't advertise while a central is
# connected.
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                    _ADV_INTERVAL_MS,
                    name="mpy-temp",
                    services=[_FILE_SERVICE_UUID]
            ) as connection:
                print("Connection from", connection.device)
                await write_task(connection)
                await connection.disconnected()
        except Exception as e:
            print(type(e))
            print("Error:", e)


# Run both tasks.
async def main():
    # t1 = asyncio.create_task(write_task())
    # t2 = asyncio.create_task(peripheral_task())
    # await asyncio.gather(t1, t2)
    # await asyncio.gather(t2)
    await peripheral_task()


asyncio.run(main())

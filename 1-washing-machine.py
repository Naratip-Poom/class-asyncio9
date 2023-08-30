import time
import random
import json
import asyncio
import aiomqtt
from enum import Enum
import sys
import os

student_id = "6310301012"


class MachineStatus(Enum):
    pressure = round(random.uniform(2000, 3000), 2)
    temperature = round(random.uniform(25.0, 40.0), 2)
    speed = round(random.uniform(25.0, 40.0), 2)
    #
    # add more machine status
    #


class MachineMaintStatus(Enum):
    filter = random.choice(["clear", "clogged"])
    noise = random.choice(["quiet", "noisy"])
    #
    # add more maintenance status
    #


class WashingMachine:
    def __init__(self, serial):
        self.MACHINE_STATUS = 'OFF'
        self.SERIAL = serial


async def publish_message(w, client, app, action, name, value):
    print(f"{time.ctime()} - [{w.SERIAL}] {name}:{value}")
    await asyncio.sleep(2)
    payload = {
        "action": "get",
        "project": student_id,
        "model": "model-01",
        "serial": w.SERIAL,
        "name": name,
        "value": value
    }
    print(
        f"{time.ctime()} - PUBLISH - [{w.SERIAL}] - {payload['name']} > {payload['value']}")
    await client.publish(f"v1cdti/{app}/{action}/{student_id}/model-01/{w.SERIAL}", payload=json.dumps(payload))


async def CoroWashingMachine(w, client):
    # washing coroutine
    while True:
        wait_next = round(10*random.random(), 2)
        print(
            f"{time.ctime()} - [{w.SERIAL}] Waiting to start... {wait_next} seconds.")
        await asyncio.sleep(wait_next)
        if w.MACHINE_STATUS == 'OFF':
            continue
        else:
            await publish_message(w, client, 'hw', 'set', 'STATUS', 'START')
            await publish_message(w, client, 'hw', 'set', 'LID', 'OPEN')
            await publish_message(w, client, 'hw', 'set', 'LID', 'CLOSE')

            status = random.choice(list(MachineStatus))
            await publish_message(w, client, 'app', 'get', status.name, status.value)
            await publish_message(w, client, 'app', 'get', "STATUS", "FINISHED")

            maint = random.choice(list(MachineMaintStatus))
            await publish_message(w, client, 'app', 'get', maint.name, maint.value)

            sensor = random.choice(list(MachineStatus))

            await publish_message(w, client, 'app', 'get', 'SPEED', '100')

            if maint.name == 'noise' and maint.value == 'noisy':
                w.MACHINE_STATUS = 'OFF'
                continue

            w.MACHINE_STATUS = 'OFF'


async def listen(w, client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}"):
                print(
                    f"{time.ctime()} - MQTT - [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']}")
                w.MACHINE_STATUS = 'ON'


async def main():
    w1 = WashingMachine(serial='SN-001')
    async with aiomqtt.Client("test.mosquitto.org") as client:
        print(client)
        await asyncio.gather(listen(w1, client), CoroWashingMachine(w1, client))
        # await listen(client)


# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())

# <aiomqtt.client.Client object at 0x000002DAB2BA2560>
# Wed Aug 30 14:34:18 2023 - [SN-001] Waiting to start... 6.29 seconds.
# Wed Aug 30 14:34:25 2023 - [SN-001] Waiting to start... 6.86 seconds.
# Wed Aug 30 14:34:32 2023 - [SN-001] Waiting to start... 1.47 seconds.
# Wed Aug 30 14:34:33 2023 - [SN-001] Waiting to start... 4.42 seconds.
# Wed Aug 30 14:34:37 2023 - [SN-001] Waiting to start... 9.52 seconds.
# Wed Aug 30 14:34:47 2023 - [SN-001] Waiting to start... 1.05 seconds.
# Wed Aug 30 14:34:48 2023 - [SN-001] Waiting to start... 9.8 seconds.
# Wed Aug 30 14:34:58 2023 - [SN-001] Waiting to start... 0.52 seconds.
# Wed Aug 30 14:34:58 2023 - [SN-001] Waiting to start... 8.19 seconds.
# Wed Aug 30 14:35:07 2023 - [SN-001] Waiting to start... 0.79 seconds.
# Wed Aug 30 14:35:07 2023 - [SN-001] Waiting to start... 3.8 seconds.
# Wed Aug 30 14:35:11 2023 - [SN-001] Waiting to start... 3.5 seconds.
# Wed Aug 30 14:35:15 2023 - [SN-001] Waiting to start... 1.64 seconds.
# Wed Aug 30 14:35:16 2023 - [SN-001] Waiting to start... 4.99 seconds.
# Wed Aug 30 14:35:19 2023 - MQTT - [SN-001]:POWER => ON
# Wed Aug 30 14:35:21 2023 - [SN-001] STATUS:START
# Wed Aug 30 14:35:23 2023 - PUBLISH - [SN-001] - STATUS > START
# Wed Aug 30 14:35:23 2023 - [SN-001] LID:OPEN
# Wed Aug 30 14:35:24 2023 - MQTT - [SN-001]:STATUS => START
# Wed Aug 30 14:35:25 2023 - PUBLISH - [SN-001] - LID > OPEN
# Wed Aug 30 14:35:25 2023 - [SN-001] LID:CLOSE
# Wed Aug 30 14:35:26 2023 - MQTT - [SN-001]:LID => OPEN
# Wed Aug 30 14:35:27 2023 - PUBLISH - [SN-001] - LID > CLOSE
# Wed Aug 30 14:35:27 2023 - [SN-001] temperature:32.61
# Wed Aug 30 14:35:28 2023 - MQTT - [SN-001]:LID => CLOSE
# Wed Aug 30 14:35:29 2023 - PUBLISH - [SN-001] - temperature > 32.61
# Wed Aug 30 14:35:29 2023 - [SN-001] STATUS:FINISHED
# Wed Aug 30 14:35:31 2023 - PUBLISH - [SN-001] - STATUS > FINISHED
# Wed Aug 30 14:35:31 2023 - [SN-001] filter:clogged
# Wed Aug 30 14:35:34 2023 - PUBLISH - [SN-001] - filter > clogged
# Wed Aug 30 14:35:34 2023 - [SN-001] SPEED:100
# Wed Aug 30 14:35:36 2023 - PUBLISH - [SN-001] - SPEED > 100
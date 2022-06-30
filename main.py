import logging
from pprint import pprint
import minimalmodbus
import time
import serial
import yaml
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.server.sync import StartSerialServer

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock

import logging
import asyncio
from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient as ModbusClient
from pymodbus.client.asynchronous import schedulers

FORMAT = (
    "%(asctime)-15s %(threadName)-15s"
    " %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
)
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


UNIT = 0x01

store = {
    3: ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17] * 100),
        co=ModbusSequentialDataBlock(0, [17] * 100),
        hr=ModbusSequentialDataBlock(0, [16] * 100),
        ir=ModbusSequentialDataBlock(0, [18] * 100),
    )
}
context = ModbusServerContext(slaves=store, single=False,)

reload_counter = 1

async def init_modbus():

    with open('config.yaml') as f:
        conf = yaml.safe_load(f)

    parity = {'none': serial.PARITY_NONE, 'even': serial.PARITY_EVEN, 'odd': serial.PARITY_ODD}
    mode = {'rtu': minimalmodbus.MODE_RTU, 'ascii': minimalmodbus.MODE_ASCII}

    server = await StartSerialServer(context, framer=ModbusRtuFramer, unit=3, ignore_missing_slaves=True,
                                     port="/dev/ttyUSB1", timeout=.005, baudrate=9600, autoreconnect=True)

    asyncio.get_event_loop().call_later(20, lambda: server.serve_forever)
    await server.serve_forever()


async def reload_data():
    while True:
        reload_counter = 1
        print(dir(context[3]))
        print(context[3].getValues(3, 0, 10))
        context[3].setValues(3, 0, [reload_counter,]*10)
        print(context[3].getValues(3, 0, 10))
        # context[3].setValues(4, 0x10, 33, 145, 14, 0, 54)
        reload_counter += 1
        await asyncio.sleep(10)


async def main():
    # server_task = asyncio.create_task(init_modbus())
    # reload_task = asyncio.create_task(reload_data())
    # await server_task
    # await reload_task

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(init_modbus())
    # loop.run_until_complete(reload_data())
    # loop.close()

    await asyncio.wait(
        asyncio.create_task(reload_data()),
        asyncio.create_task(init_modbus()),
    )



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())
    # main()
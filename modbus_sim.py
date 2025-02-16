import sys
import subprocess
def install_pymodbus():
    try:
        import pymodbus  # Check if pymodbus is installed
    except ImportError:
        print("pymodbus not found! Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymodbus"])
        print("pymodbus installed successfully!")
install_pymodbus()
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.client import ModbusTcpClient
import logging
import random
import time
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

modbus_opeations = {
    1: 'Read Coil', 
    2: 'Read Discrete Input', 
    3: 'Read Holding Registers',
    4: 'Read Input Registers', 
    5: 'Write Single Coil', 
    6: 'Write Single Holding Register', 
    15: 'Write Multiple Coils', 
    16: 'Write Multiple Holding Registers'
}

class LoggingDataBlock(ModbusSequentialDataBlock):
    def setValues(self, address, value):
        logging.info(f"Write Request: Address={address}, Values={value}")
        super().setValues(address, value)

    def getValues(self, address, count=1):
        values = super().getValues(address, count)
        logging.info(f"value = {values[0]} Operation = {modbus_opeations[values[0]]}")
        return values
store = ModbusSlaveContext(
    di=LoggingDataBlock(0, [0] * 100),  # Discrete Inputs
    co=LoggingDataBlock(0, [0] * 100),  # Coils
    hr=LoggingDataBlock(0, [0] * 100),  # Holding Registers
    ir=LoggingDataBlock(0, [0] * 100),  # Input Registers
)
context = ModbusServerContext(slaves=store, single=True)
identity = ModbusDeviceIdentification()
def run_server():
    print("Modbus TCP Server Running on port 502...")
    StartTcpServer(
        context,
        identity=identity,
        address=("0.0.0.0", 502),  # Listen on all interfaces
    )



def run_client():
    SERVER_IP = input("Enter remote server ip:")
    if len(SERVER_IP.strip()) == 0:
        SERVER_IP = "localhost"
    PORT = 502
    client = ModbusTcpClient(SERVER_IP, port=PORT)
    if not client.connect():
        print("Unable to connect to server")
        return
    print(f"Connected to Modbus TCP Server at {SERVER_IP}:{PORT}")
    try:
        while True:
            register_address = random.randint(0,10)
            ops = list(modbus_opeations.keys())
            value = random.choice(ops)
            response = client.write_register(register_address, value)
            if response.isError():
                print(f"Failed to write to register {register_address}")
            else:
                print(f"Wrote {value} to register {register_address}")
            response = client.read_holding_registers(register_address)
            if response.isError():
                print(f"Failed to read register {register_address}")
            else:
                print(f"Read from register {register_address}: {response.registers[0]}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClient stopped.")
    finally:
        client.close()
if __name__ == "__main__":
    choice = int(input("1.Run as master\n2.Run as slave\nEnter your choice:"))
    if choice == 1:
        run_client()
    elif choice == 2:
        run_server()
    else:
        print("Give valid input")

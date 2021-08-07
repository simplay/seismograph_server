import abc
import os
import socket
import time
import types
import typing
import requests
import json
import time
from datetime import datetime
from enum import Enum
from multiprocessing import Process
from pathlib import Path

from dotenv import load_dotenv

SERVER_PORT = 20001
RESPONSE_MSG = str.encode("ACK")
MAX_SAMPLES = 100

ROOT_PATH = Path(__file__).parent.parent


class Connection:
    def __init__(self, server_ip: str, server_port: str):
        self.server_ip = server_ip
        self.server_port = server_port

    @abc.abstractmethod
    def message(self):
        return

    @abc.abstractmethod
    def ack_message(self):
        return


class TestConnection(Connection):
    def __init__(self, server_ip: str, server_port: str):
        super().__init__(server_ip, server_port)
        self.data = []
        self.line_counter = 0

        test_filepath = os.path.join(ROOT_PATH, "test_data", "seismograph_1623428408489_1.txt")
        with open(test_filepath, "r") as file:
            self.data = file.readlines()

    def message(self):
        if self.line_counter >= len(self.data):
            self.line_counter = 0

        sample = self.data[self.line_counter].strip()
        self.line_counter = (self.line_counter + 1) % len(self.data)

        time.sleep(0.05)
        return [sample, None]

    def ack_message(self, address):
        pass


class SeismographConnection(Connection):
    BUFFER_SIZE = 1024
    RESPONSE_MSG = str.encode("ACK")

    def __init__(self, server_ip: str, server_port: str):
        super().__init__(server_ip, server_port)
        self.udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_server_socket.bind((server_ip, server_port))

    def message(self):
        msg, sender = self.udp_server_socket.recvfrom(self.BUFFER_SIZE)
        print(sender, ": ", msg)
        return msg.decode("utf-8"), sender

    def ack_message(self, address):
        self.udp_server_socket.sendto(self.RESPONSE_MSG, address)


class StorageMethods(Enum):
    TO_PIPELINE = "pipeline"
    TO_FILE = "file"


class ConnectionTypes(Enum):
    TEST = "test"
    SERVER = "server"


def main() -> None:
    storage_methods = {
        StorageMethods.TO_FILE: save_to_file,
        StorageMethods.TO_PIPELINE: send_to_pipeline
    }

    connection_types = {
        ConnectionTypes.TEST: TestConnection,
        ConnectionTypes.SERVER: SeismographConnection
    }

    load_dotenv()
    server_ip = os.getenv("SEISMOGRAPH_SERVER_IP")
    storage_method_name = os.getenv("SEISMOGRAPH_STORAGE_METHOD")
    connection_type_name = os.getenv("SEISMOGRAPH_CONNECTION_TYPE")
    backend_url = os.getenv("SEISMOGRAPH_PIPELINE_BACKEND_URL")
    host_ip = os.getenv("SEISMOGRAPH_HOST_IP")
    location = os.getenv("SEISMOGRAPH_LOCATION")

    meta_data = {
        "backend_url": backend_url,
        "host_ip": host_ip,
        "location": location
    }

    connection = connection_types[ConnectionTypes(connection_type_name)](server_ip, SERVER_PORT)

    # try:
    storage_method = storage_methods[StorageMethods(storage_method_name)]
    run(connection, storage_method, meta_data)
# except (KeyError, ValueError) as error:
#     print(error)
#     print(f"Not supported storage method '{storage_method_name}'")


def send_to_pipeline(data: typing.List[str], meta_data: dict) -> None:
    now = datetime.now()
    timestamp = datetime.timestamp(now)

    headers = {"Content-Type": "application/json"}

    backend_url = meta_data["backend_url"]

    url = f"http://{backend_url}/sensors/seismograph"
    params = [
        {
            'data': data,
            'timestamp': timestamp,
            'location': meta_data["location"],
            'ip': meta_data["host_ip"]
        }
    ]

    try:
        response = requests.post(
            url,
            data=json.dumps(params),
            headers=headers
        )
        if response.status_code == 201:
            print(response.text)

    except Exception as err:
        print(str(err))


def save_to_file(data: typing.List[str], meta_data: dict) -> None:
    file_count = meta_data["file_count"]
    timestamp = int(round(time.time() * 1000))

    filename = f"seismograph_{str(timestamp)}_{str(file_count)}.txt"
    filepath = os.path.join(ROOT_PATH, 'data', filename)

    print(f"Saving samples to {filepath}")
    with open(filepath, 'w') as file:
        while len(data) > 0:
            file.write(data.pop(0))
            file.write("\n")


def run(connection: Connection, storage_method: types.FunctionType, meta_data: dict) -> None:
    """ Fetches samples from a seismograph server and stores it according to a provided storage method function """

    samples = []
    file_count = 1

    print(f"Reading data on UDP {connection.server_ip}:{SERVER_PORT}")
    while True:
        message = connection.message()

        # https://manual.raspberryshake.org/udp.html
        # data-format:

        # Each data packet contains data for a single channel only
        # Entire data packet is wrapped with open and closing braces: { }
        # All fields are separated by a comma
        # First element defines the channel name - string in single quotes
        # Second element defines the timestamp, in epoch seconds, down to milliseconds, of the first data point - float
        # All remaining elements are the data points themselves - integer

        data, address = message

        samples.append(data)
        if len(samples) > MAX_SAMPLES:
            meta_data["file_count"] = file_count
            process = Process(target=storage_method, args=(samples, meta_data))
            process.daemon = True
            process.start()

            samples = []
            file_count += 1

        connection.ack_message(address)


if __name__ == "__main__":
    main()

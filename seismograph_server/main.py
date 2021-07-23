import os
import socket
import time
import types
from enum import Enum
from multiprocessing import Process
from pathlib import Path

from dotenv import load_dotenv

SERVER_PORT = 20001
RESPONSE_MSG = str.encode("ACK")
MAX_SAMPLES = 100

ROOT_PATH = Path(__file__).parent.parent


class SeismographConnection:
    BUFFER_SIZE = 1024
    RESPONSE_MSG = str.encode("ACK")

    def __init__(self, server_ip: str, server_port: str):
        self.server_ip = server_ip
        self.server_port = server_port
        self.udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_server_socket.bind((server_ip, server_port))

    def message(self):
        return self.udp_server_socket.recvfrom(self.BUFFER_SIZE)

    def ack_message(self, address):
        self.udp_server_socket.sendto(self.RESPONSE_MSG, address)


class StorageMethods(Enum):
    TO_PIPELINE = "pipeline"
    TO_FILE = "file"


def main() -> None:
    storage_methods = {
        StorageMethods.TO_FILE: save_to_file,
        StorageMethods.TO_PIPELINE: send_to_pipeline
    }

    load_dotenv()
    server_ip = os.getenv("SEISMOGRAPH_SERVER_IP")
    storage_method_name = os.getenv("SEISMOGRAPH_STORAGE_METHOD")

    connection = SeismographConnection(server_ip, SERVER_PORT)

    try:
        storage_method = storage_methods[StorageMethods(storage_method_name)]
        run(connection, storage_method)
    except (KeyError, ValueError):
        print(f"Not supported storage method '{storage_method_name}'")


def send_to_pipeline(data: list, file_count: int) -> None:
    pass


def save_to_file(data: list, file_count: int) -> None:
    timestamp = int(round(time.time() * 1000))

    filename = f"seismograph_{str(timestamp)}_{str(file_count)}.txt"
    filepath = os.path.join(ROOT_PATH, 'data', filename)

    print(f"Saving samples to {filepath}")
    with open(filepath, 'w') as file:
        while len(data) > 0:
            file.write(data.pop(0).decode())
            file.write("\n")


def run(connection: SeismographConnection, storage_method: types.FunctionType) -> None:
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
            process = Process(target=storage_method, args=(samples, file_count))
            process.daemon = True
            process.start()

            samples = []
            file_count += 1

        connection.ack_message(address)


if __name__ == "__main__":
    main()

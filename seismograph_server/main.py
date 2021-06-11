import socket
import time
import os
from pathlib import Path
from multiprocessing import Process

SERVER_PORT = 20001
BUFFER_SIZE = 1024
RESPONSE_MSG = str.encode("ACK")
MAX_SAMPLES = 100

ROOT_PATH = Path(__file__).parent.parent


def main():
    server_ip = "192.168.67.23"
    run(server_ip)


def save_to_file(data: list, file_count: int):
    timestamp = int(round(time.time() * 1000))

    filename = f"seismograph_{str(timestamp)}_{str(file_count)}.txt"
    filepath = os.path.join(ROOT_PATH, 'data', filename)

    print(f"Saving samples to {filepath}")
    with open(filepath, 'w') as file:
        while len(data) > 0:
            file.write(data.pop(0).decode())
            file.write("\n")


def run(server_ip: str):
    udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_server_socket.bind((server_ip, SERVER_PORT))

    samples = []
    file_count = 1

    print(f"Running seismograph server on UDP port {SERVER_PORT}")
    while True:
        message = udp_server_socket.recvfrom(BUFFER_SIZE)

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
            process = Process(target=save_to_file, args=(samples, file_count))
            process.daemon = True
            process.start()

            samples = []
            file_count += 1

        udp_server_socket.sendto(RESPONSE_MSG, address)


if __name__ == "__main__":
    main()

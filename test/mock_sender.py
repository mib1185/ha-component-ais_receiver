"""Derived from https://github.com/M0r13n/pyais/blob/master/tests/mock_sender.py."""

import socket
import time

HOST = "127.0.0.1"
PORT = 12346
MESSAGES: list[bytes] = [
    # add here the messages to send as list of byte strings - example:
    # b'!AIVDM,1,1,,B,339edFP00fPwMwPM<294tku@R000,0*26'
]


def udp_mock_server(host, port) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        while True:
            while True:
                print(f"Sending {len(MESSAGES)} messages, one every 0.3 seconds.")
                for msg in MESSAGES:
                    sock.sendto(msg + b"\r\n", (host, port))
                    time.sleep(0.3)
                break
            break
    finally:
        sock.close()


if __name__ == "__main__":
    print(f"Starting Mock UDP server on {HOST}:{PORT}")
    udp_mock_server(HOST, PORT)

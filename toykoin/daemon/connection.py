from hashlib import sha256
import threading
import socket


def add_headers(name: str, payload: bytes):
    command = name + ((12 - len(name)) * "\00")
    payload_len = len(payload).to_bytes(4, "big")
    checksum = sha256(sha256(payload).digest()).digest()[:4]
    return command.encode() + payload_len + checksum + payload


def _verify_headers(message: bytes):
    message_type = message[:12]
    payload_len = int.from_bytes(message[12:16], "big")
    checksum = message[16:20]
    payload = message[20:]
    if len(payload) != payload_len:
        raise Exception("Wrong payload length")
    if checksum != sha256(sha256(payload).digest()).digest()[:4]:
        raise Exception("Wrong checksum, the message might have been tampered")


def get_payload(message: bytes):
    try:
        _verify_headers(message)
    except Exception:
        raise Exception("Incorrect headers")
    message_type = message[:12].rstrip(b"\x00")
    payload = message[20:]

    return [message_type, payload]


class Connection(threading.Thread):
    def __init__(self, socket, address, network="regtest"):
        super().__init__()
        self.socket = socket
        self.address = address
        self.terminate_flag = threading.Event()
        self.network = network.encode()
        self.messages = []
        self.buffer = b""

    def send(self, data):
        self.socket.sendall(self.network + data)

    def stop(self):
        self.terminate_flag.set()

    def parse_messages(self):
        msgs = self.buffer.split(self.network)
        if not msgs[0]:
            msgs = msgs[1:]
            self.buffer = self.buffer[len(self.network) :]
        for i, msg in enumerate(msgs):
            try:
                payload = get_payload(msg)
                self.messages.append(payload)
                self.buffer = self.buffer[len(msg) + len(self.network) :]
            except Exception:
                if i != len(msgs) - 1:
                    self.buffer = self.buffer[len(msg) + len(self.network) :]

    def run(self):
        self.socket.settimeout(0.0)
        while not self.terminate_flag.is_set():
            try:
                line = self.socket.recv(4096)
                self.buffer += line
                self.parse_messages()
            except socket.error:
                pass
            except Exception:
                self.terminate_flag.set()

    def __repr__(self):
        return f"Connection to {self.address[0]}:{self.address[1]}"

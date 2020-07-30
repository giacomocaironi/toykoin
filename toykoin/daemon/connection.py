from toykoin.daemon.messages import get_payload, Version, Verack

import threading
import socket
import time


class Connection(threading.Thread):
    def __init__(self, socket, address, node):
        super().__init__()

        self.node = node
        self.socket = socket
        self.address = list(address)

        self.terminate_flag = threading.Event()
        self.network = node.network.encode()

        self.messages = []
        self.buffer = b""

        self.received_version = False
        self.connected = False
        self.conn_time = time.time()
        self.connect()

    def send(self, data):
        self.socket.sendall(self.network + data)

    def stop(self):
        self.terminate_flag.set()

    def connect(self):
        self.send(Version(version=1, port=self.node.port).serialize())

    def validate_handshake(self):
        if not self.received_version:
            if self.messages:
                # first message must be version
                if not self.messages[0][0] == "version":
                    self.stop()
                else:
                    version_message = Version.deserialize(self.messages[0][1])
                    if version_message.accept():
                        self.address[1] = version_message.port
                        self.send(Verack().serialize())
                        self.messages = self.messages[1:]
                        self.received_version = True
                    else:
                        self.stop()
        if self.received_version and not self.connected:
            if self.messages:
                # second message must be verack
                if not self.messages[0][0] == "verack":
                    self.stop()
                else:
                    self.messages = self.messages[1:]
                    self.connected = True

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

    def handle_messages(self):
        if not self.connected:
            self.validate_handshake()
        else:
            pass

    def run(self):
        self.socket.settimeout(0.0)
        while not self.terminate_flag.is_set():
            try:  # TODO: exit if other side is closed
                line = self.socket.recv(4096)
                self.buffer += line
                self.parse_messages()
                if self.messages:
                    self.handle_messages()
            except socket.error:
                pass
            except Exception as e:
                print(e)
                self.terminate_flag.set()

    def __repr__(self):
        return f"Connection to {self.address[0]}:{self.address[1]}"

from toykoin.core.utils import hash256

from dataclasses import dataclass


def add_headers(name: str, payload: bytes):
    command = name + ((12 - len(name)) * "\00")
    payload_len = len(payload).to_bytes(4, "big")
    checksum = hash256(payload)[:4]
    return command.encode() + payload_len + checksum + payload


def _verify_headers(message: bytes):
    message_type = message[:12]
    payload_len = int.from_bytes(message[12:16], "big")
    checksum = message[16:20]
    payload = message[20:]
    if len(payload) != payload_len:
        raise Exception("Wrong payload length")
    if checksum != hash256(payload)[:4]:
        raise Exception("Wrong checksum, the message might have been tampered")


def get_payload(message: bytes):
    try:
        _verify_headers(message)
    except Exception:
        raise Exception("Incorrect headers")
    message_type = message[:12].rstrip(b"\x00").decode()
    payload = message[20:]

    return [message_type, payload]


@dataclass
class Version:
    version: int
    address: str

    @staticmethod
    def deserialize(cls, data):
        pass

    def serialize(self):
        payload = self.version.to_bytes(2, "big")
        payload += self.address.encode()
        return add_headers("version", payload)


@dataclass
class Verack:
    @staticmethod
    def deserialize(cls, data):
        pass

    def serialize(self):
        return add_headers("verack", b"")


@dataclass
class Debug:
    payload: bytes

    @staticmethod
    def deserialize(cls, data):
        pass

    def serialize(self):
        return add_headers("debug", self.payload)

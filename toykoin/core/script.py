from dataclasses import dataclass


@dataclass
class Script:
    def __init__(self, hex=""):
        self.hex = hex
        self.hashes = []

    def __add__(self, other):
        hex = self.hex + other.hex
        return Script(hex)

    def serialize(self):
        return bytes.fromhex(self.hex)

    @classmethod
    def deserialize(cls, data):
        return Script()

    def is_valid(self):
        return len(self.serialize()) < 256 ** 2

    def execute(self):
        return True

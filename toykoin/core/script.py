from dataclasses import dataclass, field
from typing import List
from btclib.utils import hash256
from btclib import ssa


@dataclass
class Script:
    expressions: List[str] = field(default_factory=list)

    def __add__(self, other):
        expressions = self.expressions + other.expressions
        return Script(expressions)

    def serialize(self):
        out = b""
        for expression in self.expressions:
            out += (len(expression[2]) + 2).to_bytes(2, "big")
            out += expression[0].to_bytes(1, "big")
            out += expression[1].to_bytes(1, "big")
            out += expression[2]
        return out

    @classmethod
    def deserialize(cls, data):
        expressions = []
        while data:
            expression_len = int.from_bytes(data[:2], "big")
            data = data[2:]
            var = data[0]
            func = data[1]
            expression_data = data[2:expression_len]
            data = data[expression_len:]
            expressions.append([var, func, expression_data])
        return cls(expressions=expressions)

    @property
    def hex(self):
        return self.serialize().hex()

    @classmethod
    def from_hex(cls, hex_data):
        return cls.deserialize(bytes.fromhex(hex_data))

    def is_valid(self):
        return len(self.serialize()) < 256 ** 2

    def execute(self):
        return _execute_script(self)


def _pushdata(variable, data, memory):
    memory[variable] = data


def _equal(variable, data, memory):
    if memory[data[0]] == memory[data[1]]:
        memory[variable] = b"\x01"
    else:
        memory[variable] = b"\x00"


def _hash256(variable, data, memory):
    memory[variable] = hash256(memory[data[0]])


def _schnorr_checksig(variable, data, memory):
    is_valid = ssa._verify(memory[0x100], memory[data[0]], memory[data[1]])
    if is_valid:
        memory[variable] = b"\x01"
    else:
        memory[variable] = b"\x00"


def _verify(variable, data, memory):
    if not bool(memory[data[0]][0]):
        raise Exception


FUNCTIONS = {
    0x00: _pushdata,
    0x01: _equal,
    0x02: _hash256,
    0x03: _schnorr_checksig,
    0x04: _verify,
}


def _execute_script(script):
    memory = {0x100: script.sighashes[0]}
    for variable, function, data in script.expressions:
        try:
            FUNCTIONS[function](variable, data, memory)
        except:
            return False
    return True

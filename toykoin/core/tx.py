from toykoin.core.utils import hash256
from toykoin.core.script import Script

from dataclasses import dataclass
from typing import List


@dataclass
class OutPoint:
    hash: str
    index: int

    @property
    def hex(self):
        return self.hash + self.index.to_bytes(2, "big").hex()

    def serialize(self):
        return bytes.fromhex(self.hex)

    @classmethod
    def deserialize(cls, data):
        hash = data[:32].hex()
        index = int.from_bytes(data[32:34], "big")
        return OutPoint(hash, index)

    def is_coinbase(self):
        return self.hash == "00" * 32 and self.index == 0

    def is_valid(self):
        if not 0 <= self.index < 256 ** 2:
            return False
        return True


@dataclass
class TxIn:
    prevout: OutPoint
    unlocking_script: Script = Script()

    def serialize(self):
        out = self.prevout.serialize()
        script_bytes = self.unlocking_script.serialize()
        out += len(script_bytes).to_bytes(2, "big") + script_bytes
        return out

    @classmethod
    def deserialize(cls, data):
        prevout = OutPoint.deserialize(data)
        script_len = int.from_bytes(data[34:36], "big")
        unlocking_script = Script.deserialize(data[36 : 36 + script_len])
        return TxIn(prevout, unlocking_script)

    def is_coinbase(self):
        return self.prevout.is_coinbase()

    def is_valid(self):
        if not self.unlocking_script.is_valid():
            return False
        if not self.prevout.is_valid():
            return False
        return True


@dataclass
class TxOut:
    value: int = 0
    locking_script: Script = Script()

    def serialize(self):
        out = self.value.to_bytes(8, "big")
        script_bytes = self.locking_script.serialize()
        out += len(script_bytes).to_bytes(2, "big") + script_bytes
        return out

    @classmethod
    def deserialize(cls, data):
        out = int.from_bytes(data[:8], "big")
        script_len = int.from_bytes(data[8:10], "big")
        locking_script = Script.deserialize(data[10 : 10 + script_len])
        return TxOut(out, locking_script)

    def is_valid(self):
        if not self.locking_script.is_valid():
            return False
        if self.value < 0 or self.value >= 256 ** 8:
            return False
        return True


@dataclass
class Tx:
    inputs: List[TxIn]
    outputs: List[TxOut]

    def serialize(self):
        out = len(self.inputs).to_bytes(2, "big")
        for tx_in in self.inputs:
            tx_in_bytes = tx_in.serialize()
            out += len(tx_in_bytes).to_bytes(2, "big") + tx_in_bytes
        out += len(self.outputs).to_bytes(2, "big")
        for tx_out in self.outputs:
            tx_out_bytes = tx_out.serialize()
            out += len(tx_out_bytes).to_bytes(2, "big") + tx_out_bytes
        return out

    @classmethod
    def deserialize(cls, data):
        inputs = []
        inputs_len = int.from_bytes(data[:2], "big")
        data = data[2:]
        for i in range(inputs_len):
            input_len = int.from_bytes(data[:2], "big")
            data = data[2:]
            inputs.append(TxIn.deserialize(data[:input_len]))
            data = data[input_len:]
        outputs = []
        outputs_len = int.from_bytes(data[:2], "big")
        data = data[2:]
        for i in range(outputs_len):
            output_len = int.from_bytes(data[:2], "big")
            data = data[2:]
            outputs.append(TxOut.deserialize(data[:output_len]))
            data = data[output_len:]
        return Tx(inputs, outputs)

    def is_coinbase(self):
        return len(self.inputs) == 1 and self.inputs[0].is_coinbase()

    # confirm that is a valid transaction only by looking at its data, without looking at the blockchain
    def is_valid(self):
        outpoints = []
        coinbase = self.is_coinbase()
        for tx_in in self.inputs:
            # the transaction is not coinbase but has a coinbase input
            if tx_in.is_coinbase() and not coinbase:
                return False
            if tx_in.prevout in outpoints:  # duplicate reference
                return False
            outpoints.append(tx_in.prevout)
            if not tx_in.is_valid():
                return False
        for tx_out in self.outputs:
            if not tx_out.is_valid():
                return False
        return True

    @property
    def txid(self):
        return hash256(self.serialize()).hex()

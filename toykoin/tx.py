from btclib.utils import hash256
from .script import Script
from dataclasses import dataclass


@dataclass
class TxIn:
    def __init__(
        self, previous_tx_hash="", previous_txout_index=0, unlocking_script=Script()
    ):
        self.previous_tx_hash = previous_tx_hash
        self.previous_txout_index = previous_txout_index
        self.unlocking_script = unlocking_script

    def serialize(self):
        out = bytes.fromhex(self.previous_tx_hash)
        out += self.previous_txout_index.to_bytes(2, "big")
        script_bytes = self.unlocking_script.serialize()
        out += len(script_bytes).to_bytes(2, "big") + script_bytes
        return out

    @classmethod
    def deserialize(cls, data):
        previous_tx_hash = data[:32].hex()
        previous_txout_index = int.from_bytes(data[32:34], "big")
        script_len = int.from_bytes(data[34:36], "big")
        unlocking_script = Script.deserialize(data[36 : 36 + script_len])
        return TxIn(previous_tx_hash, previous_txout_index, unlocking_script)

    def is_valid(self):
        if not self.unlocking_script.is_valid():
            return False
        return self.previous_txout_index < 256 ** 2


@dataclass
class TxOut:
    def __init__(self, value=0, locking_script=Script()):
        self.value = value
        self.locking_script = locking_script

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
        return self.locking_script.is_valid()


@dataclass
class Tx:
    def __init__(self, inputs=[], outputs=[]):
        self.inputs = inputs
        self.outputs = outputs

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

    def is_valid(self):
        outpoints = []
        for tx_in in self.inputs:
            outpoint = (
                tx_in.previous_tx_hash
                + tx_in.previous_txout_index.to_bytes(2, "big").hex()
            )
            if outpoint in outpoints:  # duplicate reference
                return False
            outpoints.append(outpoint)
            if not tx_in.is_valid():
                return False
        for tx_out in self.outputs:
            if not tx_out.is_valid():
                return False
        return True

    @property
    def txid(self):
        hash256(self.serialize()).hex()

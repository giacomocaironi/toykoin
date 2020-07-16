from toykoin.core.utils import generate_merkle_root
from toykoin.core.tx import Tx, TxOut, OutPoint
from toykoin.core.utils import hash256

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class BlockHeader:
    previous_pow: str = ""
    merkle_root: str = ""
    nonce: int = 0

    def serialize(self):
        out = bytes.fromhex(self.previous_pow)
        out += bytes.fromhex(self.merkle_root)
        out += self.nonce.to_bytes(12, "big")
        return out

    @classmethod
    def deserialize(cls, data):
        previous_pow = data[:32].hex()
        merkle_root = data[32:64].hex()
        nonce = int.from_bytes(data[64:76], "big")
        return BlockHeader(previous_pow, merkle_root, nonce)

    def is_valid(self):
        if len(self.previous_pow) != 64:
            return False
        if len(self.merkle_root) != 64:
            return False
        return True

    @property
    def pow(self):
        return hash256(self.serialize()).hex()


@dataclass
class Block:
    header: BlockHeader
    transactions: List[Tx]

    def serialize(self):
        out = self.header.serialize()
        out += len(self.transactions).to_bytes(2, "big")
        for tx in self.transactions:
            tx_bytes = tx.serialize()
            out += len(tx_bytes).to_bytes(2, "big") + tx_bytes
        return out

    @classmethod
    def deserialize(cls, data):
        header = BlockHeader.deserialize(data[:76])
        transactions = []
        transaction_count = int.from_bytes(data[76:78], "big")
        data = data[78:]
        for i in range(transaction_count):
            tx_size = int.from_bytes(data[:2], "big")
            transactions.append(Tx.deserialize(data[2 : 2 + tx_size]))
            data = data[2 + tx_size :]
        return Block(header, transactions)

    def is_valid(self):
        if not self.header.is_valid():
            return False
        if len(self.transactions) < 1:
            return False
        merkle_root = generate_merkle_root(self.transactions)
        if not merkle_root == self.header.merkle_root:
            return False
        if (
            not self.transactions[0].is_coinbase()
            or not self.transactions[0].is_valid()
        ):
            return False
        for tx in self.transactions[1:]:
            if tx.is_coinbase() or not tx.is_valid():
                return False
        return True


@dataclass
class RevBlock:
    pow: str
    old_txout: List[Tuple[str, TxOut]]
    removable: List[str]

    def serialize(self):
        out = bytes.fromhex(self.pow)
        out += len(self.old_txout).to_bytes(2, "big")
        for txout in self.old_txout:
            out += bytes.fromhex(txout[0])
            tx_bytes = txout[1].serialize()
            out += len(tx_bytes).to_bytes(2, "big") + tx_bytes
        out += len(self.removable).to_bytes(2, "big")
        for txout in self.removable:
            out += bytes.fromhex(txout)
        return out

    @classmethod
    def deserialize(cls, data):
        pow = data[:32].hex()
        data = data[32:]
        old_txout = []
        removable = []
        len_txout_list = int.from_bytes(data[:2], "big")
        data = data[2:]
        for x in range(len_txout_list):
            id = data[:34].hex()
            data = data[34:]
            txout_size = int.from_bytes(data[:2], "big")
            txout = TxOut.deserialize(data[2 : 2 + txout_size])
            old_txout.append([id, txout])
            data = data[2 + txout_size :]

        len_removable = int.from_bytes(data[:2], "big")
        data = data[2:]
        for x in range(len_removable):
            removable.append(data[:34].hex())
            data = data[34:]
        return RevBlock(pow, old_txout, removable)

    def is_valid(self):
        if len(self.pow) != 64:
            return False
        for txout in self.old_txout:
            if not txout[1].is_valid():
                return False
            if OutPoint.deserialize(bytes.fromhex(txout[0])).is_coinbase():
                return False
        return True

from dataclasses import dataclass
from toykoin.utils import generate_merkle_root
from toykoin.tx import Tx
from toykoin.utils import hash256
from typing import List


@dataclass
class BlockHeader:
    previous_block_hash: str = ""
    merkle_root: str = ""
    nonce: int = 0

    def serialize(self):
        out = bytes.fromhex(self.previous_block_hash)
        out += bytes.fromhex(self.merkle_root)
        out += self.nonce.to_bytes(12, "big")
        return out

    @classmethod
    def deserialize(cls, data):
        previous_block_hash = data[:32].hex()
        merkle_root = data[32:64].hex()
        nonce = int.from_bytes(data[64:76], "big")
        return BlockHeader(previous_block_hash, merkle_root, nonce)

    def is_valid(self):
        if len(self.previous_block_hash) != 64:
            return False
        if len(self.merkle_root) != 64:
            return False
        return True

    @property
    def hash(self):
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
        if not self.transactions[0].is_coinbase():
            return False
        if not self.transactions[0].is_valid():
            return False
        for tx in self.transactions[1:]:
            if tx.is_coinbase() or not tx.is_valid():
                return False
        return True

from toykoin.core.block import Block, BlockHeader
from dataclasses import dataclass


class UTXOSet:
    def __init__(self):
        self.utxo_list = {}

    # confirm is a valid transaction by
    def validate_transaction(self, tx):

        if not tx.is_valid():
            return False

        available_value = 0
        spending_value = 0
        previous_outputs = []
        for tx_in in tx.inputs:
            id = tx_in.previous_tx_hash
            id += tx_in.previous_txout_index.to_bytes(2, "big").hex()
            if id not in self.utxo_list.keys():
                return False
            tx_out = self.utxo_list[id]
            previous_outputs.append(tx_out)
            available_value += tx_out.value

        for tx_out in tx.outputs:
            spending_value += tx_out.value

        if spending_value > available_value:
            return False

        for tx_in, tx_out in zip(tx.inputs, previous_outputs):
            script = tx_out.locking_script + tx_in.unlocking_script
            script.hashes = []  # insert tx_out hashes
            result = script.execute()
            if not result:
                return False
        return True

    def validate_block(self, block):
        print(block)
        if not block.is_valid():
            return False
        for tx in block.transactions[1:]:  # do not check the coinbases
            if not self.validate_transaction(tx):
                return False
        # check if miner is collecting fees in the right way
        total_value = 0
        for tx in block.transactions[1:]:
            for tx_in in tx.inputs:
                id = tx_in.previous_tx_hash
                id += tx_in.previous_txout_index.to_bytes(2, "big").hex()
                total_value += self.utxo_list[id].value
            for tx_out in tx.outputs:
                total_value -= tx_out.value
        for tx_out in block.transactions[0].outputs:
            total_value -= tx_out.value
        print(total_value)
        if 10 ** 10 + total_value < 0:
            return False
        return True

    def add_block(self, block):
        for i, tx_out in enumerate(block.transactions[0].outputs):
            complete_id = block.transactions[0].txid + i.to_bytes(2, "big").hex()
            self.utxo_list[complete_id] = tx_out
        for tx in block.transactions[1:]:
            for i, tx_out in enumerate(tx.outputs):
                complete_id = tx.txid + i.to_bytes(2, "big").hex()
                self.utxo_list[complete_id] = tx_out
            for i, tx_in in enumerate(tx.inputs):
                complete_id = tx_in.previous_tx_hash + i.to_bytes(2, "big").hex()
                del self.utxo_list[complete_id]

    def reverse_block(self, rev_block):
        pass


@dataclass
class RevBlock:
    pass

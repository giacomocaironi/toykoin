from toykoin.utxo import UTXOSet


class Blockchain:
    def __init__(self):
        self.main_utxo_set = UTXOSet()
        self.last_block_hash = "00" * 32

    def add_block(self, block):
        if block.header.previous_block_hash != self.last_block_hash:
            raise Exception
        if not self.main_utxo_set.validate_block(block):
            raise Exception
        self.main_utxo_set.add_block(block)
        self.last_block_hash = block.header.hash

    def reorganize(self, blocks):
        pass

from toykoin.core.utxo import UTXOSet

import os


class BlockchainConfig:
    pass


class Blockchain:
    def __init__(self, name="regtest"):
        self.current_dir = os.path.join(os.path.expanduser("~"), ".toykoin", name)
        os.makedirs(self.current_dir, exist_ok=True)
        os.makedirs(os.path.join(self.current_dir, "blocks"), exist_ok=True)
        os.makedirs(os.path.join(self.current_dir, "rev"), exist_ok=True)
        os.makedirs(os.path.join(self.current_dir, "chainstate"), exist_ok=True)
        self.main_utxo_set = UTXOSet(in_memory=True)
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

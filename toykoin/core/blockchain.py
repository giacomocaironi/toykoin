from toykoin.core.utxo import UTXOSet

import os
import sqlite3


class BlockchainConfig:
    pass


class Blockchain:
    def __init__(self, name="regtest"):
        self.base_dir = os.path.join(os.path.expanduser("~"), ".toykoin", name)
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "blocks"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "rev"), exist_ok=True)
        self.last_block_hash = "00" * 32

        self.main_utxo_set = UTXOSet(self.base_dir)
        self.db = sqlite3.connect(os.path.join(self.base_dir, "chainstate.sqlite"))
        self.cursor = self.db.cursor()
        try:  # initializing db
            self.cursor.execute("CREATE TABLE header (hash, previous_hash)")
        except:
            pass

    def get_last_block(self):
        self.cursor.execute(
            "SELECT hash FROM header WHERE hash NOT IN (SELECT previous_hash FROM header)"
        )
        last_hash = self.cursor.fetchall()
        # print(last_hash)
        if len(last_hash) != 1:
            raise Exception  # multiple blocks without child
        else:
            return last_hash[0][0]

    def _add_block(self, block):
        previous_hash = block.header.previous_block_hash
        if previous_hash != "00" * 32 and previous_hash != self.get_last_block():
            raise Exception
        if not self.main_utxo_set.validate_block(block):
            raise Exception
        reverse_block = self.main_utxo_set.add_block(block)
        self.cursor.execute(
            "INSERT INTO header VALUES (?, ?)",
            (block.header.hash, block.header.previous_block_hash),
        )
        self.last_block_hash = block.header.hash
        filename = os.path.join(self.base_dir, "blocks", block.header.hash + ".block")
        with open(filename, "wb") as f:
            f.write(block.serialize())
        filename = os.path.join(self.base_dir, "rev", block.header.hash + ".rev")
        with open(filename, "wb") as f:
            f.write(reverse_block.serialize())
        return reverse_block

    def _reverse_block(self, rev_block):
        if not self.main_utxo_set.validate_reverse_block(rev_block):
            raise Exception
        self.main_utxo_set.reverse_block(rev_block)
        self.cursor.execute("DELETE FROM header WHERE hash = ?", (rev_block.hash,))

    # it does not raise exceptions, it return True if the blockchain hash been changed
    def add_blocks(self, blocks):
        pass

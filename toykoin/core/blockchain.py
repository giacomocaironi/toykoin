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
        self.last_block_pow = "00" * 32

        self.main_utxo_set = UTXOSet(self.base_dir)
        self.db = sqlite3.connect(os.path.join(self.base_dir, "chainstate.sqlite"))
        self.cursor = self.db.cursor()
        try:  # initializing db
            self.cursor.execute("CREATE TABLE header (pow, previous_pow)")
        except:
            pass

    def get_last_block(self):
        self.cursor.execute(
            "SELECT pow FROM header WHERE pow NOT IN (SELECT previous_pow FROM header)"
        )
        last_pow = self.cursor.fetchall()
        # print(last_pow)
        if len(last_pow) != 1:
            raise Exception  # multiple blocks without child
        else:
            return last_pow[0][0]

    def _add_block(self, block):
        previous_pow = block.header.previous_pow
        if previous_pow != "00" * 32 and previous_pow != self.get_last_block():
            raise Exception
        if not self.main_utxo_set.validate_block(block):
            raise Exception
        reverse_block = self.main_utxo_set.add_block(block)
        self.cursor.execute(
            "INSERT INTO header VALUES (?, ?)",
            (block.header.pow, block.header.previous_pow),
        )
        self.last_block_pow = block.header.pow
        filename = os.path.join(self.base_dir, "blocks", block.header.pow + ".block")
        with open(filename, "wb") as f:
            f.write(block.serialize())
        filename = os.path.join(self.base_dir, "rev", block.header.pow + ".rev")
        with open(filename, "wb") as f:
            f.write(reverse_block.serialize())
        return reverse_block

    def _reverse_block(self, rev_block):
        if rev_block.pow != self.get_last_block():
            raise Exception
        if not self.main_utxo_set.validate_reverse_block(rev_block):
            raise Exception
        self.main_utxo_set.reverse_block(rev_block)
        self.cursor.execute("DELETE FROM header WHERE pow = ?", (rev_block.pow,))

    # it does not raise exceptions, it return True if the blockchain pow been changed
    def add_blocks(self, blocks):
        pass

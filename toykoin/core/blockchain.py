from toykoin.core.utxo import UTXOSet
from toykoin.core.block import RevBlock
from toykoin.core.pow import work_from_chain

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
            self.cursor.execute("CREATE TABLE header (pow, previous_pow, id)")
        except:
            pass

    def get_block(self, pow):
        self.cursor.execute("SELECT * FROM header WHERE pow = ?", (pow,))
        block = self.cursor.fetchall()
        return block[0] if block else None

    def get_last_blocks(self, n=1):
        self.cursor.execute(
            "SELECT * FROM header WHERE id > (SELECT MAX(id) FROM header) -?", (n,)
        )
        last_pow = self.cursor.fetchall()
        if not last_pow:
            return [[None, None, -1]]
        else:
            return last_pow

    def _add_block(self, block):
        previous_pow = block.header.previous_pow
        if previous_pow != "00" * 32 and previous_pow != self.get_last_blocks()[0][0]:
            raise Exception
        if not self.main_utxo_set.validate_block(block):
            raise Exception
        reverse_block = self.main_utxo_set.add_block(block)
        self.cursor.execute(
            "INSERT INTO header VALUES (?, ?, ?)",
            (
                block.header.pow,
                block.header.previous_pow,
                self.get_last_blocks()[0][2] + 1,
            ),
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
        if rev_block.pow != self.get_last_blocks()[0][0]:
            raise Exception
        if not self.main_utxo_set.validate_reverse_block(rev_block):
            raise Exception
        self.main_utxo_set.reverse_block(rev_block)
        self.cursor.execute("DELETE FROM header WHERE pow = ?", (rev_block.pow,))

    # it does not raise exceptions, it return True if the blockchain pow been changed
    def add_blocks(self, blocks):

        for i, block in enumerate(blocks):
            if not self.get_block(block.header.pow):  # first new block
                blocks = blocks[i:]
                break

        try:  # tries to add enough blocks to be in the best chain

            last_valid_block = self.get_block(blocks[0].header.previous_pow)
            if last_valid_block:  # if it is not the first block
                last_valid_index = self.get_block(last_valid_block[0])[2]
                last_index = self.get_last_blocks()[0][2]
                if last_index - last_valid_index > 0:
                    reverse_blocks = self.get_last_blocks(last_index - last_valid_index)
                    for rev_block in reverse_blocks:
                        filename = os.path.join(
                            self.base_dir, "rev", rev_block[0] + ".rev"
                        )
                        with open(filename, "rb") as f:
                            rev_block = RevBlock.deserialize(f.read())
                        self._reverse_block(rev_block)

                    previous_work = work_from_chain([rev[0] for rev in reverse_blocks])
                    current_chain = []
                    blocks = (i for i in blocks)  # change to iterator
                    for block in blocks:
                        self._add_block(block)
                        current_chain.append(block.header.pow)
                        if work_from_chain(current_chain) > previous_work:
                            break  # already in best chain

            self.main_utxo_set.db.commit()
            self.db.commit()
        except Exception as e:
            print(e)
            self.main_utxo_set.db.rollback()
            self.db.rollback()
            return False

        for block in blocks:
            try:
                self._add_block(block)
                self.main_utxo_set.db.commit()
                self.db.commit()
            except:
                self.main_utxo_set.db.rollback()
                self.db.rollback()
        return True

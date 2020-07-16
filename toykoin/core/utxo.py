from toykoin.core.block import Block, BlockHeader, RevBlock
from toykoin.core.tx import OutPoint, TxOut
from toykoin.core.script import Script

import os
import sqlite3


class UTXOSet:
    def __init__(self, location="", name="main_utxo_set"):
        self.db = sqlite3.connect(os.path.join(location, name + ".sqlite"))
        self.cursor = self.db.cursor()
        try:  # initializing db
            self.cursor.execute("CREATE TABLE utxo (id, value, script)")
        except:
            pass

    def get_utxo_list(self):
        self.cursor.execute("SELECT id FROM utxo")
        id_list = self.cursor.fetchall()
        return id_list

    def get_utxo(self, id):
        self.cursor.execute("SELECT * FROM utxo WHERE id = ?", (id,))
        utxo = self.cursor.fetchall()
        return TxOut(utxo[0][1], Script.deserialize(utxo[0][1])) if utxo else None

    # does not commit to database
    def add_utxo(self, id, utxo):
        self.cursor.execute(
            "INSERT INTO utxo VALUES (?, ?, ?)",
            (id, utxo.value, utxo.locking_script.serialize()),
        )

    # does not commit to database
    def remove_utxo(self, id):
        self.cursor.execute("DELETE FROM utxo WHERE id = ?", (id,))

    # confirm is a valid transaction by
    def validate_transaction(self, tx):

        if not tx.is_valid():
            return False

        available_value = 0
        spending_value = 0
        previous_outputs = []
        for tx_in in tx.inputs:
            id = tx_in.prevout.hex
            tx_out = self.get_utxo(id)
            if not tx_out:
                return False
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

    # check if the coinbase is trying to overwrite previous coinbase outputs
    def validate_coinbase(self, coinbase):
        for i, tx_out in enumerate(coinbase.outputs):
            id = OutPoint(coinbase.txid, i).hex
            if self.get_utxo(id):
                return False
        return True

    def validate_block(self, block):
        if not block.is_valid():
            return False
        if not self.validate_coinbase(block.transactions[0]):
            return False
        for tx in block.transactions[1:]:  # do not check the coinbases
            if not self.validate_transaction(tx):
                return False
        # check if miner is collecting fees in the right way
        total_value = 0
        for tx in block.transactions[1:]:
            for tx_in in tx.inputs:
                id = tx_in.prevout.hex
                total_value += self.get_utxo(id).value
            for tx_out in tx.outputs:
                total_value -= tx_out.value
        for tx_out in block.transactions[0].outputs:
            total_value -= tx_out.value
        if 10 ** 10 + total_value < 0:
            return False
        return True

    def add_block(self, block):
        rev_block = RevBlock(block.header.pow, [], [])
        if not self.validate_block(block):
            raise Exception
        for i, tx_out in enumerate(block.transactions[0].outputs):
            complete_id = OutPoint(block.transactions[0].txid, i).hex
            self.add_utxo(complete_id, tx_out)
            rev_block.removable.append(complete_id)
        for tx in block.transactions[1:]:
            for i, tx_out in enumerate(tx.outputs):
                complete_id = OutPoint(tx.txid, i).hex
                self.add_utxo(complete_id, tx_out)
                rev_block.removable.append(complete_id)
            for i, tx_in in enumerate(tx.inputs):
                complete_id = tx_in.prevout.hex
                rev_block.old_txout.append([complete_id, self.get_utxo(complete_id)])
                self.remove_utxo(complete_id)
        return rev_block

    def validate_reverse_block(self, rev_block):  # TODO
        return True

    def reverse_block(self, rev_block):
        if not self.validate_reverse_block(rev_block):
            raise Exception
        for r_id in rev_block.removable:
            self.remove_utxo(r_id)
        for id, utxo in rev_block.old_txout:
            self.add_utxo(id, utxo)

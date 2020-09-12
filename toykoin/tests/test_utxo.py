from toykoin.core.utxo import UTXOSet
from toykoin.core.tx import Tx, TxIn, TxOut, OutPoint
from toykoin.core.script import Script
from toykoin.core.block import RevBlock

import pytest
import os


def test_invalid_tx():
    utxo_set = UTXOSet()
    tx = Tx(
        [
            TxIn(OutPoint("00" * 32, 0), Script()),
            TxIn(OutPoint("00" * 32, 0), Script()),
        ],
        [TxOut(10 ** 10, Script())],
    )
    assert not utxo_set.validate_transaction(tx)
    os.remove("utxo_set.sqlite")


def test_invalid_rev_block_1():
    utxo_set = UTXOSet()
    rev_block = RevBlock("", [], [])
    rev_block.pow = "00" * 32
    rev_block.old_txout = [[OutPoint("ff" * 32, 0).hex, TxOut(-1)]]
    with pytest.raises(Exception):
        utxo_set.reverse_block(rev_block)
    os.remove("utxo_set.sqlite")


def test_invalid_rev_block_2():
    utxo_set = UTXOSet()
    rev_block = RevBlock("", [], [])
    rev_block.pow = "00" * 32
    rev_block.old_txout = [[OutPoint("00" * 32, 0).hex, TxOut()]]
    with pytest.raises(Exception):
        utxo_set.reverse_block(rev_block)
    os.remove("utxo_set.sqlite")


def test_invalid_rev_block_3():
    utxo_set = UTXOSet()
    rev_block = RevBlock("", [], [])
    rev_block.pow = "00" * 32
    rev_block.removable = [OutPoint("aa" * 32, 0).hex]
    with pytest.raises(Exception):
        utxo_set.reverse_block(rev_block)
    os.remove("utxo_set.sqlite")

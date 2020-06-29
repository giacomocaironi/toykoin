import pytest

from toykoin.tx import TxIn, TxOut, Tx
from toykoin.script import Script


def test_serialization():

    tx_in = TxIn("ff" * 32, 0, Script())
    tx_out = TxOut(10, Script())
    tx = Tx([tx_in], [tx_out])
    assert tx == Tx.deserialize(tx.serialize())
    assert tx.is_valid()

    tx_in_2 = TxIn("ff" * 32, 1, Script())
    tx = Tx([tx_in, tx_in_2], [tx_out])
    assert tx == Tx.deserialize(tx.serialize())
    assert tx.is_valid()


def test_validation():

    tx_in = TxIn("ff" * 32, 0, Script())
    assert tx_in.is_valid()

    tx_out = TxOut(10, Script())
    assert tx_out.is_valid()

    tx_in_valid = TxIn("ff" * 32, 0, Script("ff" * (256 ** 2 - 1)))
    assert tx_in_valid.is_valid()

    tx_out_valid = TxOut(10, Script("ff" * (256 ** 2 - 1)))
    assert tx_out_valid.is_valid()

    tx_in_invalid = TxIn("ff" * 32, 0, Script("ff" * 256 ** 2))
    assert not tx_in_invalid.is_valid()

    tx_out_invalid = TxOut(10, Script("ff" * 256 ** 2))
    assert not tx_out_invalid.is_valid()

    tx = Tx([tx_in_invalid], [tx_out_valid])
    assert not tx.is_valid()

    tx = Tx([tx_in_valid], [tx_out_invalid])
    assert not tx.is_valid()

    tx_in = TxIn("ff" * 32, 0, Script())
    tx_out = TxOut(10, Script())
    tx = Tx([tx_in], [tx_out])
    assert tx.is_valid()

    tx_in_2 = TxIn("ff" * 32, 0, Script())
    tx = Tx([tx_in, tx_in_2], [tx_out])
    assert not tx.is_valid()

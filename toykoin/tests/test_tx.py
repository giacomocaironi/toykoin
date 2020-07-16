import pytest

from toykoin.core.tx import TxIn, TxOut, Tx, OutPoint
from toykoin.core.script import Script


def test_valid_serialization():

    tx_in = TxIn(OutPoint("ff" * 32, 0), Script())
    tx_out = TxOut(10, Script())
    tx = Tx([tx_in], [tx_out])
    assert tx == Tx.deserialize(tx.serialize())

    tx_in_2 = TxIn(OutPoint("ff" * 32, 1), Script())
    tx = Tx([tx_in, tx_in_2], [tx_out])
    assert tx == Tx.deserialize(tx.serialize())


def test_invalid_serialization():

    tx_in = TxIn(OutPoint("ff" * 31, 0), Script())
    tx_out = TxOut(10, Script())
    tx = Tx([tx_in], [tx_out])
    assert not tx == Tx.deserialize(tx.serialize())

    tx_in_2 = TxIn(OutPoint("ff" * 31, 1), Script())
    tx = Tx([tx_in, tx_in_2], [tx_out])
    assert not tx == Tx.deserialize(tx.serialize())


def test_coinbase():

    tx_in = TxIn(OutPoint("00" * 32, 0), Script())
    assert tx_in.is_coinbase()


def test_validation():

    tx_in = TxIn(OutPoint("ff" * 32, 0), Script())
    assert tx_in.is_valid()

    tx_out = TxOut(10, Script())
    assert tx_out.is_valid()

    tx_in_valid = TxIn(OutPoint("ff" * 32, 0), Script("ff" * (256 ** 2 - 1)))
    assert tx_in_valid.is_valid()

    tx_out_valid = TxOut(10, Script("ff" * (256 ** 2 - 1)))
    assert tx_out_valid.is_valid()

    tx_in_invalid = TxIn(OutPoint("ff" * 32, 0), Script("ff" * 256 ** 2))
    assert not tx_in_invalid.is_valid()

    tx_out_invalid = TxOut(10, Script("ff" * 256 ** 2))
    assert not tx_out_invalid.is_valid()

    tx = Tx([tx_in_invalid], [tx_out_valid])
    assert not tx.is_valid()

    tx = Tx([tx_in_valid], [tx_out_invalid])
    assert not tx.is_valid()

    tx_in = TxIn(OutPoint("ff" * 32, 0), Script())
    tx_out = TxOut(10, Script())
    tx = Tx([tx_in], [tx_out])
    assert tx.is_valid()

    tx_in_2 = TxIn(OutPoint("ff" * 32, 0), Script())
    tx = Tx([tx_in, tx_in_2], [tx_out])
    assert not tx.is_valid()


def test_invalid_outpoint_index():
    tx_in = TxIn(OutPoint("00" * 32, -1), Script())
    assert not tx_in.is_valid()

    tx_in = TxIn(OutPoint("00" * 32, 0xFFFF + 1), Script())
    assert not tx_in.is_valid()


def test_invalid_output_value():
    tx_out = TxOut(-1, Script())
    assert not tx_out.is_valid()

    tx_out = TxOut(0xFFFFFFFFFFFFFFFF + 1, Script())
    assert not tx_out.is_valid()


def test_invalid_coinbase():
    tx = Tx(
        [
            TxIn(OutPoint("00" * 32, 0), Script()),
            TxIn(OutPoint("00" * 32, 0), Script()),
        ],
        [TxOut(1, Script())],
    )
    assert not tx.is_valid()

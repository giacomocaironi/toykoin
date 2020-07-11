import pytest

from toykoin.core.tx import TxIn, TxOut, Tx, OutPoint
from toykoin.core.script import Script
from toykoin.core.block import Block, BlockHeader
from toykoin.core.utils import generate_merkle_root


def test_valid_serialization_1():

    tx_in = TxIn(OutPoint("ff" * 32, 0), Script())
    tx_out = TxOut(10, Script())
    tx_1 = Tx([tx_in], [tx_out])
    header = BlockHeader()
    block = Block(header, [tx_1])
    header.merkle_root = generate_merkle_root(block.transactions)
    header.previous_block_hash = "00" * 32
    assert Block.deserialize(block.serialize()) == block


def test_invalid_serialization_1():

    tx_in = TxIn(OutPoint("ff" * 31, 0), Script())
    tx_out = TxOut(10, Script())
    tx_1 = Tx([tx_in], [tx_out])
    header = BlockHeader()
    block = Block(header, [tx_1])
    header.merkle_root = generate_merkle_root(block.transactions)
    header.previous_block_hash = "00" * 32
    assert not Block.deserialize(block.serialize()) == block


def test_validation_1():

    tx_in = TxIn(OutPoint("ff" * 32, 0), Script())
    tx_out = TxOut(10 ** 10, Script())
    tx_1 = Tx([tx_in], [tx_out])
    header = BlockHeader()
    block = Block(header, [tx_1])
    assert not block.is_valid()

    header.merkle_root = generate_merkle_root(block.transactions)
    header.previous_block_hash = "00" * 32
    assert header.is_valid()
    assert not block.is_valid()  # has not a coinbase tx


def test_validation_2():

    tx_in = TxIn(OutPoint("00" * 32, 0), Script())
    tx_out = TxOut(10 ** 10, Script())
    tx_1 = Tx([tx_in], [tx_out])
    header = BlockHeader()
    block = Block(header, [tx_1])
    assert not block.is_valid()

    header.merkle_root = generate_merkle_root(block.transactions)
    header.previous_block_hash = "00" * 32
    assert header.is_valid()
    assert block.is_valid()  # has a coinbase tx


def test_validation_3():

    tx_in = TxIn(OutPoint("ff" * 32, 256 ** 2 - 1), Script())
    tx_out = TxOut(10, Script())
    tx_1 = Tx([tx_in], [tx_out])
    tx_in_2 = TxIn(OutPoint("ff" * 32, 256 ** 2 - 1), Script())
    tx_out_2 = TxOut(10, Script())
    tx_2 = Tx([tx_in_2], [tx_out_2])
    header = BlockHeader()
    block = Block(header, [tx_1, tx_2])

    header.merkle_root = generate_merkle_root(block.transactions)
    header.previous_block_hash = "00" * 32
    assert header.is_valid()
    assert not block.is_valid()  # two coinbases

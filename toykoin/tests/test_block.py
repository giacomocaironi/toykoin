from toykoin.core.tx import TxIn, TxOut, Tx, OutPoint
from toykoin.core.script import Script
from toykoin.core.block import Block, BlockHeader, RevBlock
from toykoin.core.utils import generate_merkle_root

import pytest


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


def test_reverse_serialization():
    rev_block_bytes = b"\x00\x01\xb8eq\x0e\x05\x8a\xca\x8c\x02\xf2\xae\xfa)\xd1\x0bZP\x94L<9\xbc\x11N1\xb5\xc9CZ\x89\xdb\x1e\x00\x00\x00\n\x00\x00\x00\x02T\x0b\xe4\x00\x00\x00\x00\x02U\xa1\xdf\xbd.g5{(\x18\xf0P\x9f\x9a?\xca/j\xc4\x99\xf1<\xba0\xfd\xb5\x18|\x9c>\x1f\xbc\x00\x00\xc4|v\xb4\x07\x08\x08\x9fQ\xc8?\x9d\xd6\x81b\x16Y)0\x800^\x98\x9d\xfa\xae.4\xfft\x7f\x13\x00\x00"
    assert RevBlock.deserialize(rev_block_bytes).serialize() == rev_block_bytes

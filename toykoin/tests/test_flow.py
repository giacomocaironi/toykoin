from toykoin.core.tx import Tx, TxIn, TxOut
from toykoin.core.block import Block, BlockHeader
from toykoin.core.script import Script
from toykoin.core.utxo import UTXOSet
from toykoin.core.blockchain import Blockchain
from toykoin.core.utils import generate_merkle_root

import pytest


def test_flow_1():
    """
    This MUST NOT fail
    We simply add two blocks, each one with only the coinbase transaction
    """

    coinbase_0 = Tx([TxIn("00" * 32, 0, Script())], [TxOut(10 ** 10, Script())])

    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain.add_block(origin)
    assert blockchain.last_block_hash == origin.header.hash

    coinbase_1 = Tx([TxIn("00" * 32, 0, Script("aa"))], [TxOut(10 ** 10, Script())])
    block_1_header = BlockHeader(
        origin.header.hash, generate_merkle_root([coinbase_1]), 0
    )
    block_1 = Block(block_1_header, [coinbase_1])
    blockchain.add_block(block_1)
    assert blockchain.last_block_hash == block_1.header.hash


def test_flow_2():
    """
    This MUST fail
    We add a block without a coinbase transaction
    """
    coinbase_0 = Tx([TxIn("00" * 32, 0, Script())], [TxOut(10 ** 10, Script())])
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain.add_block(origin)

    tx = Tx([TxIn(coinbase_0.txid, 0, Script())], [TxOut(10 ** 10, Script())])
    block_1_header = BlockHeader(origin.header.hash, generate_merkle_root([tx]), 0)
    block_1 = Block(block_1_header, [tx])
    with pytest.raises(Exception):  # missing coinbase
        blockchain.add_block(block_1)


def test_flow_3():
    """
    This MUST NOT fail
    We add two blocks to the blockchain, the second one with a transaction which spends
    the coinbase 0 output
    """
    coinbase_0 = Tx([TxIn("00" * 32, 0, Script())], [TxOut(10 ** 10, Script())])
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain.add_block(origin)

    coinbase_1 = Tx([TxIn("00" * 32, 0, Script("aa"))], [TxOut(10 ** 10, Script())])
    tx = Tx([TxIn(coinbase_0.txid, 0, Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.hash, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    blockchain.add_block(block_1)


def test_flow_4():
    """
    This MUST fail
    The second block transaction tries to spend more than its input
    """
    coinbase_0 = Tx([TxIn("00" * 32, 0, Script())], [TxOut(10 ** 10, Script())])
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain.add_block(origin)

    coinbase_1 = Tx([TxIn("00" * 32, 0, Script("aa"))], [TxOut(10 ** 10, Script())])
    # overspends
    tx = Tx([TxIn(coinbase_0.txid, 0, Script())], [TxOut(10 ** 10 + 1, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.hash, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    with pytest.raises(Exception):
        blockchain.add_block(block_1)


def test_flow_5():
    """
    This MUST NOT fail
    We add two blocks to the blockchain, the second one with a transaction which spends
    the coinbase 0 output
    """
    coinbase_0 = Tx([TxIn("00" * 32, 0, Script())], [TxOut(10 ** 10, Script())])
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain.add_block(origin)

    coinbase_1 = Tx(
        [TxIn("00" * 32, 0, Script("aa"))], [TxOut(2 * 10 ** 10 - 10 ** 5, Script())]
    )
    tx = Tx([TxIn(coinbase_0.txid, 0, Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.hash, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    blockchain.add_block(block_1)


def test_flow_6():
    """
    This MUST fail
    We add two blocks to the blockchain, the second one with a transaction which spends
    the coinbase 0 output
    """
    coinbase_0 = Tx([TxIn("00" * 32, 0, Script())], [TxOut(10 ** 10, Script())])
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain.add_block(origin)

    coinbase_1 = Tx(
        [TxIn("00" * 32, 0, Script("aa"))],
        [TxOut(2 * 10 ** 10 - 10 ** 5 + 1, Script())],
    )
    tx = Tx([TxIn(coinbase_0.txid, 0, Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.hash, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    with pytest.raises(Exception):
        blockchain.add_block(block_1)

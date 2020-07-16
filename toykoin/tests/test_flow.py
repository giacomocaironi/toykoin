from toykoin.core.tx import Tx, TxIn, TxOut, OutPoint
from toykoin.core.block import Block, BlockHeader
from toykoin.core.script import Script
from toykoin.core.blockchain import Blockchain
from toykoin.core.utils import generate_merkle_root
from toykoin.core.pow import calculate_nonce

import pytest
import os
import shutil


def reset_blockchain():
    base_dir = os.path.join(os.path.expanduser("~"), ".toykoin", "regtest")
    shutil.rmtree(base_dir)


def test_flow_1():
    """
    This MUST NOT fail
    We simply add two blocks, each one with only the coinbase transaction
    """

    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )

    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)
    assert blockchain.last_block_pow == origin.header.pow

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))], [TxOut(10 ** 10, Script())]
    )
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root([coinbase_1]), 0
    )
    block_1 = Block(block_1_header, [coinbase_1])
    blockchain._add_block(block_1)
    assert blockchain.last_block_pow == block_1.header.pow

    reset_blockchain()


def test_flow_2():
    """
    This MUST fail
    We add a block without a coinbase transaction
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)

    tx = Tx([TxIn(OutPoint(coinbase_0.txid, 0), Script())], [TxOut(10 ** 10, Script())])
    block_1_header = BlockHeader(origin.header.pow, generate_merkle_root([tx]), 0)
    block_1 = Block(block_1_header, [tx])
    with pytest.raises(Exception):  # missing coinbase
        blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_3():
    """
    This MUST NOT fail
    We add two blocks to the blockchain, the second one with a transaction which spends
    the coinbase 0 output
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))], [TxOut(10 ** 10, Script())]
    )
    tx = Tx([TxIn(OutPoint(coinbase_0.txid, 0), Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_4():
    """
    This MUST fail
    The second block transaction tries to spend more than its input
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))], [TxOut(10 ** 10, Script())]
    )
    # overspends
    tx = Tx(
        [TxIn(OutPoint(coinbase_0.txid, 0), Script())], [TxOut(10 ** 10 + 1, Script())]
    )
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    with pytest.raises(Exception):
        blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_5():
    """
    This MUST NOT fail
    We add two blocks to the blockchain, the second one with a transaction which spends
    the coinbase 0 output
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))],
        [TxOut(2 * 10 ** 10 - 10 ** 5, Script())],
    )
    tx = Tx([TxIn(OutPoint(coinbase_0.txid, 0), Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_6():
    """
    This MUST fail
    The block 1 coinbase collects more fees than it should
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))],
        [TxOut(2 * 10 ** 10 - 10 ** 5 + 1, Script())],
    )
    tx = Tx([TxIn(OutPoint(coinbase_0.txid, 0), Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    with pytest.raises(Exception):
        blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_7():
    """
    This MUST fail
    The two coinbases have the same txid
    """

    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )

    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)
    assert blockchain.last_block_pow == origin.header.pow

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root([coinbase_1]), 0
    )
    block_1 = Block(block_1_header, [coinbase_1])
    with pytest.raises(Exception):
        blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_8():
    """
    This MUST NOT fail
    Test of block reverse
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    rev_origin = blockchain._add_block(origin)

    old_utxo_list = blockchain.main_utxo_set.get_utxo_list()

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))],
        [TxOut(2 * 10 ** 10 - 10 ** 5, Script())],
    )
    tx = Tx([TxIn(OutPoint(coinbase_0.txid, 0), Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    rev_block = blockchain._add_block(block_1)

    assert not blockchain.main_utxo_set.get_utxo_list() == old_utxo_list
    blockchain._reverse_block(rev_block)
    assert blockchain.main_utxo_set.get_utxo_list() == old_utxo_list

    with pytest.raises(Exception):
        blockchain._reverse_block(rev_block)

    blockchain._reverse_block(rev_origin)
    assert blockchain.main_utxo_set.get_utxo_list() == []

    reset_blockchain()


def test_flow_9():
    """
    This MUST fail
    The transaction tries to spend an unkown utxo
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))], [TxOut(10 ** 10, Script())]
    )
    # tries to spend the coinbase output at index 1, which doesn't exist
    tx = Tx([TxIn(OutPoint(coinbase_0.txid, 1), Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    with pytest.raises(Exception):
        blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_10():
    """
    This MUST fail
    Test of block reverse
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    rev_block_0 = blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))],
        [TxOut(2 * 10 ** 10 - 10 ** 5, Script())],
    )
    tx = Tx([TxIn(OutPoint(coinbase_0.txid, 0), Script())], [TxOut(10 ** 5, Script())])
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    blockchain._add_block(block_1)

    with pytest.raises(Exception):
        blockchain._reverse_block(rev_block_0)

    reset_blockchain()


def test_flow_11():
    """
    This MUST NOT fail
    """
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))],
        [TxOut(5 * 10 ** 9, Script()), TxOut(5 * 10 ** 9, Script())],
    )
    tx = Tx(
        [TxIn(OutPoint(coinbase_0.txid, 0), Script())],
        [TxOut(10 ** 10 - 100, Script()), TxOut(50, Script())],
    )
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)
    blockchain._add_block(block_1)

    coinbase_2 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("bb"))], [TxOut(10 ** 10, Script())]
    )
    tx_2 = Tx([TxIn(OutPoint(tx.txid, 0), Script())], [TxOut(10 ** 10 - 200, Script())])
    tx_3 = Tx(
        [
            TxIn(OutPoint(coinbase_1.txid, 0), Script()),
            TxIn(OutPoint(coinbase_1.txid, 1), Script()),
            TxIn(OutPoint(tx.txid, 1), Script()),
        ],
        [TxOut(10 ** 10 + 50, Script())],
    )
    block_2_transactions = [coinbase_2, tx_2, tx_3]
    block_2_header = BlockHeader(
        block_1.header.pow, generate_merkle_root(block_2_transactions), 0
    )
    block_2 = Block(block_2_header, block_2_transactions)
    blockchain._add_block(block_2)

    reset_blockchain()


def test_flow_12():
    """
    This MUST NOT fail
    """

    blockchain = Blockchain()

    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)
    blockchain._add_block(origin)

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))],
        [TxOut(5 * 10 ** 9, Script()), TxOut(5 * 10 ** 9, Script())],
    )
    tx = Tx(
        [TxIn(OutPoint(coinbase_0.txid, 0), Script())],
        [TxOut(10 ** 10 - 100, Script()), TxOut(50, Script())],
    )
    block_1_transactions = [coinbase_1, tx]
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root(block_1_transactions), 0
    )
    block_1 = Block(block_1_header, block_1_transactions)

    coinbase_2 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("bb"))], [TxOut(10 ** 10, Script())]
    )
    tx_2 = Tx([TxIn(OutPoint(tx.txid, 0), Script())], [TxOut(10 ** 10 - 200, Script())])
    tx_3 = Tx(
        [
            TxIn(OutPoint(coinbase_1.txid, 0), Script()),
            TxIn(OutPoint(coinbase_1.txid, 1), Script()),
            TxIn(OutPoint(tx.txid, 1), Script()),
        ],
        [TxOut(10 ** 10 + 50, Script())],
    )
    block_2_transactions = [coinbase_2, tx_2, tx_3]
    block_2_header = BlockHeader(
        block_1.header.pow, generate_merkle_root(block_2_transactions), 0
    )
    block_2 = Block(block_2_header, block_2_transactions)

    # we try adding the origin again, no problem, it is skipped
    assert blockchain.add_blocks([origin, block_1, block_2])

    coinbase_3 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("cc"))], [TxOut(10 ** 10, Script())]
    )
    # tx_4 speds the same inputs as tx_2, but it is in a different chain so it is OK
    tx_4 = Tx(
        [TxIn(OutPoint(tx.txid, 0), Script("dd"))], [TxOut(10 ** 10 - 200, Script())]
    )
    block_3_transactions = [coinbase_3, tx_4]
    block_3_header = BlockHeader(
        block_1.header.pow, generate_merkle_root(block_3_transactions), 0
    )
    block_3 = Block(block_3_header, block_3_transactions)
    block_3.header.nonce = calculate_nonce(block_3_header, 100)

    coinbase_4 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("dd"))], [TxOut(10 ** 10, Script())]
    )
    block_4_transactions = [coinbase_4]
    # invalid reference, must be block_3 header, not block_2
    block_4_header = BlockHeader(
        block_2.header.pow, generate_merkle_root(block_4_transactions), 0
    )
    block_4 = Block(block_4_header, block_4_transactions)

    assert blockchain.add_blocks([block_3, block_4])
    assert blockchain.get_last_blocks()[0][0] == block_3.header.pow

    block_4.header = BlockHeader(
        block_3.header.pow, generate_merkle_root(block_4_transactions), 0
    )
    assert blockchain.add_blocks([block_3, block_4])
    assert blockchain.get_last_blocks()[0][0] == block_4.header.pow

    reset_blockchain()


def test_flow_13():

    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )

    origin_transactions = [coinbase_0]
    origin_header = BlockHeader("00" * 32, generate_merkle_root(origin_transactions), 0)
    origin = Block(origin_header, origin_transactions)

    blockchain = Blockchain()
    blockchain._add_block(origin)
    assert blockchain.last_block_pow == origin.header.pow

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))], [TxOut(10 ** 10, Script())]
    )
    block_1_header = BlockHeader("ff" * 32, generate_merkle_root([coinbase_1]), 0)
    block_1 = Block(block_1_header, [coinbase_1])
    with pytest.raises(Exception):
        blockchain._add_block(block_1)

    reset_blockchain()


def test_flow_14():
    """
    This MUST NOT fail
    """

    blockchain = Blockchain()

    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )
    origin_header = BlockHeader("00" * 32, generate_merkle_root([coinbase_0]), 0)
    origin = Block(origin_header, [coinbase_0])

    coinbase_1 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("aa"))],
        [TxOut(5 * 10 ** 9, Script()), TxOut(5 * 10 ** 9, Script())],
    )
    block_1_header = BlockHeader(
        origin.header.pow, generate_merkle_root([coinbase_1]), 0
    )
    block_1 = Block(block_1_header, [coinbase_1])

    coinbase_2 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script("bb"))], [TxOut(10 ** 10, Script())]
    )
    block_2_header = BlockHeader(
        block_1.header.pow, generate_merkle_root([coinbase_2]), 0
    )
    block_2 = Block(block_2_header, [coinbase_2])

    # we try adding the origin again, no problem, it is skipped
    assert blockchain.add_blocks([origin, block_1, block_2])

    coinbase_3 = Tx(
        [
            TxIn(OutPoint("00" * 32, 0), Script("aa")),
            TxIn(OutPoint("00" * 32, 0), Script("bb")),
        ],
        [TxOut(10 ** 10, Script())],
    )
    block_3_header = BlockHeader(
        block_1.header.pow, generate_merkle_root([coinbase_3]), 0
    )
    block_3 = Block(block_3_header, [coinbase_3])
    assert not blockchain.add_blocks([origin, block_1, block_2, block_3])

    reset_blockchain()

from toykoin.core.pow import calculate_nonce, work_from_chain
from toykoin.core.block import BlockHeader
from toykoin.core.tx import Tx, TxIn, TxOut, OutPoint
from toykoin.core.script import Script
from toykoin.core.utils import generate_merkle_root


def test_mining():
    target = 16 ** 4
    coinbase_0 = Tx(
        [TxIn(OutPoint("00" * 32, 0), Script())], [TxOut(10 ** 10, Script())]
    )

    transactions = [coinbase_0]
    header = BlockHeader("00" * 32, generate_merkle_root(transactions), 0)

    nonce = calculate_nonce(header, target)
    header.nonce = nonce
    assert work_from_chain([header.pow]) > target

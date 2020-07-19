from toykoin.core.script import Script


def sighash_all(tx):
    for tx_in in tx.inputs:
        tx_in.unlocking_script = Script()
    return tx.txid

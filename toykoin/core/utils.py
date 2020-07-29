from btclib.utils import hash256
import shutil
import os


def generate_merkle_root(transactions):
    if len(transactions) == 0:
        return hash256(b"")
    hashes = [bytes.fromhex(transaction.txid) for transaction in transactions]
    hashes_buffer = []
    while len(hashes) != 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
        for x in range(len(hashes) // 2):
            hashes_buffer.append(hash256(hashes[2 * x] + hashes[2 * x + 1]))
        hashes = hashes_buffer[:]
        hashes_buffer = []
    return hashes[0].hex()


def reset_blockchain(name="regtest"):
    base_dir = os.path.join(os.path.expanduser("~"), ".toykoin", name)
    shutil.rmtree(base_dir)

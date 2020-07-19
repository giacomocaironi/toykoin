from toykoin.core.script import Script
from toykoin.core.sighash import sighash_all
from toykoin.core.utils import hash256

from btclib import ssa
from btclib.curvemult import mult
from btclib.secpoint import bytes_from_point


def lock_with_prvkey(prvkey):
    pubkey_hash = hash256(bytes_from_point(mult(prvkey)))
    return Script(
        [
            [0x02, 0x00, pubkey_hash],  # push pubkey_hash
            [0x03, 0x02, b"\x00"],  # hash of pub key from unlocking script
            [0xFF, 0x01, b"\x03\x02"],  # check equality
            [0xFF, 0x04, b"\xff"],  # exit if not equal
            [0xFF, 0x03, b"\x00\x01"],  # schnorr verify
            [0xFF, 0x04, b"\xff"],  # exit if not equal
        ]
    )


def unlock_with_prvkey(tx, prvkey):
    sighash = sighash_all(tx)
    sig = ssa.serialize(*ssa._sign(sighash, prvkey))
    pubkey = bytes_from_point(mult(prvkey))
    return Script([[0x00, 0x00, pubkey], [0x01, 0x00, sig]])  # push signature

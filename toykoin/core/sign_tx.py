from toykoin.core.script import (
    Script,
    OP_PUSHDATA,
    OP_EQUAL,
    OP_HASH256,
    OP_SHNORR_CHECKSIG,
    OP_VERIFY,
)
from toykoin.core.utils import hash256

from btclib import ssa
from btclib.curvemult import mult
from btclib.secpoint import bytes_from_point


def pubkey_from_prvkey(prvkey):
    pubkey = bytes_from_point(mult(prvkey))
    return pubkey.hex()


def pubkey_hash_from_prvkey(prvkey):
    pubkey = bytes_from_point(mult(prvkey))
    pubkey_hash = hash256(pubkey)
    return pubkey_hash.hex()


def lock_p2pk(pubkey):
    return Script(
        [
            [0x02, OP_PUSHDATA, bytes.fromhex(pubkey)],  # push pubkey
            [0xFF, OP_EQUAL, b"\x02\x00"],  # check equality
            [0xFF, OP_VERIFY, b"\xff"],  # exit if not equal
            [0xFF, OP_SHNORR_CHECKSIG, b"\x00\x01"],  # schnorr verify
            [0xFF, OP_VERIFY, b"\xff"],  # exit if not equal
        ]
    )


def unlock_p2pk(sighash, prvkey):
    sig = ssa.serialize(*ssa._sign(sighash, prvkey))
    pubkey = bytes_from_point(mult(prvkey))
    return Script(
        [[0x00, OP_PUSHDATA, pubkey], [0x01, OP_PUSHDATA, sig]]
    )  # push signature


def lock_p2pkh(pubkey_hash):
    return Script(
        [
            [0x02, OP_PUSHDATA, bytes.fromhex(pubkey_hash)],  # push pubkey_hash
            [0x03, OP_HASH256, b"\x00"],  # hash of pub key from unlocking script
            [0xFF, OP_EQUAL, b"\x03\x02"],  # check equality
            [0xFF, OP_VERIFY, b"\xff"],  # exit if not equal
            [0xFF, OP_SHNORR_CHECKSIG, b"\x00\x01"],  # schnorr verify
            [0xFF, OP_VERIFY, b"\xff"],  # exit if not equal
        ]
    )


def unlock_p2pkh(sighash, prvkey):
    sig = ssa.serialize(*ssa._sign(sighash, prvkey))
    pubkey = bytes_from_point(mult(prvkey))
    return Script(
        [[0x00, OP_PUSHDATA, pubkey], [0x01, OP_PUSHDATA, sig]]
    )  # push signature

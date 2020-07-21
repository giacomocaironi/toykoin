from toykoin.core.script import Script
from toykoin.core.utils import hash256

from btclib import ssa
from btclib.curvemult import mult
from btclib.secpoint import bytes_from_point


def test_serialization():
    assert Script() == Script.from_hex("")
    assert Script.from_hex(Script().hex) == Script()


def test_valid_schnorr():
    sighash = bytes.fromhex("00" * 32)
    false_sighash = bytes.fromhex("aa" * 32)
    sig = ssa.serialize(*ssa._sign(sighash, 1))
    pubkey = bytes_from_point(mult(1))
    pubkey_hash = hash256(pubkey)
    script = Script(
        [
            [0x00, 0x00, pubkey],
            [0x01, 0x00, sig],
            [0x02, 0x00, pubkey_hash],  # push pubkey_hash
            [0x03, 0x02, b"\x00"],  # hash of pub key from unlocking script
            [0xFF, 0x01, b"\x03\x02"],  # check equality
            [0xFF, 0x04, b"\xff"],  # exit if not equal
            [0xFF, 0x03, b"\x00\x01"],  # schnorr verify
            [0xFF, 0x04, b"\xff"],
        ]  # exit if not equal])  # push signature
    )
    assert not script.execute(memory={0x100: false_sighash})


def test_invalid_schnorr():
    sighash = bytes.fromhex("00" * 32)
    sig = ssa.serialize(*ssa._sign(sighash, 1))
    pubkey = bytes_from_point(mult(1))
    pubkey_hash = hash256(pubkey)
    script = Script(
        [
            [0x00, 0x00, pubkey],
            [0x01, 0x00, sig],
            [0x02, 0x00, pubkey_hash],  # push pubkey_hash
            [0x03, 0x02, b"\x00"],  # hash of pub key from unlocking script
            [0xFF, 0x01, b"\x03\x02"],  # check equality
            [0xFF, 0x04, b"\xff"],  # exit if not equal
            [0xFF, 0x03, b"\x00\x01"],  # schnorr verify
            [0xFF, 0x04, b"\xff"],
        ]  # exit if not equal])  # push signature
    )
    assert script.execute(memory={0x100: sighash})

from toykoin.core.script import Script
from toykoin.core.sign_tx import (
    lock_p2pk,
    unlock_p2pk,
    lock_p2pkh,
    unlock_p2pkh,
    pubkey_from_prvkey,
    pubkey_hash_from_prvkey,
)


def test_serialization():
    assert Script() == Script.from_hex("")
    assert Script.from_hex(Script().hex) == Script()


def test_valid_schnorr():
    sighash = bytes.fromhex("00" * 32)
    script = unlock_p2pkh(sighash, 1) + lock_p2pkh(pubkey_hash_from_prvkey(1))
    assert script.execute(memory={0x100: sighash})


def test_invalid_schnorr():
    sighash = bytes.fromhex("00" * 32)
    false_sighash = bytes.fromhex("aa" * 32)
    script = unlock_p2pk(sighash, 1) + lock_p2pk(pubkey_from_prvkey(1))
    assert not script.execute(memory={0x100: false_sighash})

from toykoin.daemon.connection import _verify_headers, add_headers

import pytest


def test_headers():
    _verify_headers(add_headers("version", b""))
    _verify_headers(add_headers("version", b"\x01"))
    _verify_headers(add_headers("a" * 12, b"\x01"))
    with pytest.raises(Exception, match="Wrong payload length"):
        _verify_headers(add_headers("a" * 13, b"\x01"))


def test_invalid_headers():
    err_msg = "Wrong checksum, the message might have been tampered"
    with pytest.raises(Exception, match=err_msg):
        _verify_headers(b"\x00" * 20)


def test_invalid_length():
    err_msg = "Wrong payload length"
    with pytest.raises(Exception, match=err_msg):
        _verify_headers(add_headers("a", b"") + b"\x01")

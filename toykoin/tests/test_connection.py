from toykoin.daemon.connection import _verify_headers, add_headers

import pytest


def test_headers():
    _verify_headers(add_headers("version", b""))
    _verify_headers(add_headers("version", b"\x01"))
    _verify_headers(add_headers("a" * 12, b"\x01"))
    with pytest.raises(Exception, match="Wrong payload length"):
        _verify_headers(add_headers("a" * 13, b"\x01"))

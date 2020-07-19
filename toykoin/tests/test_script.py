from toykoin.core.script import Script


def test_serialization():
    assert Script() == Script.from_hex("")
    assert Script.from_hex(Script().hex) == Script()

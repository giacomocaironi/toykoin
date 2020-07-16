from toykoin.core.utils import generate_merkle_root


def test_merkle_root():
    assert generate_merkle_root([])

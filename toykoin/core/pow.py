from copy import copy


def calculate_nonce(header, target):
    header = copy(header)
    while True:
        header.nonce += 1
        pow = 2 ** 256 / int(header.pow, 16)
        if pow > target:
            return header.nonce


def work_from_chain(chain):
    pow = 0
    for block in chain:
        pow += 2 ** 256 / int(block, 16)
    return pow

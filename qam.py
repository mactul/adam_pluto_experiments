import math

QBSK_TABLE = [1+0j, 1j, -1j, -1 + 0j]

def symb_to_qpsk(symb: int) -> complex:
    if symb < 0b00 or symb > 0b11:
        raise ValueError("Symbols should be between 0b00 and 0b11")
    return QBSK_TABLE[symb]

def closest_symb(qpsk: complex):
    qpsk = qpsk / abs(qpsk)
    index = 0
    min_diff = abs(qpsk - QBSK_TABLE[0])
    for i in range(1, len(QBSK_TABLE)):
        diff = abs(qpsk - QBSK_TABLE[i])
        if diff < min_diff:
            min_diff = diff
            index = i
    return index

import math

SQRT2_4 = math.sqrt(2) / 4

QAM8_TABLE = [1+0j, SQRT2_4+SQRT2_4*1j, -SQRT2_4 + SQRT2_4 * 1j, 1j, SQRT2_4 - SQRT2_4 * 1j, -1j, -1 + 0j, -SQRT2_4 - SQRT2_4 * 1j]

def symb_to_qam8(symb: int) -> complex:
    if symb < 0b000 or symb > 0b111:
        raise ValueError("Symbole should be between 0b000 and 0b111")
    return QAM8_TABLE[symb]

def closest_symb(qam8: complex):
    index = 0
    min_diff = abs(qam8 - QAM8_TABLE[0])
    for i in range(1, len(QAM8_TABLE)):
        diff = abs(qam8 - QAM8_TABLE[i])
        if diff < min_diff:
            min_diff = diff
            index = i
    return index

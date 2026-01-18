from numpy import diff


def message_to_symbols(data: bytes) -> list[int]:
    num = int.from_bytes(data, byteorder='big')
    
    if num == 0:
        return [0b00, 0b01]
    
    digits = []
    while num > 0:
        digits.append(1 + num % 3)
        num //= 3
    digits.append(0b00)
    
    return digits[::-1]  # Reverse to get most significant digit first


def symbols_to_messages(digits: list[int]) -> list(bytes):
    i = 0
    while i < len(digits) and digits[i] != 0b00:
        i += 1
    messages = []
    while i < len(digits):
        while i < len(digits) and digits[i] == 0b00:
            i += 1
        num = 0
        while i < len(digits) and digits[i] != 0b00:
            num = num * 3 + digits[i] - 1
            i += 1
        
        if num == 0:
            messages.append('\x00')
        
        byte_length = (num.bit_length() + 7) // 8
        messages.append(num.to_bytes(byte_length, byteorder='big'))
    return messages


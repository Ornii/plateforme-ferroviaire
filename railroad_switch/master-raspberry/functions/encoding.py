from functions.state import Function


def packet_encode_with_get_function(function: Function) -> int:
    byte = 0
    byte = byte | (function.value << 1)
    return byte

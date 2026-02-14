from functions.encoding import packet_encode_with_get_function
from functions.state import Function


def packet_encode_get_hall() -> int:
    return packet_encode_with_get_function(Function.GET_HALL_SENSORS)

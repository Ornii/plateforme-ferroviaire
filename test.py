# different position in rail switch
MAIN_TRACK = "main_track"
STRAIGHT_TRACK = "straight_track"
DIVERGING_TRACK = "diverging_track"
RAIL_SWITCH = "rail_switch"  # in the center of rail switch, temporary position

# main positions
MAIN_POSITIONS = [MAIN_TRACK, STRAIGHT_TRACK, DIVERGING_TRACK]
MAIN_POSITIONS_ENCODING = {
    MAIN_TRACK: 0b0,
    STRAIGHT_TRACK: 0b1,
    DIVERGING_TRACK: 0b10,
}
# color of traffic lights

GREEN = "green"
RED = "red"
YELLOW = "yellow"

LIGHT_SWITCH_STATES = [GREEN, RED, YELLOW]
LIGHT_SWITCH_STATES_ENCODING = {GREEN: 0b11, RED: 0b0, YELLOW: 0b10}

# state of the rail switch: 2 modes
RAIL_SWITCH_STATES = [STRAIGHT_TRACK, DIVERGING_TRACK]
RAIL_SWITCH_STATES_ENCODING = {STRAIGHT_TRACK: 0b1, DIVERGING_TRACK: 0b0}

RAIL_SWITCH_STATES_DECODING = {}
for emplacement, code in RAIL_SWITCH_STATES_ENCODING.items():
    RAIL_SWITCH_STATES_DECODING[code] = emplacement


# functions set: order of an action
SET_LED = "set_led"
SET_RAIL_SWITCH = "set_rail_switch"

# functions get: order of getting state
GET_HALL = "get_hall"
GET_RAIL_SWITCH = "get_rail_switch"

# function which are sent by the raspberry
FUNCTIONS_SENT = [SET_LED, SET_RAIL_SWITCH, GET_HALL, GET_RAIL_SWITCH]
FUNCTIONS_SENT_ENCODING = {
    SET_LED: 0b0,
    SET_RAIL_SWITCH: 0b1,
    GET_HALL: 0b10,
    GET_RAIL_SWITCH: 0b11,
}

FUNCTIONS_SENT_DECODING = {}
for function, code in FUNCTIONS_SENT_ENCODING.items():
    FUNCTIONS_SENT_DECODING[code] = function

# variable which describes current state
rail_switch = ""  # unknown
halls_state = {
    MAIN_TRACK: 0b0,
    STRAIGHT_TRACK: 0b0,
    DIVERGING_TRACK: 0b0,
}  # all are false by default


def packet_encode_set_led(train_position: str, light_switch_state: str) -> int:
    byte = 0
    byte = byte | (MAIN_POSITIONS_ENCODING[train_position] << 5)
    byte = byte | (LIGHT_SWITCH_STATES_ENCODING[light_switch_state] << 3)
    byte = byte | (FUNCTIONS_SENT_ENCODING[SET_LED] << 1)
    return byte


def packet_encode_set_rail_switch(rail_switch_state: str) -> int:
    byte = 0
    byte = byte | (RAIL_SWITCH_STATES_ENCODING[rail_switch_state] << 3)
    byte = byte | (FUNCTIONS_SENT_ENCODING[SET_RAIL_SWITCH] << 1)
    return byte


def packet_encode_get_rail_switch() -> int:
    byte = 0
    byte = byte | (FUNCTIONS_SENT_ENCODING[GET_RAIL_SWITCH] << 1)
    return byte


def packet_encode_get_hall() -> int:
    byte = 0
    byte = byte | (FUNCTIONS_SENT_ENCODING[GET_HALL] << 1)
    return byte


def packet_decode(
    packet: int, rail_switch: str, halls_state: dict[str, int]
) -> tuple[str, dict[str, int]]:
    function = FUNCTIONS_SENT_DECODING[packet >> 1 & 0b11]
    if function == SET_RAIL_SWITCH:
        rail_switch = RAIL_SWITCH_STATES_DECODING[packet >> 3 & 0b1]
    elif function == GET_HALL:
        halls_state = {
            MAIN_TRACK: packet >> 5 & 0b1,
            STRAIGHT_TRACK: packet >> 4 & 0b1,
            DIVERGING_TRACK: packet >> 3 & 0b1,
        }
    else:
        raise ValueError("Wrong packet received")
    return rail_switch, halls_state


print(packet_decode(0b00110100, rail_switch, halls_state))

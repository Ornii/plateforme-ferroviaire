import time

from smbus2 import SMBus

"""Connection I2C"""
addr = 0x08

bus = SMBus(1)

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


def emplacement_turn_red(train_position: str) -> None:
    for emplacement in MAIN_POSITIONS:
        if emplacement != train_position:
            packet = packet_encode_set_led(emplacement, RED)
            time.sleep(0.5)
            bus.write_byte(addr, packet)


# SNCF requirement: all lights are green at the beginning/in the end
for emplacement in MAIN_POSITIONS:
    packet = packet_encode_set_led(emplacement, GREEN)
    time.sleep(0.5)
    bus.write_byte(addr, packet)

# Objective

OBJECTIVE = [MAIN_TRACK, STRAIGHT_TRACK]
#OBJECTIVE = [MAIN_TRACK, DIVERGING_TRACK]

train_position = OBJECTIVE[0]
# need to verify if objective is correct


# Init
emplacement_turn_red(train_position)
bus.write_byte(addr, packet_encode_get_rail_switch())
time.sleep(0.5)
packet = bus.read_byte(addr)

rail_switch, halls_state = packet_decode(packet, rail_switch, halls_state)
print("leds init finished", rail_switch, halls_state)

if train_position == MAIN_TRACK:
    if OBJECTIVE[1] == STRAIGHT_TRACK and rail_switch != STRAIGHT_TRACK:
        bus.write_byte(addr, packet_encode_set_rail_switch(STRAIGHT_TRACK))
        time.sleep(3)
    elif OBJECTIVE[1] == DIVERGING_TRACK and rail_switch != DIVERGING_TRACK:
        bus.write_byte(addr, packet_encode_set_rail_switch(DIVERGING_TRACK))

elif train_position == STRAIGHT_TRACK:
    if OBJECTIVE[1] == MAIN_TRACK and rail_switch != STRAIGHT_TRACK:
        bus.write_byte(addr, packet_encode_set_rail_switch(STRAIGHT_TRACK))

elif train_position == DIVERGING_TRACK:
    if OBJECTIVE[1] == MAIN_TRACK and rail_switch != DIVERGING_TRACK:
        bus.write_byte(addr, packet_encode_set_rail_switch(DIVERGING_TRACK))

rail_switch = OBJECTIVE[1]
print("rail_switch init finished")

while True:
    time.sleep(1)  # in order to not spam slave
    bus.write_byte(addr, packet_encode_get_hall())
    time.sleep(0.5)
    packet = bus.read_byte(addr)
    print(bin(packet))
    rail_switch, halls_state = packet_decode(packet, rail_switch, halls_state)
    print(rail_switch, halls_state)
    # if train is not first detected by its first position raise error
    if halls_state[OBJECTIVE[0]] == 0:
        for emplacement, state in halls_state.items():
            if emplacement != OBJECTIVE[0] and state == 1:
                raise SystemError("Wrong position of train")
    # if train passed trhough the first objective then its position is in the center of rail switch
    elif halls_state[OBJECTIVE[0]] == 1 and train_position == OBJECTIVE[0]:
        train_position = RAIL_SWITCH
    # if the train is in the center of rail switch
    elif halls_state[OBJECTIVE[0]] == 1 and train_position == RAIL_SWITCH:
        for emplacement, state in halls_state.items():
            # if the train goes in the wrong way then raise error
            if (
                emplacement != OBJECTIVE[1]
                and emplacement != OBJECTIVE[0]
                and state == 1
            ):
                raise SystemError("Wrong position of train")

            # if the train is detected in the the direction it shall goes then finish
            elif emplacement == OBJECTIVE[1] and halls_state[emplacement] == 1:
                train_position = OBJECTIVE[1]
                for emplacement in MAIN_POSITIONS:
                    packet = packet_encode_set_led(emplacement, GREEN)
                    bus.write_byte(addr, packet)
                print("Train arrived")
                time.sleep(10)
                quit()

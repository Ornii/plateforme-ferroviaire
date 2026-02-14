from blade_switch.state import BladeSwitchPosition


class BladeSwitch:
    def __init__(self, init_position: BladeSwitchPosition):
        self.position: BladeSwitchPosition = init_position

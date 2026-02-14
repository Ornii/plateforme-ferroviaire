from positions.state import Position


class Train:
    def __init__(
        self,
        init_position: Position,
        objective_position: Position,
    ):
        self.position = init_position
        self.init_position = init_position
        self.objective_position = objective_position
        self.is_in_railroad_switch: bool = False

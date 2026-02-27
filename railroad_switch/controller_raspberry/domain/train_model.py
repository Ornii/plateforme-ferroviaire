from protocol.railroad_protocol import TrackPosition


class TrainState:
    def __init__(
        self,
        init_position: TrackPosition,
        objective_position: TrackPosition,
    ):
        self.position = init_position
        self.init_position = init_position
        self.objective_position = objective_position
        self.is_in_railroad_switch: bool = False

from domain.packet_protocol import Position


class TrainState:
    def __init__(
        self,
        init_position: Position,
        objective_position: Position,
    ) -> None:
        self.position = init_position
        self.init_position = init_position
        self.objective_position = objective_position

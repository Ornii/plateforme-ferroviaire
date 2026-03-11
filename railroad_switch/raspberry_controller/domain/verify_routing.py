from domain.packet_protocol import Position
from domain.train_state import TrainState


def is_routing_right(train: TrainState) -> bool:
    return not (
        (
            train.init_position == Position.REVERSE
            and (
                train.objective_position == Position.REVERSE
                or train.objective_position == Position.NORMAL
            )
        )
        or (
            train.init_position == Position.NORMAL
            and (
                train.objective_position == Position.NORMAL
                or train.objective_position == Position.REVERSE
            )
        )
        or (
            train.init_position == Position.LEAD
            and train.objective_position == Position.LEAD
        )
    )

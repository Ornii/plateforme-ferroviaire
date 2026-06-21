from domain.packet_protocol import Position
from domain.train_state import Train


def is_routing_right(train: Train) -> bool:
    return (
        (
            train.init_position == Position.ID_1
            and (
                train.objective_position == Position.ID_2
                or train.objective_position == Position.ID_3
            )
        )
        or (
            train.init_position == Position.ID_2
            and (
                train.objective_position == Position.ID_1
                or train.objective_position == Position.ID_4
            )
        )
        or (
            train.init_position == Position.ID_3
            and (
                train.objective_position == Position.ID_1
                or train.objective_position == Position.ID_4
            )
        )
        or (
            train.init_position == Position.ID_4
            and (
                train.objective_position == Position.ID_2
                or train.objective_position == Position.ID_3
            )
        )
    )

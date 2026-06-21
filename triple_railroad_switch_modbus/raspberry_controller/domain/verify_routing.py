from domain.packet_protocol import Position
from domain.train_state import Train


def is_routing_right(train: Train) -> bool:
    return (
        (
            train.init_position == Position.GAUCHE
            and (train.objective_position == Position.TALON)
        )
        or (
            train.init_position == Position.DROITE
            and (train.objective_position == Position.TALON)
        )
        or (
            train.init_position == Position.DIRECT
            and (train.objective_position == Position.TALON)
        )
        or (
            train.init_position == Position.TALON
            and (
                train.objective_position == Position.DIRECT
                or train.objective_position == Position.GAUCHE
                or train.objective_position == Position.DROITE
            )
        )
    )

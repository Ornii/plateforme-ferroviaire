from domain.packet_protocol import TrackPosition
from domain.train_state import TrainState


def is_routing_right(train: TrainState) -> bool:
    return not (
        (
            train.init_position == TrackPosition.DIVERGING_TRACK
            and (
                train.objective_position == TrackPosition.DIVERGING_TRACK
                or train.objective_position == TrackPosition.STRAIGHT_TRACK
            )
        )
        or (
            train.init_position == TrackPosition.STRAIGHT_TRACK
            and (
                train.objective_position == TrackPosition.STRAIGHT_TRACK
                or train.objective_position == TrackPosition.DIVERGING_TRACK
            )
        )
        or (
            train.init_position == TrackPosition.MAIN_TRACK
            and train.objective_position == TrackPosition.MAIN_TRACK
        )
    )

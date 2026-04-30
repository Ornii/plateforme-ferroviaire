from __future__ import annotations

from json import load
from pathlib import Path
from typing import Any, TypedDict

from real_circuit.create_circuit import Circuit, Structure

BASE_DIR = str(Path(__file__).parent.resolve())


class DictTrain(TypedDict):
    id: str
    init_position: str
    objective_position: str
    starting_time: int


def load_json_file(filename: str) -> Any:
    with open(BASE_DIR + "/" + str(filename), "r", encoding="utf-8") as json_file:
        data_as_dict = load(json_file)
    return data_as_dict


class Trains:
    def __init__(self) -> None:
        self.list_trains: list[Train] = []
        self.train_by_id: dict[str, Train] = {}

    def add_train(self, train: Train):
        self.list_trains.append(train)
        self.train_by_id[train.id] = train

    def are_arrived(self) -> bool:
        for train in self.list_trains:
            if train.position != train.objective_position:
                return False
        return True


class Train:
    def __init__(
        self,
        id: str,
        starting_position: Structure,
        objective_position: Structure,
        starting_time: int,
    ) -> None:
        self.id = id
        self.starting_position = starting_position
        self.objective_position = objective_position
        self.starting_time = starting_time
        self.position = starting_position


def create_train(circuit: Circuit, trains: Trains, dict_train: DictTrain):
    init_structure = circuit.find_structure(dict_train["init_position"])
    end_structure = circuit.find_structure(dict_train["objective_position"])
    assert init_structure is not None
    assert end_structure is not None
    train = Train(
        dict_train["id"],
        init_structure,
        end_structure,
        dict_train["starting_time"],
    )
    trains.add_train(train)


def create_trains(circuit: Circuit, train_filename: str):
    list_trains: list[DictTrain] = load_json_file(train_filename)
    trains = Trains()
    for dict_train in list_trains:
        create_train(circuit, trains, dict_train)


def route_train_naive(circuit: Circuit, trains: Trains):
    while not trains.are_arrived():
        train_to_go =

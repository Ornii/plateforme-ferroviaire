from __future__ import annotations

import threading
import time
from json import load
from pathlib import Path
from typing import Any, TypedDict

from trains.dijkstra import dijsktra

from real_circuit.circuit.create_circuit import (
    Circuit,
    Structure,
)

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

    def all_are_arrived(self) -> bool:
        for train in self.list_trains:
            if train.position != train.objective_position:
                return False
        return True

    def all_are_trying_to_leave(self) -> bool:
        for train in self.list_trains:
            if not train.is_trying_to_leave:
                return False
        return True

    def select_train_to_leave(self, current_time: float) -> Train | None:
        train_with_minimal_leaving_time = None
        minimal_leaving_time = 0
        for train in self.list_trains:
            if (
                not train.is_trying_to_leave
                and train.starting_time < minimal_leaving_time
            ):
                minimal_leaving_time = train.starting_time
                train_with_minimal_leaving_time = train

        return train_with_minimal_leaving_time


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
        self.is_trying_to_leave: bool = False

    def avance(self):
        pass

    def go_to_path(self, path: list[tuple[Structure, str]]):
        """init"""
        current_structure = path[0][0]
        next_structures = path.copy()
        next_structures.pop(0)
        next_structure = next_structures[0][0]
        current_structure.prepare_of_arrival(next_structure)
        next_next_structure = next_structures[1][0]
        next_structure.prepare_of_arrival(next_next_structure)
        self.avance()
        """loop"""
        while self.position != self.objective_position:
            if detect_train(next_structure, next_next_structure):
                current_structure.set_occupation(False)
                current_structure = next_structure
                next_structures.pop(0)

                self.position = current_structure
                current_structure.set_occupation(True)

                next_structure = next_structures[0][0]
                next_next_structure = next_structures[1][0]
                next_structure.prepare_of_arrival(next_next_structure)

    def calculate_path(self, circuit: Circuit) -> list[tuple[Structure, str]]:
        path = dijsktra(circuit, self.starting_position, self.objective_position)
        return path


def detect_train(next_structure, next_next_structure):
    pass


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


def reserve_structures(path: list[tuple[Structure, str]]):
    for structure, _ in path:
        structure.set_reservation(True)


def route_train_naive(circuit: Circuit, trains: Trains):
    t_init = time.time()
    while not trains.all_are_trying_to_leave():
        t_current = time.time() - t_init
        train_to_go = trains.select_train_to_leave(t_current)

        if train_to_go is None:  # threading relative issues
            continue
        else:
            assert train_to_go is not None

        path = train_to_go.calculate_path(circuit)
        reserve_structures(path)

        threading.Thread(
            target=train_to_go.go_to_path(path),
            daemon=True,
            name=f"{train_to_go.id} to {train_to_go.objective_position.id}",
        ).start()

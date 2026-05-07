from __future__ import annotations


class Train:
    def __init__(self, init_position: Canton, id: float) -> None:
        self.position = init_position
        self.id = id


def build_trains(list_trains: list[Train]):
    trains = {}
    for train in trains:
        trains[train.id] = train
    return trains


class Canton:
    def __init__(self, id: int) -> None:
        self.id = id
        self.is_occupied = False
        self.successors = []
        self.predecessors = []

    def __str__(self) -> str:
        return f"id: {self.id}, is_occupied: {self.is_occupied}"


def add_successors_prodecessors(canton: Canton, successor: Canton):
    canton.successors.append(successor)
    successor.predecessors.append(canton)


def create_cantons(circuit: Circuit, adjacency_matrix: list[tuple[int, list[int]]]):
    for canton_id, _ in adjacency_matrix:
        canton = Canton(canton_id)
        circuit.cantons[canton_id] = canton
    for canton_id, successors_id in adjacency_matrix:
        for canton_successor_id in successors_id:
            add_successors_prodecessors(
                circuit.cantons[canton_id], circuit.cantons[canton_successor_id]
            )


class Circuit:
    def __init__(self, adjacency_matrix: list[tuple[int, list[int]]]) -> None:
        self.cantons = {}
        self.init_adjacency_matrix = adjacency_matrix

    def add_trains(self, trains: dict[float, Train]):
        self.trains = trains
        for train in trains.values():
            self.cantons[train.position.id].is_occupied = True

    def create_adjacency_matrix(self):
        current_adjacency_matrix = self.init_adjacency_matrix.copy()
        for train in self.trains.values():
            for i in range(len(current_adjacency_matrix)):
                if train.position.id in current_adjacency_matrix[i][1]:
                    current_adjacency_matrix[i][1].remove(train.position.id)
        return current_adjacency_matrix

    def route(self, route_objectives: list[tuple[Train, Canton]]):
        # G = self.create_adjacency_matrix()
        for train, objective_canton in route_objectives:
            pass


G = [
    (1, [2]),
    (2, [3, 5]),
    (3, [4]),
    (4, [1]),
    (5, [7]),
    (6, [4]),
    (7, [8, 9]),
    (8, [6]),
    (9, [8]),
]

circuit = Circuit(G)
print(circuit.cantons[1].predecessors[0])

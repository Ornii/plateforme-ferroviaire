from real_circuit.circuit.create_circuit import (
    Aiguillage,
    AiguillageTriple,
    Canton,
    Circuit,
    CroisementAvecAiguille,
    Structure,
    Terminal,
    create_circuit,
)


def find_shortest_id(distance_by_id: dict[str, float], chosen_ids: list[str]) -> str:
    best_id = chosen_ids[0]
    best_distance = distance_by_id[best_id]
    for id in chosen_ids:
        if distance_by_id[id] < best_distance:
            best_distance = distance_by_id[id]
            best_id = id
    return best_id


def dijsktra(circuit: Circuit, start: Structure, end: Structure):
    assert not start.is_reserved
    ids = list(circuit.structure_by_id.keys())
    predecessor = {}
    distance_with_predecessor = {}
    ids_available_not_visited = []
    for id in ids:
        structure = circuit.find_structure(id)
        assert structure is not None
        if not structure.is_reserved:
            ids_available_not_visited.append(id)
            predecessor[id] = None
            distance_with_predecessor[id] = float("inf")

    predecessor[start.id] = start.id
    distance_with_predecessor[start.id] = 0.0
    shortest_id = find_shortest_id(distance_with_predecessor, ids_available_not_visited)
    while shortest_id != end.id:
        shortest_id = find_shortest_id(
            distance_with_predecessor, ids_available_not_visited
        )
        ids_available_not_visited.remove(shortest_id)
        structure = circuit.find_structure(shortest_id)
        assert structure is not None
        for next_structure in structure.next_structures:
            if (
                distance_with_predecessor[next_structure[0].id]
                > distance_with_predecessor[shortest_id] + 1
            ):
                predecessor[next_structure[0].id] = shortest_id
                distance_with_predecessor[next_structure[0].id] = (
                    distance_with_predecessor[shortest_id] + 1
                )
    result = []
    id = end.id
    result.append(id)
    while id != start.id:
        id = predecessor[id]
        result.append(id)
    return result[::-1]


if __name__ == "__main__":
    circuit = create_circuit("circuit.json", "id.json", "route.json")
    print(dijsktra(circuit, circuit.find_structure("C1"), circuit.find_structure("T4")))

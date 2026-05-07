from real_circuit.circuit.create_circuit import (
    Circuit,
    Structure,
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


def dijsktra(
    circuit: Circuit, start: Structure, end: Structure
) -> list[tuple[Structure, str]]:
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
    result_id = []
    id = end.id
    result_id.append(id)
    while id != start.id:
        id = predecessor[id]
        result_id.append(id)
    result_id = result_id[::-1]
    result = get_real_path_with_ids(circuit, result_id)
    return result


def get_real_path_with_ids(
    circuit: Circuit, path_ids: list[str]
) -> list[tuple[Structure, str]]:
    result = []
    for i in range(len(path_ids) - 1):
        current_structure_id = path_ids[i]
        current_structure = circuit.find_structure(current_structure_id)
        next_structure_id = path_ids[i + 1]
        next_structure = circuit.find_structure(next_structure_id)
        for successor_structure, entry_id, exit_id in current_structure.next_structures:
            if successor_structure == next_structure:
                result.append((current_structure, entry_id))
                result.append((next_structure, exit_id))
    return result


if __name__ == "__main__":
    circuit = create_circuit("circuit.json", "id.json", "route.json")
    path = dijsktra(circuit, circuit.find_structure("C1"), circuit.find_structure("T4"))
    readable_path = []
    for structure, position_id in path:
        readable_path.append((structure.id, position_id))
    print(readable_path)

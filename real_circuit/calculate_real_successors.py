import json
from pathlib import Path

import networkx as nx

BASE_DIR = str(Path(__file__).parent.resolve())

"""Extract data from ``circuit.json`` once at module import."""
with open(rf"{BASE_DIR}\circuit.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

structures: list[dict[str, str | list[dict[str, str]]]] = data["structures"]
type_by_graph_type: dict[str, list[str]] = data["graphe type"]
entrance_exit_by_type: dict[str, list[dict[str, list[str]]]] = data["route"]
uturn_nodes: list[str] = data["u-turn"]


def map_successors(node_ids, node_props_by_id):
    """Build the successor list for every graph node.

    Args:
        node_ids: List of graph node identifiers (example: ``"N1,h"``).
        node_props_by_id: Mapping of node identifier to useful properties.

    Returns:
        A dictionary where keys are node identifiers and values are lists
        of successor node identifiers.
    """
    successors_by_node = {}
    for node_id in node_ids:
        successors_by_node[node_id] = []
        structure_id = node_props_by_id[node_id]["id"]
        direction = node_props_by_id[node_id]["sens"]
        add_successor(node_id, structure_id, direction, successors_by_node)

    return successors_by_node


def handle_node_successors(node_id, structure, direction, successors_by_node):
    """Resolve successors when the current structure is a graph node.

    Args:
        node_id: Current graph node identifier.
        structure: Current structure definition from ``circuit.json``.
        direction: Traversal direction (``"horaire"`` or ``"trigo"``).
        successors_by_node: Mutable mapping to fill with successors.
    """
    successor_structures = structure["successeurs"]
    for next_structure in successor_structures:
        type_next_structure = next_structure["type"]
        id_next_structure = next_structure["id"]
        if next_structure["sens"] != direction:
            continue

        if type_next_structure in type_by_graph_type["node"]:
            successors_by_node[node_id].append(id_next_structure + "," + direction[0])
            continue

        # The successor is an edge connector: continue traversal recursively.
        new_entrance_position = next_structure["successeur_position_entree"]
        add_successor(
            node_id,
            id_next_structure,
            direction,
            successors_by_node,
            new_entrance_position,
        )


def handle_edge_connectors(
    node_id, structure, direction, successors_by_node, entrance_position
):
    """Resolve successors when traversing an edge connector.

    Args:
        node_id: Current graph node identifier.
        structure: Current connector structure from ``circuit.json``.
        direction: Traversal direction (``"horaire"`` or ``"trigo"``).
        successors_by_node: Mutable mapping to fill with successors.
        entrance_position: Connector entrance position used to compute exits.
    """
    type_structure = structure["type"]
    exit_positions = []
    for exit_by_entrance in entrance_exit_by_type[type_structure]:
        if exit_by_entrance["position_entree"] == entrance_position:
            exit_positions = exit_by_entrance["positions_sortie"].copy()
            break

    successor_structures = structure["successeurs"]
    for next_structure in successor_structures:
        if next_structure["sens"] != direction:
            continue
        if next_structure["position_sortie"] not in exit_positions:
            continue

        type_next_structure = next_structure["type"]
        id_next_structure = next_structure["id"]
        if type_next_structure in type_by_graph_type["node"]:
            successors_by_node[node_id].append(id_next_structure + "," + direction[0])
            continue

        new_entrance_position = next_structure["successeur_position_entree"]
        add_successor(
            node_id,
            id_next_structure,
            direction,
            successors_by_node,
            new_entrance_position,
        )


def handle_uturn_node(node_id, structure, direction, successors_by_node):
    """Add U-turn successor if the current structure is configured as U-turn.

    Args:
        node_id: Current graph node identifier.
        structure: Current structure from ``circuit.json``.
        direction: Traversal direction (``"horaire"`` or ``"trigo"``).
        successors_by_node: Mutable mapping to fill with successors.
    """
    structure_id = structure["id"]
    if structure_id not in uturn_nodes:
        return

    reverse_direction = "trigo" if direction == "horaire" else "horaire"
    successors_by_node[node_id].append(structure_id + "," + reverse_direction[0])


def add_successor(
    node_id,
    structure_id,
    direction,
    successors_by_node,
    entrance_position=None,
) -> None:
    """Find a structure by ID and dispatch successor computation.

    Args:
        node_id: Current graph node identifier.
        structure_id: ID of the structure to inspect.
        direction: Traversal direction.
        successors_by_node: Mutable mapping to fill with successors.
        entrance_position: Entrance position when current structure is a connector.
    """
    for structure in structures:
        if structure["id"] != structure_id:
            continue

        if entrance_position is None:
            handle_node_successors(node_id, structure, direction, successors_by_node)
            handle_uturn_node(node_id, structure, direction, successors_by_node)
        else:
            handle_edge_connectors(
                node_id, structure, direction, successors_by_node, entrance_position
            )
        break


def create_node_ids_and_props():
    """Create node identifiers and associated properties.

    Returns:
        A tuple ``(node_ids, node_props_by_id)`` where:
            - ``node_ids`` is a list of unique graph node identifiers.
            - ``node_props_by_id`` maps each identifier to structure ID and direction.
    """
    node_ids = []
    node_props_by_id = {}
    for structure in structures:
        current_id = structure["id"]
        current_type = structure["type"]
        if current_type not in type_by_graph_type["node"]:
            continue

        for successor_structure in structure["successeurs"]:
            current_direction = successor_structure["sens"]
            node_id = current_id + "," + current_direction[0]
            if node_id in node_ids:
                continue
            node_ids.append(node_id)
            node_props_by_id[node_id] = {"id": current_id, "sens": current_direction}

    for structure in structures:
        for successor_structure in structure["successeurs"]:
            current_direction = successor_structure["sens"]
            successor_id = successor_structure["id"]
            successor_type = successor_structure["type"]
            if successor_type not in type_by_graph_type["node"]:
                continue

            node_id = successor_id + "," + current_direction[0]
            if node_id in node_ids:
                continue
            node_ids.append(node_id)
            node_props_by_id[node_id] = {
                "id": successor_id,
                "sens": current_direction,
            }

    for uturn_node_id in uturn_nodes:
        trigo_node_id = uturn_node_id + ",t"
        horaire_node_id = uturn_node_id + ",h"
        if trigo_node_id not in node_ids:
            node_ids.append(trigo_node_id)
            node_props_by_id[trigo_node_id] = {"id": uturn_node_id, "sens": "trigo"}
        if horaire_node_id not in node_ids:
            node_ids.append(horaire_node_id)
            node_props_by_id[horaire_node_id] = {
                "id": uturn_node_id,
                "sens": "horaire",
            }
    return node_ids, node_props_by_id


if __name__ == "__main__":
    node_ids, node_props_by_id = create_node_ids_and_props()
    successors_by_node = map_successors(node_ids, node_props_by_id)
    graph = nx.DiGraph(successors_by_node)
    nx.write_gexf(graph, rf"{BASE_DIR}\graph.gexf")
    print("test")

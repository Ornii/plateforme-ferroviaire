import json
from pathlib import Path

import networkx as nx

BASE_DIR = str(Path(__file__).parent.resolve())

"""Extracting data from circuit.json"""
json_file = open(rf"{BASE_DIR}\circuit.json", "r")
data = json.load(json_file)
json_file.close()

structures: list[dict[str, str | list[dict[str, str]]]] = data["structures"]
type_by_graph_type: dict[str, list[str]] = data["graphe type"]
entrance_exit_by_type: dict[str, list[dict[str, list[str]]]] = data["route"]
uturn_nodes: list[str] = data["u-turn"]


def map_successors(node_ids, props_by_node_id):
    successor_by_node = {}
    for node_id in node_ids:
        successor_by_node[node_id] = []
        id = props_by_node_id[node_id]["id"]
        sens = props_by_node_id[node_id]["sens"]
        add_successor(node_id, id, sens, successor_by_node)

    return successor_by_node


def handle_node_successors(node_id, structure, sens, successor_by_node):
    successor_structures = structure["successeurs"]
    for next_structure in successor_structures:
        type_next_structure = next_structure["type"]
        id_next_structure = next_structure["id"]
        if next_structure["sens"] == sens:
            if type_next_structure in type_by_graph_type["node"]:  # structure is a node
                successor_by_node[node_id].append(id_next_structure + "," + sens[0])
            else:  # structure is an edge connector
                new_entrance_position = next_structure["successeur_position_entree"]
                add_successor(
                    node_id,
                    id_next_structure,
                    sens,
                    successor_by_node,
                    new_entrance_position,
                )


def handle_edge_connectors(
    node_id, structure, sens, successor_by_node, entrance_position
):
    type_structure = structure["type"]
    exit_positions = []
    for exit_by_entrance in entrance_exit_by_type[type_structure]:
        if exit_by_entrance["position_entree"] == entrance_position:
            exit_positions = exit_by_entrance["positions_sortie"].copy()

    successor_structures = structure["successeurs"]
    for next_structure in successor_structures:
        if (
            next_structure["sens"] == sens
            and next_structure["position_sortie"] in exit_positions
        ):
            type_next_structure = next_structure["type"]
            id_next_structure = next_structure["id"]
            if type_next_structure in type_by_graph_type["node"]:
                successor_by_node[node_id].append(id_next_structure + "," + sens[0])

            else:
                new_entrance_position = next_structure["successeur_position_entree"]
                add_successor(
                    node_id,
                    id_next_structure,
                    sens,
                    successor_by_node,
                    new_entrance_position,
                )


def handle_uturn_node(node_id, structure, sens, successor_by_node):
    id = structure["id"]
    if id in uturn_nodes:
        if sens == "horaire":
            new_sens = "trigo"
        else:
            new_sens = "horaire"
        successor_by_node[node_id].append(id + "," + new_sens[0])


def add_successor(
    node_id,
    id,
    sens,
    successor_by_node,
    entrance_position=None,
) -> None:
    for structure in structures:
        if structure["id"] == id:
            if entrance_position is None:
                handle_node_successors(node_id, structure, sens, successor_by_node)
                handle_uturn_node(node_id, structure, sens, successor_by_node)
            else:
                handle_edge_connectors(
                    node_id, structure, sens, successor_by_node, entrance_position
                )


def create_node_ids_and_props():
    node_ids = []
    props_by_node_id = {}
    for structure in structures:
        current_id = structure["id"]
        current_type = structure["type"]
        if current_type in type_by_graph_type["node"]:
            for successor_structures in structure["successeurs"]:
                current_sens = successor_structures["sens"]
                node_id = current_id + "," + current_sens[0]
                if node_id not in node_ids:
                    node_ids.append(node_id)
                    props_by_node_id[node_id] = {"id": current_id, "sens": current_sens}

    for structure in structures:
        for successor_structures in structure["successeurs"]:
            current_sens = successor_structures["sens"]
            successeur_id = successor_structures["id"]
            successeur_type = successor_structures["type"]
            if successeur_type in type_by_graph_type["node"]:
                node_id = successeur_id + "," + current_sens[0]
                if node_id not in node_ids:
                    node_ids.append(node_id)
                    props_by_node_id[node_id] = {
                        "id": successeur_id,
                        "sens": current_sens,
                    }

    for id in uturn_nodes:
        node_id_1 = id + ",t"
        node_id_2 = id + ",h"
        if node_id_1 not in node_ids:
            node_ids.append(node_id_1)
            props_by_node_id[node_id_1] = {"id": id, "sens": "trigo"}
        if node_id_2 not in node_ids:
            node_ids.append(node_id_2)
            props_by_node_id[node_id_2] = {"id": id, "sens": "horaire"}
    return node_ids, props_by_node_id


if __name__ == "__main__":
    node_ids, props_by_node_id = create_node_ids_and_props()
    successor_by_node = map_successors(node_ids, props_by_node_id)
    G = nx.DiGraph(successor_by_node)
    nx.write_gexf(G, rf"{BASE_DIR}\graph.gexf")

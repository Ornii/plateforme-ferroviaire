import json
from pathlib import Path
from platform import node

import matplotlib.pyplot as plt
import networkx as nx

BASE_DIR = str(Path(__file__).parent.resolve())
json_file = open(rf"{BASE_DIR}\circuit.json", "r")
data = json.load(json_file)
json_file.close()
list_structures = data["structures"]
dict_graph_type = data["graphe type"]
dict_route = data["route"]
list_uturn = data["u-turn"]


def add_successor(
    id,
    sens,
    position_entree=None,
) -> None:
    for structure in list_structures:
        if structure["id"] == id:
            type_structure = structure["type"]
            for potential_successor in structure["successeurs"]:
                type_potential_successor = potential_successor["type"]
                id_potential_successor = potential_successor["id"]
                if position_entree is None and potential_successor["sens"] == sens:
                    if type_potential_successor in dict_graph_type["node"]:
                        successor_by_node[node_id].append(
                            id_potential_successor + "," + sens[0]
                        )
                    else:
                        new_id = id_potential_successor
                        new_position_entree = potential_successor[
                            "successeur_position_entree"
                        ]
                        add_successor(
                            new_id,
                            sens,
                            new_position_entree,
                        )

                if position_entree is not None and potential_successor["sens"] == sens:
                    positions_sortie = []
                    for sorties_by_entree in dict_route[type_structure]:
                        if sorties_by_entree["position_entree"] == position_entree:
                            positions_sortie = sorties_by_entree["positions_sortie"]
                    if potential_successor["position_sortie"] in positions_sortie:
                        type_potential_successor = potential_successor["type"]
                        id_potential_successor = potential_successor["id"]
                        if type_potential_successor in dict_graph_type["node"]:
                            successor_by_node[node_id].append(
                                id_potential_successor + "," + sens[0]
                            )

                        else:
                            new_id = id_potential_successor
                            new_position_entree = potential_successor[
                                "successeur_position_entree"
                            ]
                            add_successor(
                                new_id,
                                sens,
                                new_position_entree,
                            )

            if id in list_uturn:
                if sens == "horaire":
                    new_sens = "trigo"
                else:
                    new_sens = "horaire"
                successor_by_node[node_id].append(id + "," + new_sens[0])


node_ids = []
props_by_node_id = {}

for dict_structure in list_structures:
    current_id = dict_structure["id"]
    current_type = dict_structure["type"]
    if current_type in dict_graph_type["node"]:
        for dict_successeur in dict_structure["successeurs"]:
            current_sens = dict_successeur["sens"]
            node_id = current_id + "," + current_sens[0]
            if node_id not in node_ids:
                node_ids.append(node_id)
                props_by_node_id[node_id] = {"id": current_id, "sens": current_sens}

for dict_structure in list_structures:
    for dict_successeur in dict_structure["successeurs"]:
        current_sens = dict_successeur["sens"]
        successeur_id = dict_successeur["id"]
        successeur_type = dict_successeur["type"]
        if successeur_type in dict_graph_type["node"]:
            node_id = successeur_id + "," + current_sens[0]
            if node_id not in node_ids:
                node_ids.append(node_id)
                props_by_node_id[node_id] = {"id": successeur_id, "sens": current_sens}

for id in list_uturn:
    node_id_1 = id + ",t"
    node_id_2 = id + ",h"
    if node_id_1 not in node_ids:
        node_ids.append(node_id_1)
        props_by_node_id[node_id_1] = {"id": id, "sens": "trigo"}
    if node_id_2 not in node_ids:
        node_ids.append(node_id_2)
        props_by_node_id[node_id_2] = {"id": id, "sens": "horaire"}

successor_by_node = {}
for node_id in node_ids:
    successor_by_node[node_id] = []
    id = props_by_node_id[node_id]["id"]
    sens = props_by_node_id[node_id]["sens"]
    add_successor(id, sens)
G = nx.DiGraph(successor_by_node)
nx.write_gexf(G, rf"{BASE_DIR}\graph.gexf")

print(successor_by_node)

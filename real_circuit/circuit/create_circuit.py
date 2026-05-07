from __future__ import annotations

from enum import Enum
from json import load
from pathlib import Path
from typing import Any, TypedDict

BASE_DIR = str(Path(__file__).parent.resolve())


class DictPositionEntreeSortie(TypedDict):
    position_entree: str
    positions_sorties: list[str]


class DictRoute(TypedDict):
    aiguillage: list[DictPositionEntreeSortie]
    aiguillage_triple: list[DictPositionEntreeSortie]
    croisement_avec_aiguille: list[DictPositionEntreeSortie]
    croisement_sans_aiguille: list[DictPositionEntreeSortie]


class DictStructureSuccesseur(TypedDict):
    sens: str
    id: str
    via_position_sortie: str
    structure_suivante_position_entree: str


class DictStructure(TypedDict):
    type: str
    id: str
    u_turn: str
    sens_circulation: list[str]
    structures_suivantes: list[DictStructureSuccesseur]


class StructureType(Enum):
    AIGUILLAGE = "aiguillage"
    AIGUILLAGE_TRIPLE = "aiguillage_triple"
    CROISEMENT_SANS_AIGUILLE = "croisement_sans_aiguille"
    CROISEMENT_AVEC_AIGUILLE = "croisement_avec_aiguille"
    CANTON = "canton"
    TERMINAL = "terminal"


class Circuit:
    def __init__(self) -> None:
        self.structures = []
        self.structure_by_id = {}

    def add_structures(self, structure: Structure) -> None:
        if structure not in self.structures:
            self.structures.append(structure)
            self.structure_by_id[structure.id] = structure

    def find_structure(self, id: str) -> Structure:
        assert id in self.structure_by_id
        return self.structure_by_id[id]


class Structure:
    def __init__(self, id: str, type: StructureType) -> None:
        self.id = id
        self.type = type
        self.is_occupied = False
        self.is_reserved = False
        self.next_structures: list[tuple[Structure, str, str]] = []

    def __eq__(self, value: object) -> bool:
        assert isinstance(value, Structure)
        return self.id == value.id

    def __str__(self) -> str:
        result_list = [
            f"{structure.id} via {entry} to {exit}"
            for (structure, entry, exit) in self.next_structures
        ]
        result_str = ""
        for e in result_list:
            result_str += "- " + e + "\n"
        return f"Structure is a {self.type.name} with id {self.id}.\nIts next structures are:\n{result_str}"

    def set_reservation(self, is_reserved: bool) -> None:
        self.is_reserved = is_reserved

    def set_occupation(self, is_occupied: bool) -> None:
        self.is_occupied = is_occupied

    def add_next_structure(self, structure: Structure, entry_id: str, exit_id: str):
        self.next_structures.append((structure, entry_id, exit_id))

    def create_canton(self, is_u_turn_allowed: bool, allowed_directions: list[str]):
        self.is_u_turn_allowed = is_u_turn_allowed
        self.allowed_directions = allowed_directions

    def prepare_of_arrival(self, next_structure: Structure):
        pass


def create_structures(
    circuit: Circuit,
    dict_structure: DictStructure,
) -> None:

    structure = Structure(dict_structure["id"], StructureType(dict_structure["type"]))
    if structure.type == StructureType.CANTON:
        structure.create_canton(
            dict_structure["u_turn"] == "true", dict_structure["sens_circulation"]
        )
    circuit.add_structures(structure)


def create_next_structures(
    circuit: Circuit,
    dict_structure: DictStructure,
) -> None:
    structure = circuit.find_structure(dict_structure["id"])
    for dict_next_structure in dict_structure["structures_suivantes"]:
        id_next_structure = dict_next_structure["id"]
        next_structure = circuit.find_structure(id_next_structure)
        if next_structure is None:
            raise Exception("id is in successor but not in root")
        else:
            assert structure is not None  # for type checker
            structure.add_next_structure(
                next_structure,
                dict_next_structure["via_position_sortie"],
                dict_next_structure["structure_suivante_position_entree"],
            )


def load_json_file(filename: str) -> Any:
    with open(BASE_DIR + "/" + str(filename), "r", encoding="utf-8") as json_file:
        data_as_dict = load(json_file)
    return data_as_dict


def create_circuit(
    circuit_filename: str,
    id_position_filename: str,
    route_filename: str,
) -> Circuit:

    list_structures: list[DictStructure] = load_json_file(circuit_filename)
    # dict_id: dict[str, str] = load_json_file(id_position_filename)
    # dict_route: DictRoute = load_json_file(route_filename)

    circuit = Circuit()

    for structure in list_structures:
        create_structures(
            circuit,
            structure,
        )
    for structure in list_structures:
        create_next_structures(
            circuit,
            structure,
        )
    return circuit


if __name__ == "__main__":
    circuit = create_circuit("circuit.json", "id.json", "route.json")
    print(circuit.find_structure("C1"))

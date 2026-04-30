from __future__ import annotations

from json import load
from pathlib import Path
from typing import Any, TypedDict, Union

BASE_DIR = str(Path(__file__).parent.resolve())
type Structure = Union[
    Canton,
    Aiguillage,
    AiguillageTriple,
    CroisementAvecAiguille,
    CroisementSansAiguille,
    Terminal,
]


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


class Circuit:
    def __init__(self) -> None:
        self.cantons = Cantons()
        self.aiguillages = Aiguillages()
        self.aiguillages_triple = AiguillagesTriple()
        self.croisements_sans_aiguille = CroisementsSansAiguille()
        self.croisements_avec_aiguille = CroisementsAvecAiguille()
        self.terminaux = Terminaux()

    def find_structure(self, id: str) -> None | Structure:
        if self.cantons.find_canton(id) is not None:
            return self.cantons.find_canton(id)

        elif self.aiguillages.find_aiguillage(id) is not None:
            return self.aiguillages.find_aiguillage(id)

        elif self.aiguillages_triple.find_aiguillage_triple(id) is not None:
            return self.aiguillages_triple.find_aiguillage_triple(id)

        elif (
            self.croisements_sans_aiguille.find_croisement_sans_aiguille(id) is not None
        ):
            return self.croisements_sans_aiguille.find_croisement_sans_aiguille(id)

        elif (
            self.croisements_avec_aiguille.find_croisement_avec_aiguille(id) is not None
        ):
            return self.croisements_avec_aiguille.find_croisement_avec_aiguille(id)

        elif self.terminaux.find_terminal(id) is not None:
            return self.terminaux.find_terminal(id)

        return None


class Structures:
    def __init__(self) -> None:
        self.list_structures = []
        self.structure_by_id = {}

    def add_structure(self, canton: Canton):
        self.list_structures.append(canton)
        self.structure_by_id[canton.id] = canton


class Cantons:
    def __init__(self) -> None:
        self.list_cantons: list[Canton] = []
        self.canton_by_id: dict[str, Canton] = {}
        self.is_occupied = False
        self.is_reserved = False

    def add_canton(self, canton: Canton):
        self.list_cantons.append(canton)
        self.canton_by_id[canton.id] = canton

    def find_canton(self, id: str) -> None | Canton:
        if id not in self.canton_by_id:
            return None
        return self.canton_by_id[id]


class Canton:
    def __init__(
        self, id: str, allowed_directions: list[str], is_uturn_allowed: str
    ) -> None:
        self.id = id
        self.allowed_directions = allowed_directions
        self.is_uturn_allowed = is_uturn_allowed == "true"
        self.next_structures: list[tuple[Structure, str, str]] = []

    def add_next_structures(
        self, structure: Structure, via_position: str, to_position: str
    ):
        self.next_structures.append((structure, via_position, to_position))

    def __str__(self) -> str:
        result_list = [
            f"{structure.id} via {entry} to {exit}"
            for (structure, entry, exit) in self.next_structures
        ]
        result_str = ""
        for e in result_list:
            result_str += "- " + e + "\n"
        return f"Structure is a canton with id {self.id}.\nIts next structures are:\n{result_str}"


class Terminaux:
    def __init__(self) -> None:
        self.list_terminaux = []
        self.terminal_by_id = {}

    def add_terminal(self, terminal: Terminal):
        self.list_terminaux.append(terminal)
        self.terminal_by_id[terminal.id] = terminal

    def find_terminal(self, id: str):
        if id not in self.terminal_by_id:
            return None
        return self.terminal_by_id[id]


class Terminal:
    def __init__(
        self,
        id: str,
    ) -> None:
        self.id = id
        self.next_structures: list[tuple[Structure, str, str]] = []
        self.is_occupied = False
        self.is_reserved = False

    def add_next_structures(
        self, structure: Structure, via_position: str, to_position: str
    ):
        self.next_structures.append((structure, via_position, to_position))

    def __str__(self) -> str:
        result_list = [
            f"{structure.id} via {entry} to {exit}"
            for (structure, entry, exit) in self.next_structures
        ]
        result_str = ""
        for e in result_list:
            result_str += "- " + e + "\n"
        return f"Structure is a terminal with id {self.id}.\nIts next structures are:\n{result_str}"


class Aiguillages:
    def __init__(self) -> None:
        self.list_aiguillages: list[Aiguillage] = []
        self.aiguillage_by_id: dict[str, Aiguillage] = {}

    def add_aiguillage(self, aiguillage: Aiguillage):
        self.list_aiguillages.append(aiguillage)
        self.aiguillage_by_id[aiguillage.id] = aiguillage

    def find_aiguillage(self, id: str) -> None | Aiguillage:
        if id not in self.aiguillage_by_id:
            return None
        return self.aiguillage_by_id[id]


class Aiguillage:
    def __init__(
        self,
        id: str,
    ) -> None:
        self.id = id
        self.next_structures: list[tuple[Structure, str, str]] = []

    def add_next_structures(
        self, structure: Structure, via_position: str, to_position: str
    ):
        self.next_structures.append((structure, via_position, to_position))

    def __str__(self) -> str:
        result_list = [
            f"{structure.id} via {entry} to {exit}"
            for (structure, entry, exit) in self.next_structures
        ]
        result_str = ""
        for e in result_list:
            result_str += "- " + e + "\n"
        return f"Structure is an aiguillage with id {self.id}.\nIts next structures are:\n{result_str}"


class AiguillagesTriple:
    def __init__(self) -> None:
        self.list_aiguillages_triple: list[AiguillageTriple] = []
        self.aiguillage_triple_by_id: dict[str, AiguillageTriple] = {}

    def add_aiguillage_triple(self, aiguillage_triple: AiguillageTriple):
        self.list_aiguillages_triple.append(aiguillage_triple)
        self.aiguillage_triple_by_id[aiguillage_triple.id] = aiguillage_triple

    def find_aiguillage_triple(self, id: str) -> None | AiguillageTriple:
        if id not in self.aiguillage_triple_by_id:
            return None
        return self.aiguillage_triple_by_id[id]


class AiguillageTriple:
    def __init__(
        self,
        id: str,
    ) -> None:
        self.id = id
        self.next_structures: list[tuple[Structure, str, str]] = []

    def add_next_structures(
        self, structure: Structure, via_position: str, to_position: str
    ):
        self.next_structures.append((structure, via_position, to_position))

    def __str__(self) -> str:
        result_list = [
            f"{structure.id} via {entry} to {exit}"
            for (structure, entry, exit) in self.next_structures
        ]
        result_str = ""
        for e in result_list:
            result_str += "- " + e + "\n"
        return f"Structure is a triple aiguillage with id {self.id}.\nIts next structures are:\n{result_str}"


class CroisementsSansAiguille:
    def __init__(self) -> None:
        self.list_croisements_sans_aiguille: list[CroisementSansAiguille] = []
        self.croisement_sans_aiguille_by_id: dict[str, CroisementSansAiguille] = {}

    def add_croisement_sans_aiguille(
        self, croisement_sans_aiguille: CroisementSansAiguille
    ):
        self.list_croisements_sans_aiguille.append(croisement_sans_aiguille)
        self.croisement_sans_aiguille_by_id[croisement_sans_aiguille.id] = (
            croisement_sans_aiguille
        )

    def find_croisement_sans_aiguille(self, id: str) -> None | CroisementSansAiguille:
        if id not in self.croisement_sans_aiguille_by_id:
            return None
        return self.croisement_sans_aiguille_by_id[id]


class CroisementSansAiguille:
    def __init__(
        self,
        id: str,
    ) -> None:
        self.id = id
        self.next_structures: list[tuple[Structure, str, str]] = []

    def add_next_structures(
        self, structure: Structure, via_position: str, to_position: str
    ):
        self.next_structures.append((structure, via_position, to_position))

    def __str__(self) -> str:
        result_list = [
            f"{structure.id} via {entry} to {exit}"
            for (structure, entry, exit) in self.next_structures
        ]
        result_str = ""
        for e in result_list:
            result_str += "- " + e + "\n"
        return f"Structure is a croisement sans aiguille with id {self.id}.\nIts next structures are:\n{result_str}"


class CroisementsAvecAiguille:
    def __init__(self) -> None:
        self.list_croisements_avec_aiguille = []
        self.croisement_avec_aiguille_by_id = {}

    def add_croisement_avec_aiguille(
        self, croisement_avec_aiguille: CroisementAvecAiguille
    ):
        self.list_croisements_avec_aiguille.append(croisement_avec_aiguille)
        self.croisement_avec_aiguille_by_id[croisement_avec_aiguille.id] = (
            croisement_avec_aiguille
        )

    def find_croisement_avec_aiguille(self, id: str) -> None | CroisementAvecAiguille:
        if id not in self.croisement_avec_aiguille_by_id:
            return None
        return self.croisement_avec_aiguille_by_id[id]


class CroisementAvecAiguille:
    def __init__(
        self,
        id: str,
    ) -> None:
        self.id = id
        self.next_structures: list[tuple[Structure, str, str]] = []

    def add_next_structures(
        self, structure: Structure, via_position: str, to_position: str
    ):
        self.next_structures.append((structure, via_position, to_position))

    def __str__(self) -> str:
        result_list = [
            f"{structure.id} via {entry} to {exit}"
            for (structure, entry, exit) in self.next_structures
        ]
        result_str = ""
        for e in result_list:
            result_str += "- " + e + "\n"
        return f"Structure is a croisement avec aiguille with id {self.id}.\nIts next structures are:\n{result_str}"


def create_objects(
    circuit: Circuit,
    structure: DictStructure,
) -> None:

    if structure["type"] == "canton":
        canton = Canton(
            structure["id"], structure["sens_circulation"], structure["u_turn"]
        )
        circuit.cantons.add_canton(canton)

    elif structure["type"] == "aiguillage":
        aiguillage = Aiguillage(structure["id"])
        circuit.aiguillages.add_aiguillage(aiguillage)

    elif structure["type"] == "terminal":
        terminal = Terminal(structure["id"])
        circuit.terminaux.add_terminal(terminal)

    elif structure["type"] == "aiguillage_triple":
        aiguillage_triple = AiguillageTriple(structure["id"])
        circuit.aiguillages_triple.add_aiguillage_triple(aiguillage_triple)

    elif structure["type"] == "croisement_sans_aiguille":
        croisement_sans_aiguille = CroisementSansAiguille(structure["id"])
        circuit.croisements_sans_aiguille.add_croisement_sans_aiguille(
            croisement_sans_aiguille
        )

    elif structure["type"] == "croisement_avec_aiguille":
        croisement_avec_aiguille = CroisementAvecAiguille(structure["id"])
        circuit.croisements_avec_aiguille.add_croisement_avec_aiguille(
            croisement_avec_aiguille
        )


def create_next_structures(
    circuit: Circuit,
    dict_structure: DictStructure,
) -> None:
    structure = circuit.find_structure(dict_structure["id"])
    for dict_next_structure in dict_structure["structures_suivantes"]:
        id_next_structure = dict_next_structure["id"]
        next_structure = circuit.find_structure(id_next_structure)
        if next_structure is None:
            print(id_next_structure)
            raise Exception("id is in successor but not in root")
        else:
            assert structure is not None  # for type checker
            structure.add_next_structures(
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
):

    list_structures: list[DictStructure] = load_json_file(circuit_filename)
    dict_id: dict[str, str] = load_json_file(id_position_filename)
    dict_route: DictRoute = load_json_file(route_filename)

    circuit = Circuit()

    for structure in list_structures:
        create_objects(
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

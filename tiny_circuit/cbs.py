from __future__ import annotations

from enum import Enum, auto


class CollisionType(Enum):
    SWAP_COLLISION = auto()
    NODE_COLLISION = auto()


class Collision:
    def __init__(self, type: CollisionType) -> None:
        self.type = type

    def add_node_collision(self, node: Node, agents: tuple[Agent, Agent], time: int):
        self.node = node
        self.agents = agents
        self.time = time

    def add_swap_collision(
        self,
        nodes: tuple[Node, Node],
        agents: tuple[Agent, Agent],
        times: tuple[int, int],
    ):
        self.nodes = nodes
        self.agents = agents
        self.times = times


class Node:
    def __init__(self, id: str) -> None:
        self.id = id
        self.is_occupied: bool = False

    def add_successors(self, successors: dict[Node, int]):
        self.successors = successors

    def get_id(self):
        return self.id


class Graphe:
    def __init__(self, adjacency_matrix: dict[str, dict[str, int]]) -> None:
        self.nodes = []
        self.dict_nodes = {}
        for node_id in adjacency_matrix:
            self.nodes.append(Node(node_id))

        for node_id, successors_dict_id in adjacency_matrix.items():
            successors_dict_nodes = {}
            for successor_node_id in successors_dict_id:
                successors_dict_nodes[self.dict_nodes[node_id]] = successors_dict_id[
                    successor_node_id
                ]
            self.dict_nodes[node_id].add_successors(successors_dict_nodes)

    def get_node_with_id(self, node_id: str):
        return self.dict_nodes[node_id]

    def get_nodes(self):
        return self.nodes


class Agent:
    def __init__(self, id: str, start_node: Node, target_node: Node) -> None:
        self.id = id
        self.start_node = start_node
        self.current_node = start_node
        self.target_node = target_node

    def get_id(self):
        return self.id

    def get_start_node(self):
        return self.start_node

    def get_target_node(self):
        return self.target_node


class Scenario:
    def __init__(self) -> None:
        self.constraints = []
        self.collisions = []

    def create_paths_and_cost(self, graphe: Graphe, list_agents: list[Agent]):
        self.paths = {}
        self.cost = 0
        for agent in list_agents:
            self.paths[agent], cost = djikstra(
                graphe, agent.start_node, agent.target_node
            )
            if cost == -1:
                raise Exception("Routing is impossible")
            self.cost += cost

    def get_cost(self) -> int:
        return self.cost

    def detect_collisions(self):
        self.detect_nodes_collisions()
        self.detect_swap_collisions()

    def detect_nodes_collisions(self) -> None:
        all_paths = []
        all_agents = []
        for agent, path in self.paths.items():
            all_paths.append(path)
            all_agents.append(agent)
        for i in range(len(all_paths)):
            for j in range(i + 1, len(all_paths)):
                for t in range(len(all_paths[i])):
                    if t <= len(all_paths[j]) and all_paths[i][t] == all_paths[j][t]:
                        collision = Collision(CollisionType.NODE_COLLISION)
                        collision.add_node_collision(
                            all_paths[i][t], (all_agents[i], all_agents[j]), t
                        )
                        self.collisions.append(collision)

    def detect_swap_collisions(self) -> None:
        all_paths = []
        all_agents = []
        for agent, path in self.paths.items():
            all_paths.append(path)
            all_agents.append(agent)
        for i in range(len(all_paths)):
            for j in range(i + 1, len(all_paths)):
                for t in range(len(all_paths[i]) - 1):
                    if (
                        t + 1 <= len(all_paths[j]) - 1
                        and all_paths[i][t] == all_paths[j][t + 1]
                        and all_paths[i][t + 1] == all_paths[j][t]
                    ):
                        collision = Collision(CollisionType.SWAP_COLLISION)
                        collision.add_swap_collision(
                            (all_paths[i][t], all_paths[j][t]),
                            (all_agents[i], all_agents[j]),
                            (t, t + 1),
                        )
                        self.collisions.append(collision)

    def get_collisions(self):
        return self.collisions

    def add_constraints(self, constraints):
        self.constraints.append(constraints)

    def copy_paths_and_cost(self, scenario: Scenario):
        self.paths = scenario.paths
        self.cost = scenario.cost

    def change_path(self, agent: Agent, path: list[Node]):
        self.paths[agent] = path

    def change_cost(self, cost: int):
        self.cost = cost


def minimum_distance_with_chosen_nodes(
    distances: dict[Node, int], chosen_nodes: list[Node]
) -> Node:
    mini_node = chosen_nodes[0]
    mini_distance = distances[mini_node]
    for node in chosen_nodes:
        if distances[node] < mini_distance:
            mini_node = node
            mini_distance = distances[node]
    return mini_node


def minimum_cost_scenario(scenarios: list[Scenario]) -> Scenario:
    mini_scenario = scenarios[0]
    mini_cost = mini_scenario.get_cost()
    for scenario in scenarios:
        if scenario.get_cost() < mini_cost:
            mini_cost = scenario.get_cost()
            mini_scenario = scenario
    return mini_scenario


def djikstra(
    graphe: Graphe,
    start_node: Node,
    target_node: Node,
    constraints=[],
) -> tuple[list[Node], int]:
    nodes_not_visited = graphe.get_nodes().copy()
    predecessors = {}
    for node in nodes_not_visited:
        predecessors[node] = "Unknown"
    predecessors[start_node] = start_node
    distances = {}
    for node in nodes_not_visited:
        distances[node] = float("inf")
    distances[start_node] = 0
    node = minimum_distance_with_chosen_nodes(distances, nodes_not_visited)
    nodes_not_visited.remove(node)
    while node != target_node:
        for successor_node in node.successors:
            if (
                distances[successor_node]
                > distances[node] + node.successors[successor_node]
            ):
                predecessors[successor_node] = node
                distances[successor_node] = (
                    distances[node] + node.successors[successor_node]
                )
        node = minimum_distance_with_chosen_nodes(distances, nodes_not_visited)
        nodes_not_visited.remove(node)
    if distances[target_node] == float("inf"):
        return [], -1
    result = []
    node = target_node
    result.append(node)
    while node != start_node:
        node = predecessors[node]
        result.append(node)
    return result[::-1], distances[target_node]


def CBS(graphe: Graphe, list_agents: list[Agent]):

    open_scenarios = []
    scenario = Scenario()
    scenario.create_paths_and_cost(graphe, list_agents)

    scenario.detect_collisions()

    open_scenarios.append(scenario)

    while len(open_scenarios) > 0:
        scenario = minimum_cost_scenario(open_scenarios)
        open_scenarios.remove(scenario)

        if len(scenario.get_collisions()) == 0:
            return scenario

        collision = scenario.get_collisions()[0]
        constraints_list = standard_splitting(collision)

        for constraint in constraints_list:
            new_scenario = Scenario()
            new_scenario.add_constraints(constraint)
            new_scenario.copy_paths_and_cost(scenario)

            agent = constraint.get_agent()
            start_node = agent.get_start_node()
            target_node = agent.get_target_node()

            new_path, new_cost = djikstra(
                graphe, start_node, target_node, new_scenario.constraints
            )

            if new_path is not None:
                new_scenario.change_path(agent, new_path)
                new_scenario.change_cost(new_cost)
                new_scenario.detect_collisions()
                open_scenarios.append(new_scenario)
    return None


if __name__ == "__main__":
    G = {
        "1": {"2": 10, "3": 7, "4": 5},
        "2": {"5": 1},
        "3": {"2": 2, "5": 4, "7": 9},
        "4": {"3": 1, "6": 9},
        "5": {"6": 3, "7": 6},
        "6": {"7": 4},
        "7": {},
    }

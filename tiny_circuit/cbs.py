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


class ConstraintType(Enum):
    NODE_CONSTRAINT = auto()
    EDGE_CONSTRAINT = auto()


class Constraint:
    def __init__(
        self,
        agent: Agent,
        type: ConstraintType,
        node: Node | None = None,
        time: int | None = None,
        edge: tuple[Node, Node] | None = None,
    ) -> None:
        self.agent = agent
        self.type = type
        self.node = node
        self.time = time
        self.edge = edge

    def get_agent(self) -> Agent:
        return self.agent

    def forbids(self, current_node: Node, next_node: Node, next_time: int) -> bool:
        if self.type == ConstraintType.NODE_CONSTRAINT:
            return self.node == next_node and self.time == next_time
        if self.type == ConstraintType.EDGE_CONSTRAINT:
            if self.edge is None or self.time is None:
                return False
            return (
                self.edge[0] == current_node
                and self.edge[1] == next_node
                and self.time == next_time - 1
            )
        return False


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
            node = Node(node_id)
            self.nodes.append(node)
            self.dict_nodes[node_id] = node

        for node_id, successors_dict_id in adjacency_matrix.items():
            successors_dict_nodes = {}
            for successor_node_id, successor_cost in successors_dict_id.items():
                successors_dict_nodes[self.dict_nodes[successor_node_id]] = (
                    successor_cost
                )
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
        self.collisions = []
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
                    if (
                        t <= len(all_paths[j]) - 1
                        and all_paths[i][t] == all_paths[j][t]
                    ):
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

    def copy_paths_cost_constraints(self, scenario: Scenario):
        new_paths = {}
        for agent, path in scenario.paths.items():
            new_paths[agent] = path.copy()
        self.paths = new_paths
        self.cost = scenario.cost
        self.constraints = scenario.constraints.copy()

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


def standard_splitting(collision: Collision) -> list[Constraint]:
    if collision.type == CollisionType.NODE_COLLISION:
        agent1, agent2 = collision.agents
        node = collision.node
        time = collision.time
        return [
            Constraint(agent1, ConstraintType.NODE_CONSTRAINT, node=node, time=time),
            Constraint(agent2, ConstraintType.NODE_CONSTRAINT, node=node, time=time),
        ]

    else:
        agent1, agent2 = collision.agents
        node1, node2 = collision.nodes
        time = collision.times[0]
        return [
            Constraint(
                agent1,
                ConstraintType.EDGE_CONSTRAINT,
                edge=(node1, node2),
                time=time,
            ),
            Constraint(
                agent2,
                ConstraintType.EDGE_CONSTRAINT,
                edge=(node2, node1),
                time=time,
            ),
        ]


def djikstra(
    graphe: Graphe,
    start_node: Node,
    target_node: Node,
    constraints=None,
) -> tuple[list[Node], int]:
    if constraints is None:
        constraints = []

    max_constraint_time = -1
    for constraint in constraints:
        if constraint.time is not None and constraint.time > max_constraint_time:
            max_constraint_time = constraint.time
    max_time = max_constraint_time + len(graphe.get_nodes()) + 2

    nodes_not_visited = [(start_node, 0)]
    predecessors = {(start_node, 0): (start_node, 0)}
    distances = {(start_node, 0): 0}
    visited_nodes = []

    node = (start_node, 0)
    while len(nodes_not_visited) > 0:
        mini_node = nodes_not_visited[0]
        mini_distance = distances[mini_node]
        for chosen_node in nodes_not_visited:
            if distances[chosen_node] < mini_distance:
                mini_node = chosen_node
                mini_distance = distances[chosen_node]
        node = mini_node
        nodes_not_visited.remove(node)
        visited_nodes.append(node)

        current_node, current_time = node
        if current_node == target_node and current_time >= max_constraint_time:
            break
        if current_time >= max_time:
            continue

        candidate_successors = {}
        for successor_node, successor_cost in current_node.successors.items():
            candidate_successors[successor_node] = successor_cost
        candidate_successors[current_node] = 1

        for successor_node, successor_cost in candidate_successors.items():
            next_time = current_time + 1
            forbidden = False
            for constraint in constraints:
                if constraint.forbids(current_node, successor_node, next_time):
                    forbidden = True
                    break
            if forbidden:
                continue

            successor_state = (successor_node, next_time)
            new_distance = distances[node] + successor_cost
            if (
                successor_state not in distances
                or distances[successor_state] > new_distance
            ):
                predecessors[successor_state] = node
                distances[successor_state] = new_distance
                if successor_state not in nodes_not_visited:
                    nodes_not_visited.append(successor_state)

    target_state = None
    best_distance = float("inf")
    for state in visited_nodes:
        state_node, _ = state
        if state_node == target_node and distances[state] < best_distance:
            best_distance = distances[state]
            target_state = state
    if target_state is None:
        return [], -1

    result = []
    node = target_state
    result.append(node[0])
    while node != (start_node, 0):
        node = predecessors[node]
        result.append(node[0])
    return result[::-1], distances[target_state]


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
            new_scenario.copy_paths_cost_constraints(scenario)
            new_scenario.add_constraints(constraint)
            agent = constraint.get_agent()
            start_node = agent.get_start_node()
            target_node = agent.get_target_node()
            constraints = []
            for scenario_constraint in new_scenario.constraints:
                if scenario_constraint.get_agent() == agent:
                    constraints.append(scenario_constraint)

            new_path, _ = djikstra(
                graphe, start_node, target_node, constraints
            )

            if len(new_path) > 0:
                new_scenario.change_path(agent, new_path)
                new_cost = 0
                for path in new_scenario.paths.values():
                    for i in range(len(path) - 1):
                        if path[i + 1] in path[i].successors:
                            new_cost += path[i].successors[path[i + 1]]
                        else:
                            new_cost += 1
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

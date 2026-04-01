from __future__ import annotations

from enum import Enum, auto

WAITING_COST = 1


# TODO:
# -raise error if node is itself a predecessor
class CollisionType(Enum):
    EDGE_COLLISION = auto()
    NODE_COLLISION = auto()


class Collision:
    def __init__(self, type: CollisionType) -> None:
        self.type = type
        self.nodes = []
        self.agents = []

    def add_node_collision(self, node: Node, agents: list[Agent], time: int):
        self.nodes.append(node)
        for agent in agents:
            self.agents.append(agent)
        self.time = time

    def add_edge_collision(
        self,
        nodes: list[Node],
        agents: list[Agent],
        time: int,
    ):
        for node in nodes:
            self.nodes.append(node)
        for agent in agents:
            self.agents.append(agent)
        self.time = time

    def get_nodes(self) -> list[Node]:
        return self.nodes

    def get_agents(self) -> list[Agent]:
        return self.agents

    def get_time(self) -> int:
        return self.time


class ConstraintType(Enum):
    NODE_CONSTRAINT = auto()
    EDGE_CONSTRAINT = auto()


class Constraint:
    def __init__(
        self,
        agent: Agent,
        type: ConstraintType,
        nodes: list[Node],
        time: int,
    ) -> None:
        self.agent = agent
        self.type = type
        self.nodes = nodes
        self.time = time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Constraint):
            return False
        return (
            self.agent == other.agent
            and self.type == other.type
            and self.nodes == other.nodes
            and self.time == other.time
        )

    def get_agent(self) -> Agent:
        return self.agent

    def forbids(self, current_node: Node, next_node: Node, next_time: int) -> bool:
        if self.type == ConstraintType.NODE_CONSTRAINT:
            return self.nodes[0] == next_node and self.time == next_time
        return (
            self.nodes[0] == current_node
            and self.nodes[1] == next_node
            and self.time == next_time - 1
        )

    def get_time(self) -> int:
        return self.time


class Node:
    def __init__(self, id: str) -> None:
        self.id = id
        self.is_occupied: bool = False

    def add_successors(self, weight_by_successor_node: dict[Node, int]):
        self.weight_by_successor_node = weight_by_successor_node

    def get_id(self) -> str:
        return self.id

    def get_weight_by_successor_node(self):
        return self.weight_by_successor_node


class Graphe:
    def __init__(self, adjacency_matrix: dict[str, dict[str, int]]) -> None:
        self.nodes = []
        self.node_by_id = {}
        for node_id in adjacency_matrix:
            node = Node(node_id)
            self.nodes.append(node)
            self.node_by_id[node_id] = node

        for node_id, weight_by_successor_node_id in adjacency_matrix.items():
            successors_node_by_id = {}
            for (
                successor_node_id,
                successor_weight,
            ) in weight_by_successor_node_id.items():
                successors_node_by_id[self.node_by_id[successor_node_id]] = (
                    successor_weight
                )
            self.node_by_id[node_id].add_successors(successors_node_by_id)

    def get_node_with_id(self, node_id: str) -> Node:
        return self.node_by_id[node_id]

    def get_nodes(self) -> list[Node]:
        return self.nodes


class Agent:
    def __init__(self, id: str, start_node: Node, target_node: Node) -> None:
        self.id = id
        self.start_node = start_node
        self.current_node = start_node
        self.target_node = target_node

    def get_id(self) -> str:
        return self.id

    def get_start_node(self) -> Node:
        return self.start_node

    def get_target_node(self) -> Node:
        return self.target_node


class Scenario:
    def __init__(self) -> None:
        self.constraints = []
        self.collisions = []
        self.cost = 0
        self.path_by_agent = {}

    def route(self, graphe: Graphe, agents: list[Agent]):
        self.cost = 0
        for agent in agents:
            self.path_by_agent[agent], cost = djikstra(
                graphe, agent.start_node, agent.target_node
            )
            if cost == -1:
                raise Exception("Routing is impossible")
            self.cost += cost

    def get_agents(self) -> list[Agent]:
        return list(self.path_by_agent.keys())

    def get_paths(self) -> list[list[Node]]:
        return list(self.path_by_agent.values())

    def get_cost(self) -> int:
        return self.cost

    def detect_collisions(self):
        self.collisions = []
        self.detect_node_collisions()
        self.detect_edge_collisions()

    def detect_node_collisions(self) -> None:
        """
        Detect nodes collisions.
        Node collision happens when two agents or more are on the same node.
        It can happen when an agent is moving or idling.

        This function adds collisions in self.collisions.
        """
        paths = self.get_paths().copy()
        agents = self.get_agents().copy()
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                max_time = max(len(paths[i]), len(paths[j]))
                for t in range(max_time):
                    if t < len(paths[i]):
                        node_i = paths[i][t]  # agent is moving
                    else:
                        node_i = paths[i][-1]  # agent is idling
                    if t < len(paths[j]):
                        node_j = paths[j][t]  # agent is moving
                    else:
                        node_j = paths[j][-1]  # agent is idling
                    if node_i == node_j:
                        collision = Collision(CollisionType.NODE_COLLISION)
                        collision.add_node_collision(node_i, [agents[i], agents[j]], t)
                        self.collisions.append(collision)

    def detect_edge_collisions(self) -> None:
        paths = self.get_paths().copy()
        agents = self.get_agents().copy()
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                for t in range(len(paths[i]) - 1):
                    if t + 1 <= len(paths[j]) - 1:
                        node_i_t = paths[i][t]
                        node_i_tp1 = paths[i][t + 1]
                        node_j_t = paths[j][t]
                        node_j_tp1 = paths[j][t + 1]
                        if node_i_t == node_j_tp1 and node_i_tp1 == node_j_t:
                            collision = Collision(CollisionType.EDGE_COLLISION)
                            collision.add_edge_collision(
                                [node_i_t, node_j_t],
                                [agents[i], agents[j]],
                                t,
                            )
                            self.collisions.append(collision)

    def add_constraints(self, constraints) -> bool:
        if constraints in self.constraints:
            return False
        self.constraints.append(constraints)
        return True

    def copy_paths_cost_constraints(self, scenario: Scenario):
        new_paths = {}
        for agent, path in scenario.path_by_agent.items():
            new_paths[agent] = path.copy()
        self.path_by_agent = new_paths
        self.cost = scenario.cost
        self.constraints = scenario.constraints.copy()

    def change_path(self, agent: Agent, path: list[Node]):
        self.path_by_agent[agent] = path

    def change_cost(self, cost: int):
        self.cost = cost

    def get_collisions(self):
        return self.collisions

    def agent_to_constraints(self, agent: Agent) -> list[Constraint]:
        constraints_of_agent = []
        for constraint in self.constraints:
            if constraint.get_agent() == agent:
                constraints_of_agent.append(constraint)
        return constraints_of_agent

    def calculate_cost(self) -> int:
        self.cost = 0
        for path in self.path_by_agent.values():
            for i in range(len(path) - 1):
                if path[i + 1] in path[i].weight_by_successor_node:
                    self.cost += path[i].weight_by_successor_node[path[i + 1]]
                else:
                    self.cost += WAITING_COST  # in this case, agent stays on its node
        return self.cost


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
        agent_1, agent_2 = collision.get_agents()
        node = collision.get_nodes()[0]
        time = collision.get_time()
        return [
            Constraint(agent_1, ConstraintType.NODE_CONSTRAINT, [node], time),
            Constraint(agent_2, ConstraintType.NODE_CONSTRAINT, [node], time),
        ]

    agent_1, agent_2 = collision.get_agents()
    node_1, node_2 = collision.get_nodes()
    time = collision.time
    return [
        Constraint(
            agent_1,
            ConstraintType.EDGE_CONSTRAINT,
            [node_1, node_2],
            time,
        ),
        Constraint(
            agent_2,
            ConstraintType.EDGE_CONSTRAINT,
            [node_2, node_1],
            time,
        ),
    ]


def minimum_with_chosen_states(
    distances: dict[tuple[Node, int], int], chosen_states: list[tuple[Node, int]]
) -> tuple[Node, int]:
    mini_state = chosen_states[0]
    mini_distance = distances[mini_state]
    for chosen_state in chosen_states:
        if distances[chosen_state] < mini_distance:
            mini_state = chosen_state
            mini_distance = distances[chosen_state]
    return mini_state


def is_successor_node_possible_with_constraints(
    current_node: Node,
    successor_node: Node,
    constraints: list[Constraint],
    next_time: int,
):
    for constraint in constraints:
        if constraint.forbids(current_node, successor_node, next_time):
            return False
    return True


def djikstra(
    graphe: Graphe,
    start_node: Node,
    target_node: Node,
    constraints: list[Constraint] = [],
) -> tuple[list[Node], int]:

    max_constraint_time = max(
        [constraint.get_time() for constraint in constraints] + [0]
    )
    max_time = max_constraint_time + len(graphe.get_nodes())

    """init"""
    not_visited_states = [(start_node, 0)]
    predecessors = {(start_node, 0): (start_node, 0)}
    distances = {(start_node, 0): 0}
    visited_states = []
    """loop"""
    while len(not_visited_states) > 0:
        """chosing the unvisited node with minimal distance """
        mini_state = minimum_with_chosen_states(distances, not_visited_states)
        not_visited_states.remove(mini_state)
        visited_states.append(mini_state)
        current_node, current_time = mini_state

        if current_node == target_node and current_time >= max_constraint_time:
            break
        if current_time >= max_time:
            continue

        """creating all candidates and include the current node itself"""
        candidate_successors = current_node.get_weight_by_successor_node().copy()
        candidate_successors[current_node] = WAITING_COST
        next_time = current_time + 1

        for successor_node, successor_weight in candidate_successors.items():
            if not is_successor_node_possible_with_constraints(
                current_node, successor_node, constraints, next_time
            ):
                continue  # if the constraint forbids current node and a successor then chose another successor

            successor_state = (successor_node, next_time)
            new_distance = distances[mini_state] + successor_weight
            if (
                successor_state not in distances
                or distances[successor_state] > new_distance
            ):
                predecessors[successor_state] = mini_state
                distances[successor_state] = new_distance
                if successor_state not in not_visited_states:
                    not_visited_states.append(successor_state)
    target_state = None
    best_distance = float("inf")
    for state in visited_states:
        node, time = state
        if (
            node == target_node
            and time >= max_constraint_time
            and distances[state] < best_distance
        ):
            target_state = state
            best_distance = distances[state]
    if target_state is None:
        return [], -1

    result = []
    state = target_state
    result.append(state[0])
    while state != (start_node, 0):
        state = predecessors[state]
        result.append(state[0])
    return result[::-1], distances[target_state]


def CBS(graphe: Graphe, agents: list[Agent]) -> Scenario:
    open_scenarios = []
    scenario = Scenario()
    scenario.route(graphe, agents)
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
            if not new_scenario.add_constraints(constraint):
                continue
            agent = constraint.get_agent()
            start_node = agent.get_start_node()
            target_node = agent.get_target_node()

            constraints_of_agent = new_scenario.agent_to_constraints(agent)

            new_path, _ = djikstra(
                graphe, start_node, target_node, constraints_of_agent
            )

            if len(new_path) > 0:
                new_scenario.change_path(agent, new_path)
                new_scenario.calculate_cost()
                new_scenario.detect_collisions()
                open_scenarios.append(new_scenario)
    raise Exception("Routing is impossible")

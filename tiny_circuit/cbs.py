from __future__ import annotations

from enum import Enum, auto


# TODO:
# -waitingcost = 1 is hardcoded
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

    def get_agent(self) -> Agent:
        return self.agent

    def forbids(self, current_node: Node, next_node: Node, next_time: int) -> bool:
        if self.type == ConstraintType.NODE_CONSTRAINT:
            return self.nodes == next_node and self.time == next_time
        return (
            self.nodes[0] == current_node
            and self.nodes[1] == next_node
            and self.time == next_time - 1
        )

    def get_time(self):
        return self.time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Constraint):
            return False
        return (
            self.agent == other.agent
            and self.type == other.type
            and self.nodes == other.nodes
            and self.time == other.time
        )

    def __hash__(self) -> int:
        return hash((self.agent, self.type, self.nodes, self.time))


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
        self.cost = 0
        self.paths = {}

    def create_paths_and_cost(self, graphe: Graphe, list_agents: list[Agent]):
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
        self.detect_node_collisions()
        self.detect_edge_collisions()

    def detect_node_collisions(self) -> None:
        """
        Detect nodes collisions.
        Node collision happens when two agents or more are on the same node.
        It can happen when an agent is moving or idling.

        This function adds collisions in self.collisions.
        """
        all_paths = []
        all_agents = []
        for agent, path in self.paths.items():
            all_paths.append(path)
            all_agents.append(agent)
        for i in range(len(all_paths)):
            for j in range(i + 1, len(all_paths)):
                max_time = max(len(all_paths[i]), len(all_paths[j]))
                for t in range(max_time):
                    if t < len(all_paths[i]):
                        node_i = all_paths[i][t]  # agent is moving
                    else:
                        node_i = all_paths[i][-1]  # agent is idling
                    if t < len(all_paths[j]):
                        node_j = all_paths[j][t]  # agent is moving
                    else:
                        node_j = all_paths[j][-1]  # agent is idling
                    if node_i == node_j:
                        collision = Collision(CollisionType.NODE_COLLISION)
                        collision.add_node_collision(
                            node_i, [all_agents[i], all_agents[j]], t
                        )
                        self.collisions.append(collision)

    def detect_edge_collisions(self) -> None:
        all_paths = []
        all_agents = []
        for agent, path in self.paths.items():
            all_paths.append(path)
            all_agents.append(agent)
        for i in range(len(all_paths)):
            for j in range(i + 1, len(all_paths)):
                for t in range(len(all_paths[i]) - 1):
                    if t + 1 <= len(all_paths[j]) - 1:
                        node_i_t = all_paths[i][t]
                        node_i_tp1 = all_paths[i][t + 1]
                        node_j_t = all_paths[j][t]
                        node_j_tp1 = all_paths[j][t + 1]
                        if node_i_t == node_j_tp1 and node_i_tp1 == node_j_t:
                            collision = Collision(CollisionType.EDGE_COLLISION)
                            collision.add_edge_collision(
                                [node_i_t, node_j_t],
                                [all_agents[i], all_agents[j]],
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
        for agent, path in scenario.paths.items():
            new_paths[agent] = path.copy()
        self.paths = new_paths
        self.cost = scenario.cost
        self.constraints = scenario.constraints.copy()

    def change_path(self, agent: Agent, path: list[Node]):
        self.paths[agent] = path

    def change_cost(self, cost: int):
        self.cost = cost

    def get_collisions(self):
        return self.collisions


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
        node = collision.nodes[0]
        time = collision.time
        return [
            Constraint(agent1, ConstraintType.NODE_CONSTRAINT, node, time),
            Constraint(agent2, ConstraintType.NODE_CONSTRAINT, node, time),
        ]

    else:
        agent1, agent2 = collision.agents
        node1, node2 = collision.nodes
        time = collision.time
        return [
            Constraint(
                agent1,
                ConstraintType.EDGE_CONSTRAINT,
                [node1, node2],
                time,
            ),
            Constraint(
                agent2,
                ConstraintType.EDGE_CONSTRAINT,
                [node2, node1],
                time,
            ),
        ]


def djikstra(
    graphe: Graphe,
    start_node: Node,
    target_node: Node,
    constraints=[],
) -> tuple[list[Node], int]:

    max_constraint_time = -1
    for constraint in constraints:
        if constraint.time > max_constraint_time:
            max_constraint_time = constraint.time
    max_time = max_constraint_time + len(graphe.get_nodes()) + 2

    """init"""
    not_visited_nodes_time = [(start_node, 0)]
    predecessors = {(start_node, 0): (start_node, 0)}
    distances = {(start_node, 0): 0}

    visited_nodes_time = []
    """loop"""
    while len(not_visited_nodes_time) > 0:
        """chosing the unvisited node with minimal distance """
        mini_node_time = not_visited_nodes_time[0]
        mini_distance = distances[mini_node_time]
        for chosen_node_time in not_visited_nodes_time:
            if distances[chosen_node_time] < mini_distance:
                mini_node_time = chosen_node_time
                mini_distance = distances[chosen_node_time]
        not_visited_nodes_time.remove(mini_node_time)
        visited_nodes_time.append(mini_node_time)

        current_node, current_time = (
            mini_node_time  # perhaps current node is forbidden with the constraints
        )

        if current_node == target_node and current_time >= max_constraint_time:
            break
        if current_time >= max_time:
            continue

        """creating all candidate candidates and include the current node itself"""
        candidate_successors = {}

        for successor_node, successor_cost in current_node.successors.items():
            candidate_successors[successor_node] = successor_cost
            candidate_successors[current_node] = 1  # waiting one timestep costs 1
        next_time = current_time + 1
        for successor_node, successor_cost in candidate_successors.items():
            forbidden = False
            for constraint in constraints:
                if constraint.forbids(current_node, successor_node, next_time):
                    forbidden = True
                    break
            if forbidden:
                continue  # if the constraint forbids current node and a successor then chose another successor

            successor_node_time = (successor_node, next_time)
            new_distance = distances[mini_node_time] + successor_cost
            if (
                successor_node_time not in distances
                or distances[successor_node_time] > new_distance
            ):
                predecessors[successor_node_time] = mini_node_time
                distances[successor_node_time] = new_distance
                if successor_node_time not in not_visited_nodes_time:
                    not_visited_nodes_time.append(successor_node_time)
    target_node_time = None
    best_distance = float("inf")
    for node_time in visited_nodes_time:
        node, time = node_time
        if (
            node == target_node
            and time >= max_constraint_time
            and distances[node_time] < best_distance
        ):
            target_node_time = node_time
            best_distance = distances[node_time]
    if target_node_time is None:
        return [], -1

    result = []
    node_time = target_node_time
    result.append(node_time[0])
    while node_time != (start_node, 0):
        node_time = predecessors[node_time]
        result.append(node_time[0])
    return result[::-1], distances[target_node_time]


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
            if not new_scenario.add_constraints(constraint):
                continue  # TODO: test if it is really necessary to continue
            agent = constraint.get_agent()
            start_node = agent.get_start_node()
            target_node = agent.get_target_node()
            constraints_of_agent = []
            for new_scenario_constraint in new_scenario.constraints:
                if new_scenario_constraint.get_agent() == agent:
                    constraints_of_agent.append(new_scenario_constraint)

            new_path, _ = djikstra(
                graphe, start_node, target_node, constraints_of_agent
            )

            if len(new_path) > 0:
                new_scenario.change_path(agent, new_path)
                new_cost = 0
                for path in new_scenario.paths.values():
                    for i in range(len(path) - 1):
                        if path[i + 1] in path[i].successors:
                            new_cost += path[i].successors[path[i + 1]]
                        else:
                            new_cost += 1  # in this case, agent stays on its node
                new_scenario.change_cost(new_cost)
                new_scenario.detect_collisions()
                open_scenarios.append(new_scenario)
    return None


if __name__ == "__main__":
    G = {
        "C1": {"C2": 1},
        "C2": {"C3": 1, "C5": 1},
        "C3": {"C4": 1},
        "C4": {"C1": 1},
        "C5": {"C7": 1},
        "C6": {"C4": 1},
        "C7": {"C8": 1},
        "C8": {"C6": 1, "C9": 1},
        "C9": {"C7": 1},
    }
    graphe = Graphe(G)
    agent1 = Agent("ter", graphe.get_node_with_id("C7"), graphe.get_node_with_id("C8"))
    agent2 = Agent("tgv", graphe.get_node_with_id("C5"), graphe.get_node_with_id("C6"))
    scenario = CBS(graphe, [agent1, agent2])
    dic = {}
    for agent, path in scenario.paths.items():
        dic[agent.id] = [node.id for node in path]

    print(dic)
    print(scenario.cost)

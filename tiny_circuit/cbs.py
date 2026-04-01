from __future__ import annotations

from enum import Enum, auto

# Cost applied when an agent remains on the same node for one timestep.
WAITING_COST = 1


class CollisionType(Enum):
    """Types of collisions handled by the CBS solver."""

    EDGE_COLLISION = auto()
    NODE_COLLISION = auto()


class Collision:
    """Represents a conflict between two agents at a given time."""

    def __init__(self, type: CollisionType) -> None:
        """Initializes an empty collision.

        Args:
            type: Collision type (node or edge).
        """
        self.type = type
        self.nodes = []
        self.agents = []

    def add_node_collision(self, node: Node, agents: list[Agent], time: int):
        """Configures this object as a node collision.

        Args:
            node: Node shared by the colliding agents.
            agents: Agents involved in the collision.
            time: Simulation time of the collision.
        """
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
        """Configures this object as an edge-swap collision.

        Args:
            nodes: The two nodes involved in the opposite swap.
            agents: Agents involved in the collision.
            time: Simulation time of the collision.
        """
        for node in nodes:
            self.nodes.append(node)
        for agent in agents:
            self.agents.append(agent)
        self.time = time

    def get_nodes(self) -> list[Node]:
        """Returns the nodes involved in the collision.

        Returns:
            The list of nodes registered in this collision.
        """
        return self.nodes

    def get_agents(self) -> list[Agent]:
        """Returns the agents involved in the collision.

        Returns:
            The list of agents registered in this collision.
        """
        return self.agents

    def get_time(self) -> int:
        """Returns the collision timestamp.

        Returns:
            The discrete time associated with the collision.
        """
        return self.time


class ConstraintType(Enum):
    """Types of constraints produced from collisions."""

    NODE_CONSTRAINT = auto()
    EDGE_CONSTRAINT = auto()


class Constraint:
    """A temporal restriction applied to one agent."""

    def __init__(
        self,
        agent: Agent,
        type: ConstraintType,
        nodes: list[Node],
        time: int,
    ) -> None:
        """Initializes a temporal constraint for one agent.

        Args:
            agent: Agent targeted by the constraint.
            type: Constraint type (node or edge).
            nodes: Node(s) covered by this constraint.
            time: Discrete time at which the constraint applies.
        """
        self.agent = agent
        self.type = type
        self.nodes = nodes
        self.time = time

    def __eq__(self, other: object) -> bool:
        """Compares two constraints by value.

        Args:
            other: Object to compare against.

        Returns:
            True if constraints are equivalent, otherwise False.
        """
        if not isinstance(other, Constraint):
            return False
        return (
            self.agent == other.agent
            and self.type == other.type
            and self.nodes == other.nodes
            and self.time == other.time
        )

    def get_agent(self) -> Agent:
        """Returns the constrained agent.

        Returns:
            The agent targeted by the constraint.
        """
        return self.agent

    def forbids(self, current_node: Node, next_node: Node, next_time: int) -> bool:
        """Checks whether a transition is forbidden by the constraint.

        Args:
            current_node: Source node of the transition.
            next_node: Destination node of the transition.
            next_time: Arrival time at destination node.

        Returns:
            True if the transition is forbidden, otherwise False.
        """
        if self.type == ConstraintType.NODE_CONSTRAINT:
            return self.nodes[0] == next_node and self.time == next_time
        return (
            self.nodes[0] == current_node
            and self.nodes[1] == next_node
            and self.time == next_time - 1
        )

    def get_time(self) -> int:
        """Returns the constraint timestamp.

        Returns:
            The constraint discrete time.
        """
        return self.time


class Node:
    """Graph node with weighted successors."""

    def __init__(self, id: str) -> None:
        """Initializes a graph node.

        Args:
            id: Unique node identifier.
        """
        self.id = id
        self.is_occupied: bool = False

    def add_successors(self, weight_by_successor_node: dict[Node, int]):
        """Sets successor nodes and transition costs.

        Args:
            weight_by_successor_node: Mapping successor -> traversal cost.
        """
        self.weight_by_successor_node = weight_by_successor_node

    def get_id(self) -> str:
        """Returns the node identifier.

        Returns:
            Node identifier.
        """
        return self.id

    def get_weight_by_successor_node(self):
        """Returns the weighted successor mapping for this node.

        Returns:
            Mapping of successors to traversal costs.
        """
        return self.weight_by_successor_node


class Graphe:
    """Directed weighted graph wrapper used by routing algorithms."""

    def __init__(self, adjacency_matrix: dict[str, dict[str, int]]) -> None:
        """Builds a weighted directed graph from an adjacency mapping.

        Args:
            adjacency_matrix: Mapping `node -> {successor: cost}`.
        """
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
        """Returns a node from its identifier.

        Args:
            node_id: Identifier of the requested node.

        Returns:
            The matching node.
        """
        return self.node_by_id[node_id]

    def get_nodes(self) -> list[Node]:
        """Returns all graph nodes.

        Returns:
            List of nodes.
        """
        return self.nodes


class Agent:
    """Agent definition with start and target nodes."""

    def __init__(self, id: str, start_node: Node, target_node: Node) -> None:
        """Initializes an agent with a start and a target node.

        Args:
            id: Agent identifier.
            start_node: Start node.
            target_node: Target node.
        """
        self.id = id
        self.start_node = start_node
        self.current_node = start_node
        self.target_node = target_node

    def get_id(self) -> str:
        """Returns the agent identifier.

        Returns:
            Agent identifier.
        """
        return self.id

    def get_start_node(self) -> Node:
        """Returns the start node.

        Returns:
            Start node.
        """
        return self.start_node

    def get_target_node(self) -> Node:
        """Returns the target node.

        Returns:
            Target node.
        """
        return self.target_node


class Scenario:
    """CBS search node containing paths, constraints, and detected collisions."""

    def __init__(self) -> None:
        """Initializes an empty CBS scenario."""
        self.constraints = []
        self.collisions = []
        self.cost = 0
        self.path_by_agent = {}

    def route(self, graphe: Graphe, agents: list[Agent]):
        """Computes initial unconstrained shortest paths for all agents.

        Args:
            graphe: Movement graph.
            agents: Agents to route.

        Raises:
            Exception: If at least one agent cannot be routed.
        """
        self.cost = 0
        for agent in agents:
            self.path_by_agent[agent], cost = djikstra(
                graphe, agent.start_node, agent.target_node
            )
            if cost == -1:
                raise Exception("Routing is impossible")
            self.cost += cost

    def get_agents(self) -> list[Agent]:
        """Returns agents present in the scenario.

        Returns:
            List of agents that have an associated path.
        """
        return list(self.path_by_agent.keys())

    def get_paths(self) -> list[list[Node]]:
        """Returns all scenario paths.

        Returns:
            List of paths, one per agent.
        """
        return list(self.path_by_agent.values())

    def get_cost(self) -> int:
        """Returns the total scenario cost.

        Returns:
            Aggregated path cost.
        """
        return self.cost

    def detect_collisions(self):
        """Refreshes the complete list of collisions.

        Returns:
            None.
        """
        self.collisions = []
        self.detect_node_collisions()
        self.detect_edge_collisions()

    def detect_node_collisions(self) -> None:
        """Detects node collisions.

        A node collision occurs when two agents occupy the same node at the
        same time, including while waiting.
        """
        paths = self.get_paths().copy()
        agents = self.get_agents().copy()
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                max_time = max(len(paths[i]), len(paths[j]))
                for t in range(max_time):
                    if t < len(paths[i]):
                        node_i = paths[i][t]
                    else:
                        node_i = paths[i][-1]
                    if t < len(paths[j]):
                        node_j = paths[j][t]
                    else:
                        node_j = paths[j][-1]
                    if node_i == node_j:
                        collision = Collision(CollisionType.NODE_COLLISION)
                        collision.add_node_collision(node_i, [agents[i], agents[j]], t)
                        self.collisions.append(collision)

    def detect_edge_collisions(self) -> None:
        """Detects edge-swap collisions between pairs of agents."""
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
        """Adds a constraint to the scenario if it is not already present.

        Args:
            constraints: Constraint to add.

        Returns:
            True if the constraint was added, otherwise False.
        """
        if constraints in self.constraints:
            return False
        self.constraints.append(constraints)
        return True

    def copy_paths_cost_constraints(self, scenario: Scenario):
        """Copies paths, cost, and constraints from another scenario.

        Args:
            scenario: Source scenario to copy.
        """
        new_paths = {}
        for agent, path in scenario.path_by_agent.items():
            new_paths[agent] = path.copy()
        self.path_by_agent = new_paths
        self.cost = scenario.cost
        self.constraints = scenario.constraints.copy()

    def change_path(self, agent: Agent, path: list[Node]):
        """Replaces the path of one agent.

        Args:
            agent: Agent to update.
            path: New path for the agent.
        """
        self.path_by_agent[agent] = path

    def change_cost(self, cost: int):
        """Updates the scenario total cost.

        Args:
            cost: New cost.
        """
        self.cost = cost

    def get_collisions(self):
        """Returns currently detected collisions.

        Returns:
            List of collisions.
        """
        return self.collisions

    def agent_to_constraints(self, agent: Agent) -> list[Constraint]:
        """Filters constraints applicable to one agent.

        Args:
            agent: Agent for which to retrieve constraints.

        Returns:
            List of constraints for this agent.
        """
        constraints_of_agent = []
        for constraint in self.constraints:
            if constraint.get_agent() == agent:
                constraints_of_agent.append(constraint)
        return constraints_of_agent

    def calculate_cost(self) -> int:
        """Recomputes the total cost across all scenario paths.

        Returns:
            Recomputed total cost.
        """
        self.cost = 0
        for path in self.path_by_agent.values():
            for i in range(len(path) - 1):
                if path[i + 1] in path[i].weight_by_successor_node:
                    self.cost += path[i].weight_by_successor_node[path[i + 1]]
                else:
                    self.cost += WAITING_COST
        return self.cost


def minimum_cost_scenario(scenarios: list[Scenario]) -> Scenario:
    """Returns the minimum-cost scenario.

    Args:
        scenarios: Non-empty list of candidate scenarios.

    Returns:
        Scenario with the lowest cost.
    """
    mini_scenario = scenarios[0]
    mini_cost = mini_scenario.get_cost()
    for scenario in scenarios:
        if scenario.get_cost() < mini_cost:
            mini_cost = scenario.get_cost()
            mini_scenario = scenario
    return mini_scenario


def standard_splitting(collision: Collision) -> list[Constraint]:
    """Builds the two standard CBS constraints for one collision.

    Args:
        collision: Collision to resolve.

    Returns:
        The two generated constraints (one per involved agent).
    """
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
    """Returns the state with the smallest distance among candidates.

    Args:
        distances: Current distance by state.
        chosen_states: Candidate states.

    Returns:
        Candidate state with minimal distance.
    """
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
    """Checks whether a transition satisfies all constraints.

    Args:
        current_node: Current node.
        successor_node: Candidate successor node.
        constraints: Constraints to apply.
        next_time: Transition time to successor node.

    Returns:
        True if the transition is allowed, otherwise False.
    """
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
    """Runs Dijkstra on a time-expanded state space with constraints.

    Args:
        graphe: Movement graph.
        start_node: Start node.
        target_node: Target node.
        constraints: Temporal constraints to satisfy.

    Returns:
        A tuple `(path, cost)` where `path` is the found path and `cost` is
        its cumulative cost. If no path is found, returns `([], -1)`.
    """

    max_constraint_time = max(
        [constraint.get_time() for constraint in constraints] + [0]
    )
    max_time = max_constraint_time + len(graphe.get_nodes())

    not_visited_states = [(start_node, 0)]
    predecessors = {(start_node, 0): (start_node, 0)}
    distances = {(start_node, 0): 0}
    visited_states = []
    while len(not_visited_states) > 0:
        mini_state = minimum_with_chosen_states(distances, not_visited_states)
        not_visited_states.remove(mini_state)
        visited_states.append(mini_state)
        current_node, current_time = mini_state

        if current_node == target_node and current_time >= max_constraint_time:
            break
        if current_time >= max_time:
            continue

        candidate_successors = current_node.get_weight_by_successor_node().copy()
        candidate_successors[current_node] = WAITING_COST
        next_time = current_time + 1

        for successor_node, successor_weight in candidate_successors.items():
            if not is_successor_node_possible_with_constraints(
                current_node, successor_node, constraints, next_time
            ):
                continue

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
    """Solves multi-agent routing with Conflict-Based Search.

    Args:
        graphe: Movement graph.
        agents: Agents to route.

    Returns:
        A collision-free scenario.

    Raises:
        Exception: If no collision-free routing is possible.
    """
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

from __future__ import annotations

from enum import Enum, auto

# Cost applied when an train remains on the same canton for one timestep.
WAITING_COST = 1


class CollisionType(Enum):
    """Types of collisions handled by the CBS solver."""

    EDGE_COLLISION = auto()
    CANTON_COLLISION = auto()


class Collision:
    """Represents a conflict between two trains at a given time."""

    def __init__(self, collision_type: CollisionType) -> None:
        """Initializes an empty collision.

        Args:
            `collision_type`: Collision type (canton or edge).
        """
        self.collision_type = collision_type
        self.cantons = []
        self.trains = []

    def add_canton_collision(self, canton: Canton, trains: list[Train], time: int):
        """Configures this object as a canton collision.

        Args:
            `canton`: Canton shared by the colliding trains.
            `trains`: Trains involved in the collision.
            `time`: Simulation time of the collision.
        """
        self.cantons.append(canton)
        for train in trains:
            self.trains.append(train)
        self.time = time

    def add_edge_collision(
        self,
        cantons: list[Canton],
        trains: list[Train],
        time: int,
    ):
        """Configures this object as an edge-swap collision.

        Args:
            `cantons`: The two cantons involved in the opposite swap.
            `trains`: Trains involved in the collision.
            `time`: Simulation time of the collision.
        """
        for canton in cantons:
            self.cantons.append(canton)
        for train in trains:
            self.trains.append(train)
        self.time = time

    def get_cantons(self) -> list[Canton]:
        """Returns the cantons involved in the collision.

        Returns:
            The list of cantons registered in this collision.
        """
        return self.cantons

    def get_trains(self) -> list[Train]:
        """Returns the trains involved in the collision.

        Returns:
            The list of trains registered in this collision.
        """
        return self.trains

    def get_time(self) -> int:
        """Returns the collision timestamp.

        Returns:
            The discrete time associated with the collision.
        """
        return self.time


class ConstraintType(Enum):
    """Types of constraints produced from collisions."""

    CANTON_CONSTRAINT = auto()
    EDGE_CONSTRAINT = auto()


class Constraint:
    """A temporal restriction applied to one train."""

    def __init__(
        self,
        train: Train,
        constraint_type: ConstraintType,
        cantons: list[Canton],
        time: int,
    ) -> None:
        """Initializes a temporal constraint for one train.

        Args:
            train: Train targeted by the constraint.
            constraint_type: Constraint type (canton or edge).
            cantons: Canton(s) covered by this constraint.
            time: Discrete time at which the constraint applies.
        """
        self.train = train
        self.constraint_type = constraint_type
        self.cantons = cantons
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
            self.train == other.train
            and self.constraint_type == other.constraint_type
            and self.cantons == other.cantons
            and self.time == other.time
        )

    def get_train(self) -> Train:
        """Returns the constrained train.

        Returns:
            The train targeted by the constraint.
        """
        return self.train

    def forbids(
        self, current_canton: Canton, next_canton: Canton, next_time: int
    ) -> bool:
        """Checks whether a transition is forbidden by the constraint.

        Args:
            `current_canton`: Source canton of the transition.
            `next_canton`: Destination canton of the transition.
            `next_time`: Arrival time at destination canton.

        Returns:
            True if the transition is forbidden, otherwise False.
        """
        if self.constraint_type == ConstraintType.CANTON_CONSTRAINT:
            return self.cantons[0] == next_canton and self.time == next_time
        return (
            self.cantons[0] == current_canton
            and self.cantons[1] == next_canton
            and self.time == next_time - 1
        )

    def get_time(self) -> int:
        """Returns the constraint timestamp.

        Returns:
            The constraint discrete time.
        """
        return self.time


class Canton:
    """Circuit canton with weighted successors."""

    def __init__(self, canton_id: str) -> None:
        """Initializes a circuit canton.

        Args:
            `canton_id`: Unique canton identifier.
        """
        self.canton_id = canton_id
        self.is_occupied: bool = False

    def add_successors(self, weight_by_successor_canton: dict[Canton, int]):
        """Sets successor cantons and transition costs.

        Args:
            `weight_by_successor_canton`: Mapping successor -> traversal cost.
        """
        self.weight_by_successor_canton = weight_by_successor_canton

    def get_id(self) -> str:
        """Returns the canton identifier.

        Returns:
            Canton identifier.
        """
        return self.canton_id

    def get_weight_by_successor_canton(self) -> dict[Canton, int]:
        """Returns the weighted successor mapping for this canton.

        Returns:
            Mapping of successors to traversal costs.
        """
        return self.weight_by_successor_canton


class Circuit:
    """Directed weighted circuit wrapper used by routing algorithms."""

    def __init__(self, adjacency_matrix: dict[str, dict[str, int]]) -> None:
        """Builds a weighted directed circuit from an adjacency mapping.

        Args:
            `adjacency_matrix`: Mapping `canton -> {successor: cost}`.
        """
        self.cantons = []
        self.canton_by_id = {}
        for canton_id in adjacency_matrix:
            canton = Canton(canton_id)
            self.cantons.append(canton)
            self.canton_by_id[canton_id] = canton

        for canton_id, weight_by_successor_canton_id in adjacency_matrix.items():
            successors_canton_by_id = {}
            for (
                successor_canton_id,
                successor_weight,
            ) in weight_by_successor_canton_id.items():
                successors_canton_by_id[self.canton_by_id[successor_canton_id]] = (
                    successor_weight
                )
            self.canton_by_id[canton_id].add_successors(successors_canton_by_id)

    def get_canton_with_id(self, canton_id: str) -> Canton:
        """Returns a canton from its identifier.

        Args:
            `canton_id`: Identifier of the requested canton.

        Returns:
            The matching canton.
        """
        return self.canton_by_id[canton_id]

    def get_cantons(self) -> list[Canton]:
        """Returns all circuit cantons.

        Returns:
            List of cantons.
        """
        return self.cantons


class Train:
    """Train definition with start and target cantons."""

    def __init__(
        self,
        train_id: str,
        start_canton: Canton,
        target_canton: Canton,
        start_time: int = 0,
    ) -> None:
        """Initializes an train with a start and a target canton.

        Args:
            `train_id`: Train identifier.
            `start_canton`: Start canton.
            `target_canton`: Target canton.
        """
        self.train_id = train_id
        self.start_canton = start_canton
        self.start_time = start_time
        self.current_canton = start_canton
        self.target_canton = target_canton

    def get_id(self) -> str:
        """Returns the train identifier.

        Returns:
            Train identifier.
        """
        return self.train_id

    def get_start_canton(self) -> Canton:
        """Returns the start canton.

        Returns:
            Start canton.
        """
        return self.start_canton

    def get_target_canton(self) -> Canton:
        """Returns the target canton.

        Returns:
            Target canton.
        """
        return self.target_canton


class Scenario:
    """CBS search canton containing paths, constraints, and detected collisions."""

    def __init__(self) -> None:
        """Initializes an empty CBS scenario."""
        self.constraints = []
        self.collisions = []
        self.cost = 0
        self.paths_by_train = {}

    def route(self, circuit: Circuit, trains: list[Train]) -> None:
        """Computes initial unconstrained shortest paths for all trains.

        Args:
            `circuit`: Movement circuit.
            `trains`: Trains to route.

        Raises:
            Exception: If at least one train cannot be routed.
        """
        self.cost = 0
        for train in trains:
            self.paths_by_train[train], cost = dijkstra(
                circuit, train.start_canton, train.target_canton
            )
            if cost == -1:
                raise Exception("Routing is impossible")
            self.cost += cost

    def get_trains(self) -> list[Train]:
        """Returns trains present in the scenario.

        Returns:
            List of trains that have an associated path.
        """
        return list(self.paths_by_train.keys())

    def get_paths(self) -> list[list[Canton]]:
        """Returns all scenario paths.

        Returns:
            List of paths, one per train.
        """
        return list(self.paths_by_train.values())

    def get_cost(self) -> int:
        """Returns the total scenario cost.

        Returns:
            Aggregated path cost.
        """
        return self.cost

    def detect_collisions(self) -> None:
        """Refreshes the complete list of collisions."""
        self.collisions = []
        self.detect_canton_collisions()
        self.detect_edge_collisions()

    def detect_canton_collisions(self) -> None:
        """Detects canton collisions.

        A canton collision occurs when two trains occupy the same canton at the
        same time, including while waiting.
        """
        train_paths = self.get_paths().copy()
        scenario_trains = self.get_trains().copy()
        for first_train_index in range(len(train_paths)):
            for second_train_index in range(first_train_index + 1, len(train_paths)):
                max_time = max(
                    len(train_paths[first_train_index]),
                    len(train_paths[second_train_index]),
                )
                for time in range(max_time):
                    if time < len(train_paths[first_train_index]):
                        first_train_canton = train_paths[first_train_index][time]
                    else:
                        first_train_canton = train_paths[first_train_index][-1]
                    if time < len(train_paths[second_train_index]):
                        second_train_canton = train_paths[second_train_index][time]
                    else:
                        second_train_canton = train_paths[second_train_index][-1]
                    if first_train_canton == second_train_canton:
                        collision = Collision(CollisionType.CANTON_COLLISION)
                        collision.add_canton_collision(
                            first_train_canton,
                            [
                                scenario_trains[first_train_index],
                                scenario_trains[second_train_index],
                            ],
                            time,
                        )
                        self.collisions.append(collision)

    def detect_edge_collisions(self) -> None:
        """Detects edge-swap collisions between pairs of trains."""
        train_paths = self.get_paths().copy()
        scenario_trains = self.get_trains().copy()
        for first_train_index in range(len(train_paths)):
            for second_train_index in range(
                first_train_index + 1,
                len(train_paths),
            ):
                for time in range(len(train_paths[first_train_index]) - 1):
                    if time + 1 <= len(train_paths[second_train_index]) - 1:
                        first_train_current_canton = train_paths[first_train_index][
                            time
                        ]
                        first_train_next_canton = train_paths[first_train_index][
                            time + 1
                        ]
                        second_train_current_canton = train_paths[second_train_index][
                            time
                        ]
                        second_train_next_canton = train_paths[second_train_index][
                            time + 1
                        ]
                        if (
                            first_train_current_canton == second_train_next_canton
                            and first_train_next_canton == second_train_current_canton
                        ):
                            collision = Collision(CollisionType.EDGE_COLLISION)
                            collision.add_edge_collision(
                                [
                                    first_train_current_canton,
                                    second_train_current_canton,
                                ],
                                [
                                    scenario_trains[first_train_index],
                                    scenario_trains[second_train_index],
                                ],
                                time,
                            )
                            self.collisions.append(collision)

    def add_constraints(self, constraint: Constraint) -> bool:
        """Adds a constraint to the scenario if it is not already present.

        Args:
            `constraint`: Constraint to add.

        Returns:
            True if the constraint was added, otherwise False.
        """
        if constraint in self.constraints:
            return False
        self.constraints.append(constraint)
        return True

    def copy_paths_cost_and_constraints(self, scenario: Scenario):
        """Copies paths, cost, and constraints from another scenario.

        Args:
            `scenario`: Source scenario to copy.
        """
        new_paths = {}
        for train, path in scenario.paths_by_train.items():
            new_paths[train] = path.copy()
        self.paths_by_train = new_paths
        self.cost = scenario.cost
        self.constraints = scenario.constraints.copy()

    def change_path(self, train: Train, path: list[Canton]):
        """Replaces the path of one train.

        Args:
            `train`: Train to update.
            `path`: New path for the train.
        """
        self.paths_by_train[train] = path

    def change_cost(self, cost: int):
        """Updates the scenario total cost.

        Args:
            `cost`: New cost.
        """
        self.cost = cost

    def get_collisions(self):
        """Returns currently detected collisions.

        Returns:
            List of collisions.
        """
        return self.collisions

    def get_constraints_for_train(self, train: Train) -> list[Constraint]:
        """Filters constraints applicable to one train.

        Args:
            `train`: Train for which to retrieve constraints.

        Returns:
            List of constraints for this train.
        """
        constraints_of_train = []
        for constraint in self.constraints:
            if constraint.get_train() == train:
                constraints_of_train.append(constraint)
        return constraints_of_train

    def calculate_cost(self) -> int:
        """Recomputes the total cost across all scenario paths.

        Returns:
            Recomputed total cost.
        """
        self.cost = 0
        for path in self.paths_by_train.values():
            for i in range(len(path) - 1):
                if path[i + 1] in path[i].weight_by_successor_canton:
                    self.cost += path[i].weight_by_successor_canton[path[i + 1]]
                else:
                    self.cost += WAITING_COST
        return self.cost


def select_minimum_cost_scenario(scenarios: list[Scenario]) -> Scenario:
    """Returns the minimum-cost scenario.

    Args:
        `scenarios`: Non-empty list of candidate scenarios.

    Returns:
        Scenario with the lowest cost.
    """
    best_scenario = scenarios[0]
    best_cost = best_scenario.get_cost()
    for scenario in scenarios:
        if scenario.get_cost() < best_cost:
            best_cost = scenario.get_cost()
            best_scenario = scenario
    return best_scenario


def build_standard_constraints(collision: Collision) -> list[Constraint]:
    """Builds the two standard CBS constraints for one collision.

    Args:
        `collision`: Collision to resolve.

    Returns:
        The two generated constraints (one per involved train).
    """
    if collision.collision_type == CollisionType.CANTON_COLLISION:
        train_1, train_2 = collision.get_trains()
        canton = collision.get_cantons()[0]
        time = collision.get_time()
        return [
            Constraint(train_1, ConstraintType.CANTON_CONSTRAINT, [canton], time),
            Constraint(train_2, ConstraintType.CANTON_CONSTRAINT, [canton], time),
        ]

    train_1, train_2 = collision.get_trains()
    canton_1, canton_2 = collision.get_cantons()
    time = collision.time
    return [
        Constraint(
            train_1,
            ConstraintType.EDGE_CONSTRAINT,
            [canton_1, canton_2],
            time,
        ),
        Constraint(
            train_2,
            ConstraintType.EDGE_CONSTRAINT,
            [canton_2, canton_1],
            time,
        ),
    ]


def get_minimum_distance_state(
    distances: dict[tuple[Canton, int], int], candidate_states: list[tuple[Canton, int]]
) -> tuple[Canton, int]:
    """Returns the state with the smallest distance among candidates.

    Args:
        `distances`: Current distance by state.
        `candidate_states`: Candidate states.

    Returns:
        Candidate state with minimal distance.
    """
    best_state = candidate_states[0]
    best_distance = distances[best_state]
    for candidate_state in candidate_states:
        if distances[candidate_state] < best_distance:
            best_state = candidate_state
            best_distance = distances[candidate_state]
    return best_state


def is_transition_allowed_by_constraints(
    current_canton: Canton,
    next_canton: Canton,
    constraints: list[Constraint],
    next_time: int,
) -> bool:
    """Checks whether a transition satisfies all constraints.

    Args:
        `current_canton`: Current canton.
        `next_canton`: Candidate successor canton.
        `constraints`: Constraints to apply.
        `next_time`: Transition time to successor canton.

    Returns:
        True if the transition is allowed, otherwise False.
    """
    for constraint in constraints:
        if constraint.forbids(current_canton, next_canton, next_time):
            return False
    return True


def dijkstra(
    circuit: Circuit,
    start_canton: Canton,
    target_canton: Canton,
    constraints: list[Constraint] = [],
) -> tuple[list[Canton], int]:
    """Runs Dijkstra on a time-expanded state space with constraints.

    Args:
        `circuit`: Movement circuit.
        `start_canton`: Start canton.
        `target_canton`: Target canton.
        `constraints`: Temporal constraints to satisfy.

    Returns:
        A tuple `(path, cost)` where `path` is the found path and `cost` is
        its cumulative cost. If no path is found, returns `([], -1)`.
    """

    max_constraint_time = max(
        [constraint.get_time() for constraint in constraints] + [0]
    )
    max_time = max_constraint_time + len(circuit.get_cantons())

    not_visited_states = [(start_canton, 0)]
    predecessors = {(start_canton, 0): (start_canton, 0)}
    distances = {(start_canton, 0): 0}
    visited_states = []
    while len(not_visited_states) > 0:
        current_state = get_minimum_distance_state(distances, not_visited_states)
        not_visited_states.remove(current_state)
        visited_states.append(current_state)
        current_canton, current_time = current_state

        if current_canton == target_canton and current_time >= max_constraint_time:
            break
        if current_time >= max_time:
            continue

        candidate_successors = current_canton.get_weight_by_successor_canton().copy()
        candidate_successors[current_canton] = WAITING_COST
        next_time = current_time + 1

        for next_canton, transition_cost in candidate_successors.items():
            if not is_transition_allowed_by_constraints(
                current_canton, next_canton, constraints, next_time
            ):
                continue

            successor_state = (next_canton, next_time)
            new_distance = distances[current_state] + transition_cost
            if (
                successor_state not in distances
                or distances[successor_state] > new_distance
            ):
                predecessors[successor_state] = current_state
                distances[successor_state] = new_distance
                if successor_state not in not_visited_states:
                    not_visited_states.append(successor_state)
    target_state = None
    best_distance = float("inf")
    for state in visited_states:
        canton, time = state
        if (
            canton == target_canton
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
    while state != (start_canton, 0):
        state = predecessors[state]
        result.append(state[0])
    return result[::-1], distances[target_state]


def run_cbs(circuit: Circuit, trains: list[Train]) -> Scenario:
    """Solves multi-train routing with Conflict-Based Search.

    Args:
        `circuit`: Movement circuit.
        `trains`: Trains to route.

    Returns:
        A collision-free scenario.

    Raises:
        Exception: If no collision-free routing is possible.
    """
    open_scenarios = []
    scenario = Scenario()
    scenario.route(circuit, trains)
    scenario.detect_collisions()
    open_scenarios.append(scenario)

    while len(open_scenarios) > 0:
        scenario = select_minimum_cost_scenario(open_scenarios)
        open_scenarios.remove(scenario)

        if len(scenario.get_collisions()) == 0:
            return scenario

        collision = scenario.get_collisions()[0]
        constraints_list = build_standard_constraints(collision)

        for constraint in constraints_list:
            new_scenario = Scenario()
            new_scenario.copy_paths_cost_and_constraints(scenario)
            if not new_scenario.add_constraints(constraint):
                continue
            train = constraint.get_train()
            start_canton = train.get_start_canton()
            target_canton = train.get_target_canton()

            constraints_of_train = new_scenario.get_constraints_for_train(train)

            new_path, _ = dijkstra(
                circuit, start_canton, target_canton, constraints_of_train
            )

            if len(new_path) > 0:
                new_scenario.change_path(train, new_path)
                new_scenario.calculate_cost()
                new_scenario.detect_collisions()
                open_scenarios.append(new_scenario)
    raise Exception("No collision-free routing is possible")

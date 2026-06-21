import unittest

from cbs import CBS, Agent, Graphe

DATASETS = [
    {
        "name": "single_agent_shortest_path",
        "graph": {
            "A": {"B": 1},
            "B": {"C": 1},
            "C": {},
        },
        "agents": [
            {"id": "train_1", "start": "A", "target": "C"},
        ],
        "expected_cost": 2,
    },
    {
        "name": "node_collision_intersection",
        "graph": {
            "N": {"M": 1},
            "S": {"M": 1},
            "M": {"E": 1, "W": 1},
            "E": {},
            "W": {},
        },
        "agents": [
            {"id": "train_north", "start": "N", "target": "E"},
            {"id": "train_south", "start": "S", "target": "W"},
        ],
        "expected_cost": 5,
    },
    {
        "name": "two_agents_no_conflict",
        "graph": {
            "A1": {"A2": 1},
            "A2": {},
            "B1": {"B2": 1},
            "B2": {},
        },
        "agents": [
            {"id": "train_a", "start": "A1", "target": "A2"},
            {"id": "train_b", "start": "B1", "target": "B2"},
        ],
        "expected_cost": 2,
    },
    {
        "name": "detour_vs_waiting_reference",
        "graph": {
            "C1": {"C2": 1},
            "C2": {"C3": 1, "C5": 1},
            "C3": {"C4": 1},
            "C4": {"C1": 1},
            "C5": {"C7": 1},
            "C6": {"C4": 1},
            "C7": {"C8": 1},
            "C8": {"C6": 1, "C9": 1},
            "C9": {"C7": 1},
        },
        "agents": [
            {"id": "ter", "start": "C7", "target": "C8"},
            {"id": "tgv", "start": "C5", "target": "C6"},
        ],
        "expected_cost": 7,
    },
]


class TestCBS(unittest.TestCase):
    def _run_dataset(self, dataset):
        graph = Graphe(dataset["graph"])
        agents = [
            Agent(
                item["id"],
                graph.get_node_with_id(item["start"]),
                graph.get_node_with_id(item["target"]),
            )
            for item in dataset["agents"]
        ]
        scenario = CBS(graph, agents)
        self.assertIsNotNone(scenario, f"Aucune solution CBS pour {dataset['name']}")

        scenario.detect_collisions()
        self.assertEqual(
            len(scenario.get_collisions()),
            0,
            f"Des collisions persistent dans {dataset['name']}",
        )

        result_paths = {
            agent.id: [node.id for node in path]
            for agent, path in scenario.path_by_agent.items()
        }

        for agent in agents:
            self.assertEqual(
                result_paths[agent.id][-1],
                agent.target_node.id,
                f"L'agent {agent.id} n'atteint pas sa cible dans {dataset['name']}",
            )

        return scenario, result_paths

    def test_single_agent_shortest_path(self):
        dataset = DATASETS[0]
        scenario, _ = self._run_dataset(dataset)
        self.assertEqual(scenario.cost, dataset["expected_cost"])

    def test_node_collision_intersection(self):
        dataset = DATASETS[1]
        scenario, _ = self._run_dataset(dataset)
        self.assertEqual(scenario.cost, dataset["expected_cost"])

    def test_two_agents_no_conflict(self):
        dataset = DATASETS[2]
        scenario, paths = self._run_dataset(dataset)
        self.assertEqual(scenario.cost, dataset["expected_cost"])
        self.assertIn("train_a", paths)
        self.assertIn("train_b", paths)

    def test_detour_vs_waiting(self):
        dataset = DATASETS[3]
        scenario, paths = self._run_dataset(dataset)
        self.assertEqual(scenario.cost, dataset["expected_cost"])
        self.assertIn("ter", paths)
        self.assertIn("tgv", paths)


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
    agent_1 = Agent("ter", graphe.get_node_with_id("C7"), graphe.get_node_with_id("C8"))
    agent_2 = Agent("tgv", graphe.get_node_with_id("C5"), graphe.get_node_with_id("C6"))
    scenario = CBS(graphe, [agent_1, agent_2])
    dic = {}
    for agent, path in scenario.path_by_agent.items():
        dic[agent.id] = [node.id for node in path]

    print(dic)
    print(scenario.cost)

    unittest.main()

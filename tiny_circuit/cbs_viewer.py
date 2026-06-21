import matplotlib.pyplot as plt
import networkx as nx
from cbs import Agent, Graph, run_cbs


def networkx_graph_to_common_graph(
    graph: dict[str, dict[str, dict[str, int]]],
) -> dict[str, dict[str, int]]:
    new_graph = {}
    for node_id, successors in graph.items():
        new_successors = {}
        for next_node_id, dict_cost in successors.items():
            new_successors[next_node_id] = dict_cost["weight"]
        new_graph[node_id] = new_successors
    return new_graph


def common_graph_to_networkx_graph(
    graph: dict[str, dict[str, int]],
) -> dict[str, dict[str, dict[str, int]]]:
    new_graph = {}
    for node_id, successors in graph.items():
        new_successors = {}
        for next_node_id, cost in successors.items():
            new_successors[next_node_id] = {"weight": 1}
        new_graph[node_id] = new_successors
    return new_graph


if __name__ == "__main__":
    G_common = {
        "C1": {"C2": {"weight": 1}},
        "C2": {"C3": {"weight": 1}, "C5": {"weight": 1}},
        "C3": {"C4": {"weight": 1}},
        "C4": {"C1": {"weight": 1}},
        "C5": {"C7": {"weight": 1}},
        "C6": {"C4": {"weight": 1}},
        "C7": {"C8": {"weight": 1}},
        "C8": {"C6": {"weight": 1}, "C9": {"weight": 1}},
        "C9": {"C7": {"weight": 1}},
    }
    plt.ion()
    G = nx.DiGraph(G_common)
    pos = nx.planar_layout(G)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx(G, pos, arrows=True)
    nx.draw_networkx_nodes(G, pos, node_color="grey")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)
    plt.axis("off")
    graph = Graph(networkx_graph_to_common_graph(G_common))
    agent_1 = Agent("1", graph.get_node_with_id("C1"), graph.get_node_with_id("C7"))
    agent_2 = Agent("2", graph.get_node_with_id("C3"), graph.get_node_with_id("C6"))
    scenario = run_cbs(graph, [agent_1, agent_2])

    max_time = 0
    for path in scenario.get_paths():
        if max_time < len(path):
            max_time = len(path)

    current_agent_1_node_id = agent_1.start_node.get_id()
    next_agent_1_node_id = current_agent_1_node_id
    current_agent_2_node_id = agent_2.start_node.get_id()
    nx.draw_networkx_nodes(
        G, pos, nodelist=[current_agent_1_node_id], node_color="tab:green"
    )
    next_agent_2_node_id = current_agent_2_node_id
    nx.draw_networkx_nodes(
        G, pos, nodelist=[current_agent_2_node_id], node_color="tab:blue"
    )
    for t in range(max_time - 1):
        agent_1_G_networkx = {}
        agent_2_G_networkx = {}
        if t < len(scenario.paths_by_agent[agent_1]) - 1:
            agent_1_nodes = [
                scenario.paths_by_agent[agent_1][t],
                scenario.paths_by_agent[agent_1][t + 1],
            ]
            agent_1_G_networkx = {
                agent_1_nodes[0].get_id(): {
                    agent_1_nodes[1].get_id(): {
                        "weight": agent_1_nodes[0].get_weight_by_successor_node()[
                            agent_1_nodes[1]
                        ]
                    }
                }
            }
            next_agent_1_node_id = agent_1_nodes[1].get_id()

        if t < len(scenario.paths_by_agent[agent_1]) - 1:
            agent_2_nodes = [
                scenario.paths_by_agent[agent_2][t],
                scenario.paths_by_agent[agent_2][t + 1],
            ]

            agent_2_G_networkx = {
                agent_2_nodes[0].get_id(): {
                    agent_2_nodes[1].get_id(): {
                        "weight": agent_2_nodes[0].get_weight_by_successor_node()[
                            agent_2_nodes[1]
                        ]
                    }
                }
            }
            next_agent_2_node_id = agent_2_nodes[1].get_id()

        if next_agent_1_node_id != current_agent_1_node_id:
            nx.draw_networkx_nodes(
                G, pos, nodelist=[current_agent_1_node_id], node_color="grey"
            )
            current_agent_1_node_id = next_agent_1_node_id
        if next_agent_2_node_id != current_agent_2_node_id:
            nx.draw_networkx_nodes(
                G, pos, nodelist=[current_agent_2_node_id], node_color="grey"
            )

            current_agent_2_node_id = next_agent_2_node_id

        nx.draw_networkx_nodes(
            G, pos, nodelist=[next_agent_1_node_id], node_color="tab:green"
        )
        nx.draw_networkx_nodes(
            G, pos, nodelist=[next_agent_2_node_id], node_color="tab:blue"
        )
        agent_1_G = nx.from_dict_of_dicts(agent_1_G_networkx)
        agent_2_G = nx.from_dict_of_dicts(agent_2_G_networkx)
        nx.draw_networkx_edges(agent_1_G, pos, edge_color="green")
        nx.draw_networkx_edges(agent_2_G, pos, edge_color="blue")
        plt.pause(2)
        nx.draw_networkx_edges(agent_2_G, pos, edge_color="black")
        nx.draw_networkx_edges(agent_1_G, pos, edge_color="black")

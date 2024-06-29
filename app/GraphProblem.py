import networkx as nx
from py_search.base import Problem, GoalNode, Node


class GraphProblem(Problem):
    def __init__(self, graph_vis):
        super().__init__(int(graph_vis.start_node), int(graph_vis.goal_node))  # Ensure nodes are integers
        self.G = graph_vis.G
        single_src_dijkstra_forward = nx.single_source_dijkstra_path_length(self.G, int(graph_vis.goal_node), weight='weight')
        self.H_f = rank_dict_by_values(single_src_dijkstra_forward)
        single_src_dijkstra_backward = nx.single_source_dijkstra_path_length(self.G, int(graph_vis.start_node), weight='weight')
        self.H_b = rank_dict_by_values(single_src_dijkstra_backward)

    def shortest_path_heuristic(self, node, forward):
        if forward:
            return self.H_f.get(node, float("inf"))
        else:
            return self.H_b[node]

    def node_value(self, node):
        if isinstance(node, GoalNode):
            return (node.cost() +
                    self.shortest_path_heuristic(node.state, forward=False))
        else:
            return (node.cost() +
                    self.shortest_path_heuristic(node.state, forward=True))

    def successors(self, node):
        """
        Computes successors of the given node in the graph.

        Yields Node objects representing each successor along with necessary
        information such as action taken, path cost, etc.

        :param node: Node identifier in the graph.
        :return: Generator yielding successors as Node objects.
        """
        if node.state in self.G.nodes():
            for neighbor in self.G.neighbors(node.state):
                action = f"{node} -> {neighbor}"
                path_cost = self.G[node.state][neighbor]["weight"]
                successor_node = Node(int(neighbor), node, action, node.cost() + path_cost)  # Ensure neighbor is integer
                yield successor_node
        else:
            raise ValueError(f"Node {node} is not present in the graph.")

    def predecessors(self, goal_node):
        """
        Computes predecessors of the given node in the graph.

        Yields Node objects representing each predecessor along with necessary
        information such as action taken, path cost, etc.
        :param goal_node: identifier in the graph.
        :return: Generator yielding predecessors as Node objects.
       """
        if goal_node.state in self.G.nodes():
            for neighbor in self.G.neighbors(goal_node.state):
                action = f"{neighbor} -> {goal_node}"
                path_cost = self.G[goal_node.state][neighbor]["weight"]
                successor_node = GoalNode(int(neighbor), goal_node, action, goal_node.cost() + path_cost)  # Ensure neighbor is integer
                yield successor_node
        else:
            raise ValueError(f"Node {goal_node} is not present in the graph.")


def rank_dict_by_values(input_dict):
    # Sort the dictionary by its values
    sorted_items = sorted(input_dict.items(), key=lambda item: item[1])

    # Initialize variables
    rank = 0
    last_value = None
    rank_dict = {}

    # Assign ranks
    for idx, (key, value) in enumerate(sorted_items):
        rank_dict[key] = rank
        if value != last_value:
            rank += 1
        last_value = value

    return rank_dict


import base64
import io
from matplotlib import pyplot as plt
import networkx as nx
import random

from app.GraphProblem import rank_dict_by_values


class GraphVisualization:
    def __init__(self):
        self.H_b = None
        self.H_f = None
        self.pos = {}
        self.edges = None
        self.start_node = 0
        self.goal_node = 0
        self.G = nx.Graph()

    def generate_random_graph(self, num_nodes):
        self.__init__()
        edges = []
        for i in range(num_nodes):
            weight = float(int(random.uniform(1, 10)))
            edges.append((i, i+1, weight))
            for j in range(i + 1, num_nodes):
                if random.random() < (1 / (num_nodes / 1.5)):
                    weight = float(int(random.uniform(1, 10)))
                    edges.append((i, j, weight))

        self.add_edges_and_nodes(nodes=range(num_nodes), edges=edges)

        # Find the two farthest nodes
        all_distances = {}
        for node in self.G.nodes():
            lengths = nx.multi_source_dijkstra_path_length(self.G, {node})
            for target, length in lengths.items():
                all_distances[(node, target)] = length
        farthest_pair = max(all_distances, key=all_distances.get)

        self.start_node, self.goal_node = farthest_pair

        # Calculate the shortest path lengths from each node to the start and goal nodes
        single_src_dijkstra_forward = nx.single_source_dijkstra_path_length(self.G, int(self.goal_node),
                                                                            weight='weight')
        self.H_f = rank_dict_by_values(single_src_dijkstra_forward)
        single_src_dijkstra_backward = nx.single_source_dijkstra_path_length(self.G, int(self.start_node),
                                                                             weight='weight')
        self.H_b = rank_dict_by_values(single_src_dijkstra_backward)
        self.pos = nx.spring_layout(self.G)

    def add_edges_and_nodes(self, nodes, edges):
        self.G = nx.Graph()
        self.edges = edges
        for n in nodes:
            self.G.add_node(n)
        for edge in edges:
            self.G.add_edge(int(edge[0]), int(edge[1]), weight=edge[2])  # Ensure nodes are integers

        for node in self.G.nodes():
            if node not in self.pos.keys():
                self.pos = nx.spring_layout(self.G)
                break

    def filter_graph(self, keep_nodes):
        """
        Filter the graph to keep only the specified nodes.

        :param keep_nodes: List of nodes to keep in the graph.
        """
        keep_edges = []
        for node in keep_nodes:
            for edge_str in node.path():
                i, j = map(int, edge_str.split(' -> '))
                keep_edges.append((i, j))
                keep_edges.append((j, i))

        # print(f"keep_edges: {keep_edges}")
        keep_nodes = [n.state for n in keep_nodes]
        filtered_G = self.G.subgraph(keep_nodes).copy()
        # print(f"Original edges in filtered_G: {list(filtered_G.edges())}")

        edges_to_remove = [(i, j) for (i, j) in list(filtered_G.edges()) if
                           (i, j) not in keep_edges and (j, i) not in keep_edges]
        # print(f"Edges to remove: {edges_to_remove}")

        filtered_G.remove_edges_from(edges_to_remove)
        # print(f"Filtered edges in filtered_G: {list(filtered_G.edges())}")

        return filtered_G

    def get_graph_image(self):
        """
        Get the base64 image of the graph.

        :return: Base64 string of the graph image.
        """
        # Draw the graph with highlighted start and goal nodes
        plt.cla()
        plt.figure()
        nx.draw(self.G, self.pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=150,
                font_size=16)
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=[int(self.start_node)], node_color='green',
                               node_size=300)
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=[int(self.goal_node)], node_color='red',
                               node_size=300)
        nx.draw_networkx_edge_labels(self.G, self.pos,
                                     edge_labels={(u, v): f'{d["weight"]:.0f}' for u, v, d in
                                                  self.G.edges(data=True)},
                                     font_color='black')

        # Annotate each node with H.f and H.b values
        for node in self.G.nodes():
            x, y = self.pos[node]
            x_offset = 0.1
            y_offset = 0.1
            hf_value = self.H_f.get(node, float('inf'))
            hb_value = self.H_b.get(node, float('inf'))
            plt.text(x + x_offset, y + y_offset, f'H.f = {hf_value}\nH.b = {hb_value}',
                     ha='center', va='center', fontsize=8, alpha=0.7,
                     bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.3'))

        iobytes = io.BytesIO()
        plt.savefig(iobytes, format='png')
        plt.close()
        iobytes.seek(0)
        return base64.b64encode(iobytes.read()).decode()

    def generate_combined_graph_image(self, fronted_graph, backed_graph, path_edges=None):
        plt.cla()  # Clear the current axes
        plt.clf()  # Clear the current figure
        plt.figure(figsize=(6, 6))  # Set the figure size

        # Get edge labels for fronted and backed graphs
        fronted_edge_labels = {(u, v): f'{d["weight"]:.0f}' for u, v, d in fronted_graph.edges(data=True)}
        backed_edge_labels = {(u, v): f'{d["weight"]:.0f}' for u, v, d in backed_graph.edges(data=True)}

        # Merge edge labels, prioritizing fronted graph labels
        edge_labels = {**fronted_edge_labels, **backed_edge_labels}

        if path_edges is not None:
            total_cost = 0.0
            total_front_nodes = len(fronted_graph.nodes)
            total_back_nodes = len(backed_graph.nodes)

            # Convert path_edges from strings to tuples
            path_edges_tuples = []
            for edge_str in path_edges:
                i, j = map(int, edge_str.split(' -> '))
                path_edges_tuples.append((i, j))
                path_edges_tuples.append((j, i))
                # Calculate total cost
                if (i, j) in fronted_edge_labels:
                    total_cost += float(fronted_edge_labels[(i, j)])
                elif (i, j) in backed_edge_labels:
                    total_cost += float(backed_edge_labels[(i, j)])
                elif (j, i) in fronted_edge_labels:
                    total_cost += float(fronted_edge_labels[(j, i)])
                elif (j, i) in backed_edge_labels:
                    total_cost += float(backed_edge_labels[(j, i)])

            # Draw fronted_graph without edges
            nx.draw_networkx_nodes(fronted_graph, self.pos, node_color='green', node_size=400)
            nx.draw_networkx_nodes(backed_graph, self.pos, node_color='red', node_size=200)

            # Draw node labels (node numbers)
            nx.draw_networkx_labels(fronted_graph, self.pos, font_size=8, font_color='white')
            nx.draw_networkx_labels(backed_graph, self.pos, font_size=8, font_color='white')

            # Highlight path edges in dark green
            path_edges_set = set(path_edges_tuples)
            edge_colors = ['lightgreen' if edge in path_edges_set else 'grey' for edge in edge_labels.keys()]
            nx.draw_networkx_edges(self.G, self.pos, edgelist=edge_labels.keys(), edge_color=edge_colors, width=2.0)

            # Add annotations for total cost and node counts
            plt.text(0.1, -0.1, f'Total Cost: {total_cost}', transform=plt.gca().transAxes, fontsize=12)
            plt.text(0.1, -0.15, f'Total Front Nodes: {total_front_nodes}', transform=plt.gca().transAxes, fontsize=12)
            plt.text(0.1, -0.2, f'Total Back Nodes: {total_back_nodes}', transform=plt.gca().transAxes, fontsize=12)

        else:
            # Draw fronted_graph with edges (default behavior)
            nx.draw(fronted_graph, self.pos, with_labels=True, node_color='green', node_size=400, font_size=16,
                    font_color='white')

            # Draw backed graph in red
            nx.draw(backed_graph, self.pos, with_labels=True, node_color='red', edge_color='black', node_size=400, font_size=16)

        # Draw edge labels
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=edge_labels, font_color='black')

        # Convert the plot to a base64 image
        iobytes = io.BytesIO()
        plt.savefig(iobytes, format='png', bbox_inches='tight')
        plt.close()
        iobytes.seek(0)
        return base64.b64encode(iobytes.read()).decode()

    @staticmethod
    def generate_text_image(messages):
        """
        Generate a base64 image of the provided text messages.

        :param messages: List of strings to be displayed.
        :return: Base64 string of the text image.
        """
        # Set up the figure and axis
        fig, ax = plt.subplots(figsize=(10, len(messages) * 0.5))
        ax.axis('off')  # Turn off the axis

        # Create a string with all the messages, separated by newlines
        text = "\n".join(messages)

        # Add the text to the plot
        ax.text(0, 1, text, ha='left', va='top', fontsize=20, wrap=True,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='white', boxstyle='round,pad=0.3'))

        # Adjust the layout to fit the text better
        plt.tight_layout()

        # Convert the plot to a base64 image
        iobytes = io.BytesIO()
        plt.savefig(iobytes, format='png', bbox_inches='tight')
        plt.close()
        iobytes.seek(0)
        return base64.b64encode(iobytes.read()).decode()

    def get_node_positions(self):
        """
        Get the positions of the nodes.
        """
        return self.pos


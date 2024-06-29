import base64
import pickle
import random

from flask import render_template, request, current_app as app, session, jsonify
import matplotlib

from app.GraphProblem import GraphProblem
from app.GraphVis import GraphVisualization

from py_search.base import Node
from py_search.informed import near_optimal_front_to_end_bidirectional_search

matplotlib.use('Agg')
import matplotlib.pyplot as plt


@app.route('/', methods=['GET', 'POST'])
def index():
    # Retrieve or create a new GraphVisualization object
    if 'graph_vis' not in session:
        graph_vis = GraphVisualization()
    else:
        try:
            graph_vis = pickle.loads(base64.b64decode(session['graph_vis']))
        except:
            graph_vis = GraphVisualization()  # If there's an error, create a new object

    if request.method == 'POST':
        node1_list = request.form.getlist('node1[]')
        node2_list = request.form.getlist('node2[]')
        weight_list = request.form.getlist('weight[]')
        graph_vis.start_node = int(request.form.get('start_node'))
        graph_vis.goal_node = int(request.form.get('goal_node'))

        edges = [(int(node1), int(node2), float(weight)) for node1, node2, weight in
                 zip(node1_list, node2_list, weight_list)]
        max_node = max(node1_list, key=int)
        graph_vis.add_edges_and_nodes(range(int(max_node)), edges)

    else:  # GET request, generate a random graph
        num_nodes = request.args.get('num_nodes', random.randint(10, 20), int)
        print(num_nodes)
        graph_vis.generate_random_graph(num_nodes - 1)

    graph_img = graph_vis.get_graph_image()
    plt.close()

    # Store the updated graph_vis object in the session
    session['graph_vis'] = base64.b64encode(pickle.dumps(graph_vis)).decode('utf-8')

    return render_template('index.html', graph_img=graph_img, edges=graph_vis.edges, start_node=graph_vis.start_node,
                           goal_node=graph_vis.goal_node)


@app.route('/generate_photos', methods=['POST'])
def generate_photos():
    global fronted_graph, backed_graph
    if 'graph_vis' not in session:
        return {'error': 'No graph found'}, 400

    try:
        graph_vis = pickle.loads(base64.b64decode(session['graph_vis']))
    except:
        return {'error': 'Invalid graph data'}, 400

    new_photos = []
    structured_messages = []  # List to store structured messages
    fronted_vertices = []
    backed_vertices = []

    problem = GraphProblem(graph_vis)
    path_edges = None

    for idx, node in enumerate(near_optimal_front_to_end_bidirectional_search(problem)):
        if isinstance(node, list):
            structured_message = [{'text': line[1:] if line.startswith("`") else line, 'is_title': line.startswith("`")} for idx, line in enumerate(node)]
            structured_messages.append(structured_message)

        elif isinstance(node, Node):
            if idx % 3 == 1:
                fronted_vertices.append(node)
            elif idx % 3 == 2:
                backed_vertices.append(node)

            fronted_graph = graph_vis.filter_graph(fronted_vertices)
            backed_graph = graph_vis.filter_graph(backed_vertices)
            combined_image = graph_vis.generate_combined_graph_image(fronted_graph, backed_graph)
            if idx % 3 == 2:
                new_photos.append(combined_image)

        else:
            path_edges = node.path()
            fronted_vertices.append(node.state_node)
            backed_vertices.append(node.goal_node)
            fronted_graph = graph_vis.filter_graph(fronted_vertices)
            backed_graph = graph_vis.filter_graph(backed_vertices)
            combined_image = graph_vis.generate_combined_graph_image(fronted_graph, backed_graph)
            new_photos.append(combined_image)
            break

    if path_edges:
        final_image = graph_vis.generate_combined_graph_image(fronted_graph, backed_graph, path_edges)
        new_photos.append(final_image)
        print(path_edges)
        structured_messages.append([{'text': f"path edges: {path_edges}", 'is_title': True}])
    else:
        return {'error': 'No route was found'}, 400

    session['graph_vis'] = base64.b64encode(pickle.dumps(graph_vis)).decode('utf-8')

    return {'photos': new_photos, 'messages': structured_messages}

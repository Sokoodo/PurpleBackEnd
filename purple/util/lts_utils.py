from typing import Set

import networkx as nx
from matplotlib import pyplot as plt
from pm4py.objects.petri_net.obj import Marking


def find_marking(lts: nx.DiGraph, transition_name: str) -> [Marking]:
    """
    Find the marking(s) in the LTS (Directed Graph) where a specific transition name is present.

    Parameters:
    - lts (nx.DiGraph): The LTS graph with markings as nodes and transitions as edge labels.
    - transition_name (str): The name of the transition whose marking we want to find.

    Returns:
    - List[Marking]: A list of markings where the given transition name is present.
    The source marking of the given transition name is also returned.
    """
    ret = []

    # Iterate over all edges in the graph
    for u, v, edge_data in lts.edges(data=True):
        edge_transition_name = edge_data.get('label')  # Get the transition name from the edge data
        if edge_transition_name == transition_name:  # Check if the transition name matches
            mark = lts.nodes.get(u)['marking']
            ret.append(mark)  # Add the source marking of the edge to the result list

    return ret


def get_prefix_traces(lts: nx.DiGraph, initial_marking: Marking, target_marking: Marking):
    """
    Navigates back the LTS from the target_marking to the initial_marking, collecting all edge names.

    Parameters:
    - lts (nx.DiGraph): The LTS graph with markings as nodes and transitions as edge labels.
    - initial_marking (Marking): The initial marking to navigate back to.
    - target_marking (Marking): The target marking to start navigating from.

    Returns:
    - List[str]: A list of edge names (transition names) from target_marking to initial_marking.
    """

    # Function to compare two markings
    def markings_are_equal(marking1, marking2):
        return marking1 == marking2

    # Find the node corresponding to the target marking
    target_node = None
    for node in lts.nodes:
        if markings_are_equal(lts.nodes[node].get('marking'), target_marking):
            target_node = node
            break

    if target_node is None:
        return None

    # Initialize the list to store the edge names
    edge_names = []

    # Perform a reverse traversal from target_node to initial_marking
    current_node = target_node
    while current_node is not None and not markings_are_equal(lts.nodes[current_node].get('marking'), initial_marking):
        # Find the predecessor of the current node
        predecessors = list(lts.predecessors(current_node))
        if not predecessors:
            break

        # Choose a predecessor (in this example, we just pick the first one)
        predecessor = predecessors[0]
        edge_data = lts.get_edge_data(predecessor, current_node)

        # Get the transition name (edge label) and add it to the list
        transition_name = edge_data.get('label')
        edge_names.append(transition_name)

        # Move to the predecessor node
        current_node = predecessor

    # Reverse the list to get the correct order from initial_marking to target_marking
    edge_names.reverse()

    return edge_names


def show_lts(lts):
    pos = nx.spring_layout(lts, seed=42)  # Seed for reproducible layout
    # Node and edge styles
    node_size = 500
    node_color = 'skyblue'
    node_border_color = 'black'
    font_size = 13
    font_color = 'black'
    edge_color = 'gray'
    edge_width = 4
    # Draw nodes
    nx.draw_networkx_nodes(lts, pos, node_size=node_size, node_color=node_color, edgecolors=node_border_color)
    # Draw edges
    nx.draw_networkx_edges(lts, pos, width=edge_width, edge_color=edge_color)
    # Draw labels
    nx.draw_networkx_labels(lts, pos, font_size=font_size, font_color=font_color)
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(lts, 'label')
    nx.draw_networkx_edge_labels(lts, pos, edge_labels=edge_labels, font_color='red', font_size=10)
    plt.title('LTS Visualization (Multiple Execution Paths)')
    plt.show()

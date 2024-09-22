from datetime import datetime, timedelta

import networkx as nx
from matplotlib import pyplot as plt
from pm4py.objects.log.obj import Trace, Event
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.powl.obj import Transition


def create_event(t, current_state, current_marking):
    """
    Create an event from a given transition
    """
    return Event({
        "concept:name": t.name,
        "time:timestamp": datetime.now() + timedelta(microseconds=current_state),
        "marking": convert_marking_to_str(current_marking)
    })


def create_events_from_paths(unmatched_paths):
    """
    Create an event from a list of paths
    """
    traces = []
    i = 30
    for path in unmatched_paths:
        trace = Trace()
        for t in path:
            trace.append(Event({
                "concept:name": t,
                "time:timestamp": datetime.now() + timedelta(microseconds=i),
                "marking": ""
            }))
            i += 1
        traces.append(trace)
    return traces


def convert_marking_to_str(marking):
    """
    Convert a Marking object to a string
    """
    return {str(key): value for key, value in marking.items()}


def find_marking(lts: nx.DiGraph, transition_name: str) -> [Marking]:
    """
    Find the marking(s) in the LTS (Directed Graph) where a specific transition name is present.
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
    """
    # Function to compare two markings and see if they are the same
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

    # Initialize the list to store the traces
    trace: Trace = Trace()
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
        t = Transition()
        t.label = edge_data.get('label', "")
        t.name = edge_data.get('label', "")
        trace.append(create_event(t, current_node, lts.nodes[current_node].get('marking')))
        # Move to the predecessor node
        current_node = predecessor

    # Reverse the list to get the correct order from initial_marking to target_marking
    reversed_trace = Trace(trace[::-1])

    return reversed_trace


def show_lts(lts):
    """
    Show LTS (Directed Graph) after initializing its characteristics
    """
    pos = nx.spring_layout(lts, seed=42)
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
    # Show the actual graph
    plt.show()

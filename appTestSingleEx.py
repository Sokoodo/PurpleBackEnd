import networkx as nx
import matplotlib.pyplot as plt
import pm4py
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.petri_net.obj import PetriNet, Marking
import random


# This function checks if a transition is enabled given the current marking of the Petri net.
# The transition is considered enabled if all of its input places (sources of input arcs) have at least one token.
def is_enabled(transition, marking) -> bool:
    return all(marking.get(arc.source, 0) > 0 for arc in transition.in_arcs)


# This function updates the marking of the Petri net after a transition fires.
# For each input arc of the transition, the token count in the corresponding place is decreased.
# For each output arc of the transition, the token count in the corresponding place is increased.
def execute_transition_and_get_next_marking(transition, marking):
    new_marking = marking.copy()
    for arc in transition.in_arcs:
        new_marking[arc.source] -= 1
    for arc in transition.out_arcs:
        new_marking[arc.target] = new_marking.get(arc.target, 0) + 1
    return new_marking


def build_lts_with_multiple_executions(petri_net, initial_marking, num_executions):
    lts, state_counter, state_mapping = initialize_lts(petri_net, initial_marking)

    for _ in range(num_executions):
        lts, state_counter, state_mapping = petri_to_single_path_lts(
            petri_net, initial_marking, lts, state_counter, state_mapping
        )

    return lts


def initialize_lts(petri_net, initial_marking):
    lts = nx.DiGraph()
    state_counter = 0
    # Frozen set is just an immutable version of a Python set object.
    state_mapping = {frozenset(initial_marking.items()): state_counter}
    lts.add_node(state_counter, marking=dict(initial_marking))
    return lts, state_counter, state_mapping


# This function creates a Labelled Transition System (LTS) that represents a single execution
# path through the Petri net.
# State counter will be the actual node name
def petri_to_single_path_lts(petri_net, pn_initial_marking, lts, state_counter, state_mapping):
    # A stack used to perform a depth-first search (DFS) through the Petri net.
    # It starts with the initial marking and its corresponding state ID.
    stack = [(pn_initial_marking, state_mapping[frozenset(pn_initial_marking.items())])]
    while stack:
        current_marking, current_state = stack.pop()
        # A list of transitions that are enabled in the current marking.
        # A transition is enabled if all its input places have at least one token.
        enabled_transitions = [t for t in petri_net.transitions if is_enabled(t, current_marking)]
        if not enabled_transitions:
            continue  # No more transitions to execute, end of path
        # Choose a random enabled transition and execute it
        transition = random.choice(enabled_transitions)
        new_marking = execute_transition_and_get_next_marking(transition, current_marking)
        frozen_marking = frozenset(new_marking.items())
        # Check if new marking is not already present
        if frozen_marking not in state_mapping:
            state_counter += 1
            state_mapping[frozen_marking] = state_counter
            lts.add_node(state_counter, marking=dict(new_marking))  # add to lts if not present
        target_state = state_mapping[frozen_marking]
        lts.add_edge(current_state, target_state, label=transition.name)
        # Append the new marking to the stack to continue the path from this point
        stack.append((new_marking, target_state))
    return lts, state_counter, state_mapping


# marking to str converter
def convert_marking_to_str(marking):
    return {str(key): value for key, value in marking.items()}


# finds the state with the target marking by using string-based comparisons
def find_state_by_marking(lts, target_marking):
    print(f"Looking for state with marking: {target_marking}")
    target_marking_str = convert_marking_to_str(target_marking)

    for node, data in lts.nodes(data=True):
        node_marking = convert_marking_to_str(data['marking'])
        print(f"Checking node {node} with marking: {node_marking}")
        if node_marking == target_marking_str:
            print(f"Found matching state: {node} with marking: {node_marking}")
            return node
    return None


if __name__ == "__main__":
    # Load Petri net from PNML file
    net, initial_marking, final_marking = pm4py.read.read_pnml("pnml_model.pnml")

    # Initialize the initial marking
    im = Marking()
    for p in net.places:
        if len(p.in_arcs) == 0:
            im[p] = 1

    # Generate LTS for multiple execution paths
    lts = build_lts_with_multiple_executions(net, im, num_executions=10)

    # Print the LTS
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

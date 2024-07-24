import networkx as nx
import matplotlib.pyplot as plt
import pm4py
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.petri_net.obj import PetriNet, Marking
import random


def is_enabled(transition, marking) -> bool:
    return all(marking.get(arc.source, 0) > 0 for arc in transition.in_arcs)


def execute_transition_and_get_next_marking(transition, marking):
    new_marking = marking.copy()
    for arc in transition.in_arcs:
        new_marking[arc.source] -= 1
    for arc in transition.out_arcs:
        new_marking[arc.target] = new_marking.get(arc.target, 0) + 1
    return new_marking


def initialize_lts(petri_net, initial_marking):
    lts = nx.DiGraph()
    state_counter = 0
    state_mapping = {frozenset(initial_marking.items()): state_counter}
    lts.add_node(state_counter, marking=dict(initial_marking))
    return lts, state_counter, state_mapping


def petri_to_single_path_lts(petri_net, pn_initial_marking, lts, state_counter, state_mapping):
    stack = [(pn_initial_marking, state_mapping[frozenset(pn_initial_marking.items())])]

    while stack:
        current_marking, current_state = stack.pop()
        enabled_transitions = [t for t in petri_net.transitions if is_enabled(t, current_marking)]

        if not enabled_transitions:
            continue  # No more transitions to execute, end of path

        # Choose a random enabled transition
        transition = random.choice(enabled_transitions)
        new_marking = execute_transition_and_get_next_marking(transition, current_marking)
        frozen_marking = frozenset(new_marking.items())

        if frozen_marking not in state_mapping:
            state_counter += 1
            state_mapping[frozen_marking] = state_counter
            lts.add_node(state_counter, marking=dict(new_marking))

        target_state = state_mapping[frozen_marking]
        lts.add_edge(current_state, target_state, label=transition.name)

        # Append the new marking to the stack to continue the path from this point
        stack.append((new_marking, target_state))

    return lts, state_counter, state_mapping


def build_lts_with_multiple_executions(petri_net, initial_marking, num_executions):
    lts, state_counter, state_mapping = initialize_lts(petri_net, initial_marking)

    for _ in range(num_executions):
        lts, state_counter, state_mapping = petri_to_single_path_lts(
            petri_net, initial_marking, lts, state_counter, state_mapping
        )

    return lts


def find_state_by_marking(lts, target_marking):
    for node, data in lts.nodes(data=True):
        if data['marking'] == target_marking:
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

    # Generate LTS with multiple executions
    num_executions = 10  # Adjust the number of executions as needed
    lts = build_lts_with_multiple_executions(net, im, num_executions)

    # Example: Find state with a specific marking
    target_marking = {'p1': 1, 'p2': 0}  # Replace with the actual target marking
    state = find_state_by_marking(lts, target_marking)

    if state is not None:
        print(f"State with marking {target_marking} found: State {state}")
    else:
        print(f"State with marking {target_marking} not found")

    # Visualize the LTS
    pos = nx.spring_layout(lts, seed=42)  # Seed for reproducible layout

    # Node and edge styles
    node_size = 700
    node_color = 'skyblue'
    node_border_color = 'black'
    font_size = 12
    font_color = 'black'
    edge_color = 'gray'
    edge_width = 2

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

from collections import defaultdict

import networkx as nx
import matplotlib.pyplot as plt
import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet
import random

from purple.evaluator.log_evaluator.footprint_relations import FootprintRelations


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


def initialize_lts(initial_marking):
    lts = nx.DiGraph()
    state_counter = 1
    # Frozen set is just an immutable version of a Python set object.
    state_mapping = {frozenset(initial_marking.items()): state_counter}
    lts.add_node(0, marking="SI")  # Adding the initial empty node
    lts.add_node(state_counter, marking=dict(initial_marking))
    lts.add_edge(0, state_counter)  # Connecting the initial node to the first marking
    return lts, state_counter, state_mapping


# This function creates a Labelled Transition System (LTS) that represents a single execution
# path through the Petri net.
# State counter will be the actual node name
def build_lts_with_multiple_executions(petri_net, initial_marking, num_executions):
    lts, state_counter, state_mapping = initialize_lts(initial_marking)
    traces = []
    for _ in range(num_executions):
        lts, state_counter, state_mapping, trace = random_simulation(
            petri_net, initial_marking, lts, state_counter, state_mapping
        )
        traces.append(trace)
    return lts, state_counter, state_mapping, traces


def random_simulation(petri_net, initial_marking, lts, state_counter, state_mapping):
    stack = [(initial_marking, state_mapping[frozenset(initial_marking.items())])]
    trace = []
    visited_states = set()

    while stack:
        current_marking, current_state = stack.pop()
        frozen_marking = frozenset(current_marking.items())
        if frozen_marking in visited_states:
            continue

        visited_states.add(frozen_marking)
        enabled_transitions = [t for t in petri_net.transitions if is_enabled(t, current_marking)]
        if not enabled_transitions:
            continue  # No more transitions to execute, end of path

        # Choose a random enabled transition
        transition = random.choice(enabled_transitions)
        new_marking, target_state, state_counter = finalize_sim_update_lts(
            lts, state_counter, state_mapping, current_marking, current_state, transition
        )
        trace.append(transition.name)
        # Append the new marking to the stack to continue the path from this point
        stack.append((new_marking, target_state))

    return lts, state_counter, state_mapping, trace


def guided_simulation(petri_net, initial_marking, lts, state_counter, state_mapping, relation):
    stack = [(initial_marking, state_mapping[frozenset(initial_marking.items())])]
    trace = []
    visited_states = set()

    while stack:
        current_marking, current_state = stack.pop()
        frozen_marking = frozenset(current_marking.items())
        if frozen_marking in visited_states:
            continue

        visited_states.add(frozen_marking)
        enabled_transitions = [t for t in petri_net.transitions if is_enabled(t, current_marking)]
        if not enabled_transitions:
            continue

        transition = relation(enabled_transitions)
        new_marking, target_state, state_counter = finalize_sim_update_lts(
            lts, state_counter, state_mapping, current_marking, current_state, transition
        )
        trace.append(transition.name)
        stack.append((new_marking, target_state))

    return lts, state_counter, state_mapping, trace


def finalize_sim_update_lts(lts, state_counter, state_mapping, current_marking, current_state, transition):
    new_marking = execute_transition_and_get_next_marking(transition, current_marking)
    frozen_marking = frozenset(new_marking.items())
    if frozen_marking not in state_mapping:
        state_counter += 1
        state_mapping[frozen_marking] = state_counter
        lts.add_node(state_counter, marking=dict(new_marking))
    target_state = state_mapping[frozen_marking]
    lts.add_edge(current_state, target_state, label=transition.name)
    return new_marking, target_state, state_counter


def convert_marking_to_str(marking):
    return {str(key): value for key, value in marking.items()}


def get_footprint_matrix_from_traces(traces):
    footprint_matrix = {}

    for trace in traces:
        if len(trace) > 1:
            for i in range(len(trace) - 1):
                init = trace[i]
                successive = trace[i + 1]

                if init not in footprint_matrix:
                    footprint_matrix[init] = {}

                if successive in footprint_matrix and init in footprint_matrix[successive]:
                    del footprint_matrix[successive][init]
                else:
                    footprint_matrix[init][successive] = FootprintRelations.SEQUENCE

        elif len(trace) == 1:  # Handle case where there is only one event in the trace
            init = trace[0]
            if init not in footprint_matrix:
                footprint_matrix[init] = {}

    return footprint_matrix


def get_footprint_matrix_from_petri(net: PetriNet):
    transitions: [PetriNet.Transition] = net.transitions
    matrix = {t.label: {} for t in transitions if t.label}
    for t in transitions:
        if not t.label:
            continue
        for next_t in get_visible_successors(t, net):
            next_t_name = next_t.label
            if next_t_name:
                matrix[t.label][next_t_name] = FootprintRelations.SEQUENCE
    return matrix


def get_visible_successors(transition: [PetriNet.Transition], net: PetriNet):
    next_transitions: [PetriNet.Transition] = []
    out_places: [PetriNet.Place] = []
    for out_arc in transition.out_arcs:
        temp_place = getPlace(out_arc.target, net.places)
        if temp_place is not None:
            out_places.append(temp_place)
    for op in out_places:
        for out_places_arc in op.out_arcs:
            temp_trans = getTransition(out_places_arc.target.name, net.transitions)
            if temp_trans is not None:
                next_transitions.append(temp_trans)

    visible_successors = [t for t in next_transitions if isinstance(t, PetriNet.Transition) and t.label is not None]

    return visible_successors


def getPlace(place_name, places: [PetriNet.Place]):
    for p in places:
        if str(p.name) == str(place_name):
            return p


def getTransition(transition_name, transitions: [PetriNet.Transition]):
    for t in transitions:
        if str(t.name) == str(transition_name):
            return t


if __name__ == "__main__":
    # file_path = "bpmn_model.bpmn"  # Update this to your BPMN or PNML file path
    file_path = "pnml_model.pnml"  # Update this to your BPMN or PNML file path
    net, initial_marking, final_marking = pm4py.read.read_pnml(file_path)
    im = Marking()
    for p in net.places:
        if len(p.in_arcs) == 0:
            im[p] = 1

    print("Footprint petri net:")
    print(get_footprint_matrix_from_petri(net))


    # Example relation function: choose the first enabled transition
    def example_relation(enabled_transitions):
        print("enabled_transitions")
        print(enabled_transitions[0])
        return enabled_transitions[0]


    lts, state_counter, state_mapping, random_traces = build_lts_with_multiple_executions(net, im, 1)

    # Ensure all activities are included by running guided simulation
    lts, state_counter, state_mapping, guided_traces = guided_simulation(net, im, lts, state_counter, state_mapping,
                                                                        example_relation)
    lts, state_counter, state_mapping, guided_traces = guided_simulation(net, im, lts, state_counter, state_mapping,
                                                                         example_relation)
    print("Random Traces:")
    for trace in random_traces:
        print(trace)
    print("Guided Trace:")
    print(guided_traces)
    print(lts)

    # footprint_matrix = get_footprint_matrix_from_traces(random_traces + [guided_trace])
    footprint_matrix = get_footprint_matrix_from_traces(random_traces)
    print("Footprint Matrix:")
    print(footprint_matrix)
    for key, value in footprint_matrix.items():
        print(f"{key}: {value}")

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

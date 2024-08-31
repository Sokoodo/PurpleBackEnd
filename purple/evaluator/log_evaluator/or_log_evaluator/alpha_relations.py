from pm4py import PetriNet
from pm4py.objects.bpmn.obj import Marking
from pm4py.objects.log.obj import EventLog, Trace, Event

from purple.evaluator.log_evaluator.footprint_relations import FootprintRelations
from pm4py.algo.simulation.playout.petri_net import algorithm as simulator


def get_footprint_matrix_from_eventlog(petri_net: PetriNet):
    """
    Create a footprint matrix from a list of paths.
    """
    paths = get_all_possible_paths(petri_net)
    # Initialize an empty dictionary for the footprint matrix
    footprint_matrix = {}

    # Populate the footprint matrix
    for path in paths:
        for i in range(len(path) - 1):
            current_transition = path[i]
            next_transition = path[i + 1]
            # If the current transition is not already in the footprint matrix, add it
            if current_transition not in footprint_matrix:
                footprint_matrix[current_transition] = {}

            # Add the direct relation to the footprint matrix
            footprint_matrix[current_transition][next_transition] = '->'

    # Add any missing transitions with empty dictionaries
    for path in paths:
        for transition in path:
            if transition not in footprint_matrix:
                footprint_matrix[transition] = {}

    return footprint_matrix, paths


def get_all_possible_paths(petri_net: PetriNet):
    """
    Get all the possible paths from the execution of a petri net.
    """
    print(f"{petri_net} PORCODIO")
    im = Marking()
    for p in petri_net.places:
        if len(p.in_arcs) == 0:
            im[p] = 1
    all_paths = simulator.apply(petri_net, im, variant=simulator.Variants.EXTENSIVE,
                                parameters={"max_trace_length": 10})
    paths = []
    for trace in all_paths:
        path = [event['concept:name'] for event in trace]
        paths.append(path)
    return paths


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


def get_footprint_matrix_from_traces(traces):
    footprint_matrix = {}

    # Ensure each trace is a list of event names
    for trace in traces:
        if isinstance(trace, Trace):
            trace = [event["concept:name"] for event in trace]  # Convert Trace objects to list of event names

        if not isinstance(trace, list) or not all(isinstance(event, str) for event in trace):
            raise TypeError("Each trace should be a list of event names (strings).")

        if len(trace) > 1:
            for i in range(len(trace) - 1):
                init = trace[i]
                successive = trace[i + 1]

                if init not in footprint_matrix:
                    footprint_matrix[init] = {}

                footprint_matrix[init][successive] = FootprintRelations.SEQUENCE

            last_event = trace[-1]
            if last_event not in footprint_matrix:
                footprint_matrix[last_event] = {}
        elif len(trace) == 1:  # Handle case where there is only one event in the trace
            init = trace[0]
            if init not in footprint_matrix:
                footprint_matrix[init] = {}

    print("log_footprint_matrix")
    print(footprint_matrix)

    return footprint_matrix


def compare_footprint_matrices(event_log_matrix, petri_net_matrix, tau, ref_relations):
    el_missing = EventLog()

    for event, transitions in petri_net_matrix.items():
        if event not in event_log_matrix:  # quà entra quando l'evento non è nella 2a matrice
            if len(transitions) == 0:
                trace = Trace()
                # print(f"{event} PORCODIO")
                trace._list.append(Event({"concept:name": event}))
                el_missing.append(trace)
            for next_event in transitions:
                trace = Trace()
                trace._list.append(Event({"concept:name": event}))
                trace._list.append(Event({"concept:name": next_event}))
                el_missing.append(trace)
        else:  # quà entra quando l'evento è già nella 2a matrice ma deve comunque controllare se tutte le sue relazioni sono presenti
            for next_event, relation in transitions.items():
                if next_event not in event_log_matrix[event]:
                    trace = Trace()
                    trace._list.append(Event({"concept:name": event}))
                    trace._list.append(Event({"concept:name": next_event}))
                    el_missing.append(trace)

    print("Compare: Missing relations")
    for trace in el_missing:
        events_str = " -> ".join(event["concept:name"] for event in trace._list)
        print(f"Trace: {events_str}")

    # Da testare quando guided sim funziona
    if (1 - len(el_missing) / ref_relations) >= tau / 100:
        print(f"{tau / 100}")
        print(f"{1 - len(el_missing) / ref_relations}%, SOPRA AL THRESHOLD")
        return EventLog(), True
    return el_missing, False


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

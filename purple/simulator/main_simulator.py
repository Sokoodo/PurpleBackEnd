import networkx as nx
import random

import zope
from pm4py.objects.log.obj import Trace
from purple.semantic_engine.petri_semantic_engine import PetriSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.evaluator.trace_evaluator.trace_evaluator import TraceEvaluator
from purple.util.lts_utils import find_marking, get_prefix_traces, create_event


def execute_transition_and_get_next_marking(transition, marking):
    """
    Executes the transition and get the next marking

    :param transition: transition to execute
    :param marking: current marking
    :return: updated marking after execution
    """
    new_marking = marking.copy()
    for arc in transition.in_arcs:
        new_marking[arc.source] -= 1
    for arc in transition.out_arcs:
        new_marking[arc.target] = new_marking.get(arc.target, 0) + 1
    return new_marking


def is_enabled(transition, marking) -> bool:
    """
    If all the incoming nodes of the transition are enabled, the transition is enabled and can be executed

    :param transition: transition to check
    :param marking: marking to understand if the transition is enabled or not
    :return: True if the transition can be executed
    """
    return all(marking.get(arc.source, 0) > 0 for arc in transition.in_arcs)


def parse_trace(trace):
    """
    Parses a given trace and gets a tuple of initial and successive events

    :param trace: trace to parse
    :return: tuple of initial and successive events
    """
    events = trace._list
    sequence = []
    for i in range(len(events) - 1):
        init = events[i]["concept:name"]
        successive = events[i + 1]["concept:name"]
        sequence.append((init, successive))
    return sequence


@zope.interface.implementer(ISimulator)
class Simulator:
    def __init__(self, se, te):
        self.__lts = nx.DiGraph()
        self.__se: PetriSemanticEngine = se
        self.__te: TraceEvaluator = te
        self.__state_counter = 0

    def get_lts_graph(self):
        """
        Getter for the LTS model

        :return: the lts from nx.DiGraph()
        """
        return self.__lts

    def initialize_lts(self, initial_marking):
        """
        Initialization of the LTS from an initial marking and creates an empty initial node

        :param initial_marking: the starting point
        :return: new state mapping; a "global" marking to keep track of the markings
        """
        self.__lts = nx.DiGraph()
        self.__state_counter = 1
        # Frozen set is just an immutable version of a Python set object.
        state_mapping = {frozenset(initial_marking.items()): self.__state_counter}
        self.__lts.add_node(0, marking="SI")  # Adding the initial empty node
        self.__lts.add_node(self.__state_counter, marking=dict(initial_marking))
        self.__lts.add_edge(0, self.__state_counter)  # Connecting the initial node to the first marking
        return state_mapping

    def global_simulate(self, delta_trace, initial_marking, state_mapping):
        """
        Method that analyzes the Delta to choose if perform the random simulation or the guided simulation and returns a
        list of traces discovered with the simulation

        :param delta_trace: The delta with missing traces to discover
        :param initial_marking: The initial point of the simulation
        :param state_mapping: "global" marking to keep track of the markings
        :return: The discovered traces after simulation
        """
        traces = []
        if delta_trace is None:
            state_mapping, random_traces = self.random_simulation(initial_marking, state_mapping)
            traces.extend([random_traces])
        else:
            #print(f"Delta_trace: {delta_trace}")
            markings = find_marking(self.__lts, delta_trace[0]["concept:name"])
            if markings is None or len(markings) == 0:
                state_mapping, random_traces = self.random_simulation(initial_marking, state_mapping)
                traces.extend([random_traces])
            else:
                for m in markings:
                    prefix: Trace = get_prefix_traces(self.__lts, initial_marking, m)
                    if prefix is None:
                        state_mapping, random_traces = self.random_simulation(initial_marking, state_mapping)
                        traces.extend([random_traces])
                    else:
                        relation = parse_trace(delta_trace)
                        #print(f'Prefix Traces: {prefix}')
                        state_mapping, guided_trace = self.guided_simulation(m, state_mapping, relation)
                        if len(guided_trace) > 0:
                            for gt in guided_trace:
                                prefix.append(gt)
                            traces.extend([prefix])  # Append the guided trace
                            break
                        else:
                            state_mapping, random_traces = self.random_simulation(initial_marking, state_mapping)
                            traces.extend([random_traces])

        return state_mapping, traces

    def guided_simulation(self, source_marking, state_mapping, relation):
        """
        Simulate starting from the source_marking until reaching a final marking.
        Follows the path of init first, then directly the path of successive from the relation parameter.

        :param source_marking: Initial marking
        :param state_mapping: "global" marking to keep track of the markings
        :param relation: relation to discover with guided simulation
        :return: list of discovered traces
        """
        trace: Trace = Trace()
        random_trace: Trace = Trace()
        stack = [(source_marking, state_mapping[frozenset(source_marking.items())])]
        visited_states = set()

        for init, successive in relation:
            current_marking, current_state = stack.pop()
            if current_state in visited_states:
                continue
            visited_states.add(current_state)

            init_transition = self.__se.get_transition_by_name(init)
            successive_transition = self.__se.get_transition_by_name(successive)

            # Check if the initial transition is enabled
            if is_enabled(init_transition, current_marking):
                # Fire the initial transition
                new_marking = execute_transition_and_get_next_marking(init_transition, current_marking)
                trace.append(create_event(init_transition, current_state, current_marking))
                # Find the new state in the LTS
                new_state = state_mapping.get(frozenset(new_marking.items()))
                # Check if the successive transition is enabled
                if is_enabled(successive_transition, new_marking):
                    # Fire the successive transition
                    final_marking = execute_transition_and_get_next_marking(successive_transition, new_marking)
                    trace.append(create_event(successive_transition, new_state, new_marking))
                    state_mapping, random_trace = self.random_simulation(final_marking, state_mapping, trace,
                                                                         new_marking)
                else:
                    # If the successive transition is not enabled
                    state_mapping, random_trace = self.random_simulation(new_marking, state_mapping, trace,
                                                                         current_marking)
        #print(f'GUIDED Traces: {random_trace}')
        return state_mapping, random_trace

    def random_simulation(self, initial_marking, state_mapping, guided_traces=None, source_marking=None):
        """
        Perform a random execution of the model, in this case a petrinet, and returns the list of discovered traces

        :param initial_marking: Initial marking, where to start
        :param state_mapping: "global" marking to keep track of the markings
        :param guided_traces: If you already have starting traces, default None
        :param source_marking: If you already have starting traces you have to include their marking, default None
        :return: list of discovered traces
        """
        traces: Trace = guided_traces if guided_traces is not None else Trace()
        frozen_marking = frozenset(initial_marking.items())
        if frozen_marking not in state_mapping:
            self.__state_counter += 1
            state_mapping[frozen_marking] = self.__state_counter
            self.__lts.add_node(self.__state_counter, marking=dict(initial_marking))
            frozen_source_marking = frozenset(source_marking.items())
            self.__lts.add_edge(state_mapping[frozen_source_marking], self.__state_counter,
                                label=traces[len(traces) - 1]['concept:name'])
        stack = [(initial_marking, state_mapping[frozen_marking])]
        visited_states = set()

        while stack:
            current_marking, current_state = stack.pop()
            frozen_marking = frozenset(current_marking.items())
            if frozen_marking in visited_states:
                continue

            visited_states.add(frozen_marking)
            enabled_transitions = [t for t in self.__se.get_model().transitions if is_enabled(t, current_marking)]
            if not enabled_transitions:
                continue

            transition = random.choice(enabled_transitions)
            new_marking, target_state = self.finalize_sim_update_lts(
                state_mapping, current_marking, current_state, transition
            )
            traces.append(create_event(transition, current_state, current_marking))  # Add transition name to traces
            stack.append((new_marking, target_state))

        return state_mapping, traces  # Return a list of traces

    def finalize_sim_update_lts(self, state_mapping, current_marking, current_state, transition):
        """
        Finalization: creates a new marking and update the model with the new node and edge

        :param state_mapping: "global" marking to keep track of the markings
        :param current_marking: current marking
        :param current_state: current state of the LTS
        :param transition: transition to include in the LTS
        :return: the new marking after execution and the next state of the LTS
        """
        new_marking = execute_transition_and_get_next_marking(transition, current_marking)
        frozen_marking = frozenset(new_marking.items())
        if frozen_marking not in state_mapping:
            self.__state_counter += 1
            state_mapping[frozen_marking] = self.__state_counter
            self.__lts.add_node(self.__state_counter, marking=dict(new_marking))
        target_state = state_mapping[frozen_marking]
        self.__lts.add_edge(current_state, target_state, label=transition.name)
        return new_marking, target_state

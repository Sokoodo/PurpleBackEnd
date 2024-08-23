from datetime import datetime, timedelta

import networkx as nx
import random

import pm4py
import zope
from pm4py.objects.log.obj import Event, Trace
from purple.semantic_engine.or_semantic_engine import PetriSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.evaluator.trace_evaluator.trace_evaluator import TraceEvaluator
from purple.util.lts_utils import find_marking, get_prefix_traces, create_event


def execute_transition_and_get_next_marking(transition, marking):
    new_marking = marking.copy()
    for arc in transition.in_arcs:
        new_marking[arc.source] -= 1
    for arc in transition.out_arcs:
        new_marking[arc.target] = new_marking.get(arc.target, 0) + 1
    return new_marking


def is_enabled(transition, marking) -> bool:
    return all(marking.get(arc.source, 0) > 0 for arc in transition.in_arcs)


def parse_trace(trace):
    events = trace._list
    sequence = []
    for i in range(len(events) - 1):
        init = events[i]["concept:name"]
        successive = events[i + 1]["concept:name"]
        sequence.append((init, successive))
    return sequence


@zope.interface.implementer(ISimulator)
class OrSimulator:
    def __init__(self, se, te):
        self.__lts = nx.DiGraph()
        self.__se: PetriSemanticEngine = se
        self.__te: TraceEvaluator = te
        self.__state_counter = 0

    def get_lts_graph(self):
        return self.__lts

    def initialize_lts(self, initial_marking):
        self.__lts = nx.DiGraph()
        self.__state_counter = 1
        # Frozen set is just an immutable version of a Python set object.
        state_mapping = {frozenset(initial_marking.items()): self.__state_counter}
        self.__lts.add_node(0, marking="SI")  # Adding the initial empty node
        self.__lts.add_node(self.__state_counter, marking=dict(initial_marking))
        self.__lts.add_edge(0, self.__state_counter)  # Connecting the initial node to the first marking
        return state_mapping

    def global_simulate(self, delta_trace, initial_marking, state_mapping):
        traces = []
        if delta_trace is None:
            state_mapping, random_traces = self.random_simulation(initial_marking, state_mapping)
            traces.extend([random_traces])
        else:
            print(f"Delta_trace: {delta_trace}")
            markings = find_marking(self.__lts, delta_trace[0]["concept:name"])
            print(f"Markings: {markings}")
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
                        print(f'Prefix Traces: {prefix}')
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
        print(f'Random Traces: {random_trace}')
        return state_mapping, random_trace

    def random_simulation(self, initial_marking, state_mapping, guided_traces=None, source_marking=None):
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
        new_marking = execute_transition_and_get_next_marking(transition, current_marking)
        frozen_marking = frozenset(new_marking.items())
        if frozen_marking not in state_mapping:
            self.__state_counter += 1
            state_mapping[frozen_marking] = self.__state_counter
            self.__lts.add_node(self.__state_counter, marking=dict(new_marking))
        target_state = state_mapping[frozen_marking]
        self.__lts.add_edge(current_state, target_state, label=transition.name)
        return new_marking, target_state

    # def random_simulate(self):
    #     initial_place = self.__se.get_initial_state()
    #
    #     if not self.__lts.has_node('S-I') and not self.__lts.has_node('S-1'):
    #         self.__lts = self.update_lts('S-I')
    #         self.__lts = self.update_lts('S-1', 'S-I', ['initEdge'], Event(), [initial_place])
    #
    #     return self.finalize_random_sim(initial_place)
    #
    # def finalize_random_sim(self, initial_place: PetriNet.Place):
    #     # next_steps: [str, Trace] = self.__se.get_next_step(initial_place)
    #     final_trace = Trace()
    #     places: [PetriNet.Place] = [initial_place]
    #     while places.__len__() > 0:
    #         transitions: [PetriNet.Transition] = []
    #         old_place_for_tracking = []
    #         copy_places = copy.deepcopy(places)
    #         for p in places:
    #             next_tr: PetriNet.Transition = self.__se.get_next_transitions(p, True)
    #             if next_tr not in transitions and next_tr is not None:
    #                 transitions.append(next_tr)
    #                 copy_places = self.remove_place_from_places(copy_places, p)
    #                 old_place_for_tracking.append({
    #                     "trans": next_tr,
    #                     "placesForState": copy.deepcopy(copy_places)
    #                 })
    #             else:
    #                 for item in old_place_for_tracking:
    #                     if item["trans"] == next_tr:
    #                         item["placesForState"].remove(p)
    #
    #         if transitions.__len__() > 0:
    #             places = []
    #             other_places_to_add
    #             for t in transitions:
    #                 next_places = self.__se.get_next_places(t)
    #                 places_for_state: [PetriNet.Place] = []
    #                 for item in old_place_for_tracking:
    #                     if item["trans"] == t:
    #                         item["placesForState"].extend(next_places)
    #                         places_for_state = item["placesForState"]
    #                 places.extend(next_places)
    #                 event = Event({
    #                     "concept:name": t.name,
    #                     "time:timestamp": datetime.now() + timedelta(microseconds=self.__lts_index),
    #                     "places": self.places_to_dict(next_places)
    #                 })
    #                 self.__lts = self.update_lts(
    #                     f'S-{self.__lts_index}',
    #                     f'S-{self.__lts_index - 1}',
    #                     [t.name],
    #                     event,
    #                     places_for_state
    #                 )
    #                 final_trace.append(event)
    #                 self.__lts_index += 1
    #         else:
    #             places = []
    #
    #     # print("final_trace")
    #     # print(final_trace)
    #     print(self.__lts)
    #     return final_trace
    # def place_to_dict(self, place: PetriNet.Place) -> dict:
    #     return {
    #         "name": place.name,
    #         "in_arcs": [arc.source.name for arc in place.in_arcs],  # Assuming each arc has a name property
    #         "out_arcs": [arc.target.name for arc in place.out_arcs],  # Assuming each arc has a name property
    #         "properties": place.properties  # Assuming properties is already serializable
    #     }
    #
    # def places_to_dict(self, places: [PetriNet.Place]) -> [dict]:
    #     return [self.place_to_dict(place) for place in places]
    #
    # def update_lts(self, state, old_state: str = None, edges: [str] = None, event: Event = None, new_node_places=None):
    #     temp_lts = self.__lts
    #     temp_lts.add_node(state, places=[new_node_places])
    #
    #     if edges is not None and old_state is not None and event is not None:
    #         temp_lts.add_edge(old_state, state, label=edges[0], event=event)
    #         # print(temp_lts.edges.__getattribute__(__name=transition))
    #
    #     return temp_lts

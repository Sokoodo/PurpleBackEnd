from datetime import datetime, timedelta

import copy
import networkx as nx
import zope
from matplotlib import pyplot as plt
from pm4py import PetriNet
from pm4py.objects.log.obj import Trace, Event, EventLog

from purple.evaluator.delta import Delta
from purple.semantic_engine.or_semantic_engine import OrSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.evaluator.trace_evaluator.trace_evaluator import TraceEvaluator


@zope.interface.implementer(ISimulator)
class OrSimulator:
    def __init__(self, se, te):
        self.__lts = nx.DiGraph()
        self.__se: OrSemanticEngine = se
        self.__te: TraceEvaluator = te
        self.__lts_index = 2

    def global_simulate(self, delta: Delta):
        event_log = EventLog()
        if delta is None or delta.is_empty():
            event_log.append(self.random_simulate())
        else:
            last_delta: Delta = copy.deepcopy(delta)
            # print("Delta")
            # print(last_delta.get_missing())
            for delta_trace in last_delta.get_missing():
                # if PURPLE.is_interrupted(): ??
                #     break
                previous_places: [PetriNet.Place] = []
                successive_places: [PetriNet.Place] = []
                i = 0
                while not self.edge_exists_in_lts(delta_trace[0]["concept:name"]):
                    event_log.append(self.random_simulate())
                    i += 1

                previous_places = self.__se.get_prev_place_by_transition_name(
                    delta_trace[0]["concept:name"])
                successive_places = self.__se.get_successive_place_by_transition_name(
                    delta_trace[0]["concept:name"])
                target_of_delta: str | None = None  # delta_trace[1]["concept:name"]
                print(previous_places)
                print(delta_trace)
                if len(previous_places) > 0:
                    if target_of_delta is None:  # se non ha -> B ad esempio faccio finalize
                        print(previous_places)
                        # event_log.append(self.finalize_sim(starts_places))
                    else:  # se ha -> B ad esempio faccio guided
                        pass
                        # event_log.append(self.guided_simulate(previous_places, successive_places, delta_trace).values())
                else:  # quaa è na stronzata perchè continuo a cambia l'lts sotto e quindi che senso c'ha
                    event_log.append(self.random_simulate())
                    print(event_log[len(event_log) - 1])

        # print(self.__lts_states)
        return event_log

    def show_lts(self):
        pos = nx.spring_layout(self.__lts)
        nx.draw(self.__lts, pos, with_labels=True, node_size=500, font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(self.__lts, 'label')
        nx.draw_networkx_edge_labels(self.__lts, pos, edge_labels=edge_labels, font_color='red')
        plt.show()

    def get_prefix(self, start):

        pass

    def random_simulate(self):
        initial_place = self.__se.get_initial_state()

        if not self.__lts.has_node('S-I') and not self.__lts.has_node('S-1'):
            self.__lts = self.update_lts('S-I')
            self.__lts = self.update_lts('S-1', 'S-I', ['initEdge'], Event(), [initial_place])

        return self.finalize_random_sim(initial_place)

    def finalize_random_sim(self, initial_place: PetriNet.Place):
        # next_steps: [str, Trace] = self.__se.get_next_step(initial_place)
        final_trace = Trace()
        places: [PetriNet.Place] = [initial_place]
        while places.__len__() > 0:
            transitions: [PetriNet.Transition] = []
            old_place_for_tracking = []
            copy_places = copy.deepcopy(places)
            for p in places:
                next_tr: PetriNet.Transition = self.__se.get_next_transition(p)
                if next_tr not in transitions and next_tr is not None:
                    transitions.append(next_tr)
                    copy_places = self.remove_place_from_places(copy_places, p)
                    old_place_for_tracking.append({
                        "trans": next_tr,
                        "placesForState": copy.deepcopy(copy_places)
                    })
                else:
                    for item in old_place_for_tracking:
                        if item["trans"] == next_tr:
                            item["placesForState"].remove(p)

            if transitions.__len__() > 0:
                places = []
                other_places_to_add
                for t in transitions:
                    next_places = self.__se.get_next_places(t)
                    places_for_state: [PetriNet.Place] = []
                    for item in old_place_for_tracking:
                        if item["trans"] == t:
                            item["placesForState"].extend(next_places)
                            places_for_state = item["placesForState"]
                    places.extend(next_places)
                    event = Event({
                        "concept:name": t.name,
                        "time:timestamp": datetime.now() + timedelta(microseconds=self.__lts_index),
                        "places": self.places_to_dict(next_places)
                    })
                    self.__lts = self.update_lts(
                        f'S-{self.__lts_index}',
                        f'S-{self.__lts_index - 1}',
                        [t.name],
                        event,
                        places_for_state
                    )
                    final_trace.append(event)
                    self.__lts_index += 1
            else:
                places = []

        # print("final_trace")
        # print(final_trace)
        print(self.__lts)
        return final_trace

    def remove_place_from_places(self, pl_list: [PetriNet.Place], p: PetriNet.Place):
        for place in pl_list:
            if place.name == p.name:
                pl_list.remove(place)
        return pl_list

    def place_to_dict(self, place: PetriNet.Place) -> dict:
        return {
            "name": place.name,
            "in_arcs": [arc.source.name for arc in place.in_arcs],  # Assuming each arc has a name property
            "out_arcs": [arc.target.name for arc in place.out_arcs],  # Assuming each arc has a name property
            "properties": place.properties  # Assuming properties is already serializable
        }

    def places_to_dict(self, places: [PetriNet.Place]) -> [dict]:
        return [self.place_to_dict(place) for place in places]

    def guided_simulate(self):
        pass

    def update_lts(self, state, old_state: str = None, edges: [str] = None, event: Event = None, new_node_places=None):
        temp_lts = self.__lts
        temp_lts.add_node(state, places=[new_node_places])

        if edges is not None and old_state is not None and event is not None:
            temp_lts.add_edge(old_state, state, label=edges[0], event=event)
            # print(temp_lts.edges.__getattribute__(__name=transition))

        return temp_lts

    def edge_exists_in_lts(self, edge_to_check) -> bool:
        for u, v, data in self.__lts.edges(data=True):
            if data.get('label') == edge_to_check:
                return True
        return False

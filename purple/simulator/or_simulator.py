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
        self.__lts_states: {str, [PetriNet.Place]} = {}
        self.__se: OrSemanticEngine = se
        self.__te: TraceEvaluator = te

    def global_simulate(self, delta: Delta):
        event_log = EventLog()
        if delta is None or delta.is_empty():
            event_log.append(self.random_simulate())
            event_log.append(self.random_simulate())
        else:
            last_delta: Delta = copy.deepcopy(delta)
            print("Delta")
            print(last_delta.get_missing())
            for delta_trace in last_delta.get_missing():
                # if PURPLE.is_interrupted(): ??
                #     break
                starts = self.find_edge_and_get_target(delta_trace[0]["concept:name"])
                print(self.find_edge_and_get_target(delta_trace[0]["concept:name"]))
                other = delta_trace[0]["concept:name"]
                print(delta_trace)
                print(other)
                print(self.__lts.edges(data=True))
                if starts is None:
                    event_log.append(self.random_simulate())
                # else:
                #     delta_trace._list.pop(0)
                #     for start in starts:
                #         prefix = self.get_prefix(start)
                #         if not delta_trace._list:
                #             for traces in self.finalize_sim(prefix, start).values():
                #                 for delta_trace in traces.values():
                #                     self.log.append(delta_trace)
                #         else:
                #             for traces in self.guided_sim(prefix, start, delta_trace).values():
                #                 for delta_trace in traces.values():
                #                     self.log.append(delta_trace)

        pos = nx.spring_layout(self.__lts)
        nx.draw(self.__lts, pos, with_labels=True, node_size=500, font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(self.__lts, 'label')
        nx.draw_networkx_edge_labels(self.__lts, pos, edge_labels=edge_labels, font_color='red')
        plt.show()
        # print(self.__lts_states)

        return event_log

    def random_simulate(self):
        initial_place = self.__se.get_initial_state()

        self.__lts_states.update({'S-I': []})
        self.__lts = self.update_lts('S-I')

        self.__lts_states.update({'S-1': [initial_place]})
        self.__lts = self.update_lts('S-1', 'S-I', ['initEdge'], Event())

        return self.finalize_sim(initial_place)

    def finalize_sim(self, initial_place: PetriNet.Place):
        # next_steps: [str, Trace] = self.__se.get_next_step(initial_place)
        final_trace = Trace()
        places: [PetriNet.Place] = [initial_place]
        i = 2
        while places.__len__() > 0:
            transitions: [PetriNet.Transition] = []

            for p in places:
                next_tr = self.__se.get_next_transition(p)
                if next_tr not in transitions and next_tr is not None:
                    transitions.append(next_tr)

            if transitions.__len__() > 0:
                places = []
                for t in transitions:
                    places.extend(self.__se.get_next_places(t))
                    event = Event(
                        {"concept:name": t.name, "time:timestamp": datetime.now() + timedelta(microseconds=i)}
                    )
                    self.__lts_states.update({f'S-{i}': [self.__se.get_next_places(t)]})
                    self.__lts = self.update_lts(f'S-{i}', f'S-{i - 1}', [t.name], event)
                    final_trace.append(event)
                    i = i + 1
            else:
                places = []

        # print("final_trace")
        # print(final_trace)
        return final_trace

    def guided_simulate(self):
        pass

    def update_lts(self, state, old_state: str = None, edges: [str] = None, event: Event = None):
        temp_lts = self.__lts
        temp_lts.add_node(state)

        if edges is not None and old_state is not None and event is not None:
            temp_lts.add_edge(old_state, state, label=edges[0], event=event)
            # print(temp_lts.edges.__getattribute__(__name=transition))

        return temp_lts

    def find_edge_and_get_target(self, edge_to_check):
        for u, v, data in self.__lts.edges(data=True):
            if data.get('label') == edge_to_check:
                return v
        return None

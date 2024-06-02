import networkx as nx
import zope
from matplotlib import pyplot as plt

from purple.semantic_engine.or_semantic_engine import OrSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.trace_evaluator.trace_evaluator import TraceEvaluator


@zope.interface.implementer(ISimulator)
class OrSimulator:
    def __init__(self, se, te):
        self.__lts = nx.DiGraph()
        self.__lts_states: {str, [str]} = {}
        self.__eventLog = []
        self.__se: OrSemanticEngine = se
        self.__te: TraceEvaluator = te

    def get_event_log(self):
        return self.__eventLog

    def global_simulate(self, delta):
        temp_place = self.__se.get_initial_state()
        i = 0
        self.__lts_states.update({f'S-{i}': [temp_place]})
        self.__lts = self.update_lts(f'S-{i}')
        places: [str] = [temp_place]

        while places.__len__() != 0:
            i = i + 1
            transitions = []

            for p in places:
                next_tr = self.__se.get_next_transitions(p)
                print(next_tr)
                if next_tr not in transitions:
                    transitions.append(next_tr)

            if transitions.__len__() != 0:
                places = self.__se.get_next_places(transitions[0])
                self.__lts_states.update({f'S-{i}': places})
                self.__lts = self.update_lts(f'S-{i}', transitions[0], f'S-{i - 1}')

        pos = nx.spring_layout(self.__lts)
        nx.draw(self.__lts, pos, with_labels=True, node_size=500, font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(self.__lts, 'label')
        nx.draw_networkx_edge_labels(self.__lts, pos, edge_labels=edge_labels, font_color='red')
        plt.show()
        print(self.__lts_states)

        return self.__eventLog

    def random_simulate(self, temp_place):
        temp_lts = self.__se.get_next_step(temp_place)
        return temp_lts

    def guided_simulate(self):
        pass

    def update_lts(self, state, edges: [str] = None, old_state: str = None):
        temp_lts = self.__lts
        temp_lts.add_node(state)

        if edges is not None and old_state is not None:
            temp_lts.add_edge(old_state, state, label=edges)
            # print(temp_lts.edges.__getattribute__(__name=transition))

        return temp_lts

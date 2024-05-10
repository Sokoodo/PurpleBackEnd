import networkx as nx
import zope.interface
from matplotlib import pyplot as plt


class ISimulator(zope.interface.Interface):
    def get_event_log(self):
        pass

    def global_simulate(self, delta):
        pass

    def random_simulate(self):
        pass

    def guided_simulate(self):
        pass


@zope.interface.implementer(ISimulator)
class Simulator:
    def __init__(self, se, te):
        self.__lts = []
        self.__eventLog = []
        self.__se = se
        self.__te = te
        # directed_graph = self.create_directed_graph(net, initial_marking)
        # plt.show(directed_graph)

    def get_event_log(self):
        return self.__eventLog

    def global_simulate(self, delta):
        if delta is []:
            print("aa")
            return self.random_simulate()
        else:
            pass
        return self.__eventLog

    def random_simulate(self):
        pass

    def guided_simulate(self):
        pass

    # def create_directed_graph(self, net, initial_marking):
    #     dg = nx.DiGraph()
    #     dg.add_node(0), dg.add_node(1), dg.add_node(2), dg.add_node(3), dg.add_node(4)
    #     (dg.add_edge(0, 1), dg.add_edge(1, 2), dg.add_edge(0, 2), dg.add_edge(1, 4), dg.add_edge(1, 3),
    #      dg.add_edge(3, 2), dg.add_edge(3, 1), dg.add_edge(4, 3))
    #     nx.draw(dg, with_labels=True, font_weight='bold')
    #     return dg

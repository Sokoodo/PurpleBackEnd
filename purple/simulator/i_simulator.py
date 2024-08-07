import zope.interface


class ISimulator(zope.interface.Interface):
    def get_event_log(self):
        pass

    def get_lts_graph(self):
        pass

    def initialize_lts(self, initial_marking):
        pass

    def global_simulate(self, delta, initial_marking, state_mapping):
        pass

    def random_simulate(self):
        pass

    def guided_simulate(self, initial_marking, state_mapping, footprint_matrix):
        pass

    def update_lts(self, place: str, transition: str = None):
        pass

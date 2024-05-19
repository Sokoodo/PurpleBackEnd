import zope.interface


class ISimulator(zope.interface.Interface):
    def get_event_log(self):
        pass

    def global_simulate(self, delta):
        pass

    def random_simulate(self):
        pass

    def guided_simulate(self):
        pass

    def update_lts(self, place: str, transition: str = None):
        pass

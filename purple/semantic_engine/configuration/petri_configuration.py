import zope

from purple.simulator.i_simulator import ISimulator


@zope.interface.implementer(ISimulator)
class PnmlConfiguration:
    def __init__(self, marking):
        self.marking = marking
        self._processes = {"p"}
        self._instances = {"p": {"i"}}

    def get_global_data(self):
        return {}

    def get_local_data(self):
        return {}

    def get_instances(self, proc):
        return self._instances.get(proc, set())

    def get_processes(self):
        return self._processes

    def get_marking(self):
        return self.marking

    def __eq__(self, other):
        if not isinstance(other, PnmlConfiguration):
            return False
        return self.marking == other.marking

    def __hash__(self):
        return hash(tuple(sorted(self.marking.items())))

    def __str__(self):
        return str(self.marking)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

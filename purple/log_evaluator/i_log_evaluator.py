import zope
from pm4py import PetriNet
from pm4py.objects.log.obj import EventLog


class ILogEvaluator(zope.interface.Interface):
    def evaluate(self, event_log, delta):
        pass

    def get_footprint_matrix_from_event_log(self, log: EventLog):
        pass

    def get_footprint_matrix_from_petri(self, net: PetriNet):
        pass

    def compare_alpha_relations(self, ref, disc, tau, ref_relations):
        pass

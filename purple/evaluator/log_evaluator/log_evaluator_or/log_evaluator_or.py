import zope.interface
from pm4py.objects.log.obj import EventLog, Trace

from purple.evaluator.delta import Delta
from purple.evaluator.log_evaluator.i_log_evaluator import ILogEvaluator
from purple.evaluator.log_evaluator.log_evaluator_or.alpha_relations import get_footprint_matrix_from_petri, \
    compare_footprint_matrices, get_footprint_matrix_from_traces


@zope.interface.implementer(ILogEvaluator)
class LogEvaluator:
    def __init__(self, net):
        self.__petri_footprint_matrix = get_footprint_matrix_from_petri(net)
        self.__ref_relations = len(self.__petri_footprint_matrix)
        print("petri_footprint_matrix")
        print(self.__petri_footprint_matrix)
        for x in self.__petri_footprint_matrix.keys():
            self.__ref_relations += len(self.__petri_footprint_matrix[x])
        # print("ref relations")
        # print(self.__ref_relations)
        pass

    def get_footprint_matrix(self):
        return self.__petri_footprint_matrix

    def evaluate(self, traces, tau):
        footprint_matrix_from_event_log = get_footprint_matrix_from_traces(traces)
        return self.get_delta(footprint_matrix_from_event_log, tau)

    def get_delta(self, footprint_matrix_from_event_log, tau):
        return Delta(compare_footprint_matrices(
            footprint_matrix_from_event_log,
            self.__petri_footprint_matrix, tau,
            self.__ref_relations)
        )

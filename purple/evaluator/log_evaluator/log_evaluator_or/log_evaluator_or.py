import zope.interface

from purple.evaluator.delta import Delta
from purple.evaluator.log_evaluator.i_log_evaluator import ILogEvaluator
from purple.evaluator.log_evaluator.log_evaluator_or.alpha_relations import compare_footprint_matrices, \
    get_footprint_matrix_from_traces, get_footprint_matrix_from_eventlog


@zope.interface.implementer(ILogEvaluator)
class LogEvaluator:
    def __init__(self, net):
        self.__petri_footprint_matrix, self.__paths_from_petri = get_footprint_matrix_from_eventlog(net)
        self.__ref_relations = len(self.__petri_footprint_matrix)
        print("petri_footprint_matrix")
        print(self.__petri_footprint_matrix)
        for x in self.__petri_footprint_matrix.keys():
            self.__ref_relations += len(self.__petri_footprint_matrix[x])
        print("ref relations")
        print(self.__ref_relations)
        pass

    def get_footprint_matrix(self):
        return self.__petri_footprint_matrix

    def get_all_paths_from_petri(self):
        return self.__paths_from_petri

    def evaluate(self, traces, tau):
        footprint_matrix_from_event_log = get_footprint_matrix_from_traces(traces)
        return self.get_delta(footprint_matrix_from_event_log, tau)

    def get_delta(self, footprint_matrix_from_event_log, tau):
        delta, tau_interruption = compare_footprint_matrices(
            footprint_matrix_from_event_log,
            self.__petri_footprint_matrix, tau,
            self.__ref_relations)
        return Delta(delta), tau_interruption


def find_unmatched_paths(source_traces, final_simple_traces):
    """
    Find the paths in `source_traces` that do not appear in `final_simple_traces`.
    """
    # Initialize a list to store unmatched paths
    unmatched_paths = []
    final_traces_str = []
    for trace in final_simple_traces:
        trace_str = [event['concept:name'] for event in trace]
        final_traces_str.append(trace_str)

    # Compare each path in all_paths with final_simple_traces
    for path in source_traces:
        if path not in final_traces_str:
            unmatched_paths.append(path)

    return unmatched_paths

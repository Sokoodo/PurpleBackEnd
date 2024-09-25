import zope.interface

from purple.evaluator.trace_evaluator.i_trace_evaluator import ITraceEvaluator


@zope.interface.implementer(ITraceEvaluator)
class TraceEvaluator:
    def __init__(self):
        self.__interrupted = False
        pass

    def get_interrupted(self) -> bool:
        """
        Is the trace evaluator interrupted?

        :return: true if the number of traces overcome the number of paths by more than 10 times
        """
        return self.__interrupted

    def evaluate(self, all_paths: list[list], traces: list):
        """
        Evaluates all traces against the given list of paths.

        :param all_paths: all possible model paths
        :param traces: the traces we are evaluating
        """
        max_simulated_traces = len(all_paths) * 12
        if len(traces) > max_simulated_traces:
            self.__interrupted = True
        pass

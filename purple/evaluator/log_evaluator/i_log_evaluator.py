import zope
from pm4py.objects.log.obj import EventLog

from purple.evaluator.delta import Delta


class ILogEvaluator(zope.interface.Interface):
    def evaluate(self, event_log, tau=None) -> Delta | EventLog:
        pass

    def get_all_paths_from_petri(self) -> list[list]:
        pass

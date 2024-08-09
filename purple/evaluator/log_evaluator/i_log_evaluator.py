import zope

from purple.evaluator.delta import Delta


class ILogEvaluator(zope.interface.Interface):
    def evaluate(self, event_log, tau) -> Delta:
        pass

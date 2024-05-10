import zope.interface


class ITraceEvaluator(zope.interface.Interface):
    def evaluate(self, event_log):
        pass


@zope.interface.implementer(ITraceEvaluator)
class TraceEvaluator:
    def __init__(self):
        pass

    def evaluate(self, event_log):
        pass

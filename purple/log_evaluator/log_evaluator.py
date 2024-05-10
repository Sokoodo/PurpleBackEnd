import zope.interface


class ILogEvaluator(zope.interface.Interface):
    def evaluate(self, event_log, delta):
        pass


@zope.interface.implementer(ILogEvaluator)
class LogEvaluator:
    def __init__(self):
        pass

    def evaluate(self, event_log, delta):
        pass

import zope


class ILogEvaluator(zope.interface.Interface):
    def evaluate(self, event_log, tau):
        pass

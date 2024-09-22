import zope.interface


class ITraceEvaluator(zope.interface.Interface):
    def evaluate(self, all_paths, event_log):
        pass

    def get_interrupted(self) -> bool:
        pass

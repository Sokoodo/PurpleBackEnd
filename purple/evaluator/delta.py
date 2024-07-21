from pm4py.objects.log.obj import EventLog, Trace


class Delta:
    def __init__(self, event_log: EventLog):
        self.missing: EventLog = event_log

    def get_missing(self):
        return self.missing

    def is_empty(self):
        return len(self.missing) == 0

    def add_missing_trace(self, trace: Trace):
        self.missing.append(trace)

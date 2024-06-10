import zope
from pm4py.objects.log.obj import EventLog

from purple.util.trace.i_trace import ITrace
import itertools


@zope.interface.implementer(ITrace)
class TraceImpl:
    case_num = itertools.count()  # Iterator to generate case numbers

    def __init__(self, data):
        self.case_id = self._get_new_case_id()
        self.data = data
        self.trace: [EventLog] = []

    def _get_new_case_id(self):
        return f"case_{next(self.case_num)}"

    def append_event(self, event: EventLog):
        self.trace.append(event)

    def get(self, index):
        if index < 0 or index >= len(self.trace):
            return None
        return self.trace[index]

    def get_trace(self):
        return self.trace

    def get_case_id(self):
        return self.case_id

    def remove(self, index):
        if 0 <= index < len(self.trace):
            self.trace.pop(index)

    def get_data(self):
        return self.data

    def equals(self, other):
        if not isinstance(other, TraceImpl):
            return False
        return self.case_id == other.case_id and self.data == other.data and self.trace == other.trace

    def set_case_id(self, case_id):
        self.case_id = case_id

    def insert(self, events, index, repetitions):
        new_trace: [EventLog] = self.trace[:index]
        for _ in range(int(repetitions)):
            new_trace.extend(events)
        new_trace.extend(self.trace[index:])
        self.trace = new_trace

    def __repr__(self):
        return f"[{self.case_id}, {self.data}, {self.trace}]"

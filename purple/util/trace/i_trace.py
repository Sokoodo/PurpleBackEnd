from zope.interface import Interface


class ITrace(Interface):
    def append_event(event):
        """Appends an event to the trace"""

    def get(index):
        """Gets an event by index"""

    def get_trace():
        """Gets the list of events"""

    def get_case_id():
        """Gets the case ID"""

    def remove(index):
        """Removes an event by index"""

    def get_data():
        """Gets the data"""

    def equals(other):
        """Checks equality with another object"""

    def set_case_id(case_id):
        """Sets the case ID"""

    def insert(events, index, repetitions):
        """Inserts events with repetitions at a specific index"""

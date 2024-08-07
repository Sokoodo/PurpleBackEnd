import random
from collections import defaultdict, deque

class DirectedWeightedPseudograph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, from_node, to_node, edge):
        if from_node not in self.graph:
            self.graph[from_node] = {}
        self.graph[from_node][to_node] = edge

    def get_edge(self, from_node, to_node):
        return self.graph[from_node][to_node]

    def predecessor_list_of(self, node):
        predecessors = []
        for from_node in self.graph:
            if node in self.graph[from_node]:
                predecessors.append(from_node)
        return predecessors

class Configuration:
    def __init__(self, marking, processes=None, instances=None):
        self.marking = marking
        self.processes = processes or []
        self.instances = instances or defaultdict(list)

    def get_processes(self):
        return self.processes

    def get_instances(self, process):
        return self.instances[process]

    def get_local_data(self):
        return self.marking

class Event:
    def __init__(self, process, instance, label):
        self.process = process
        self.instance = instance
        self.label = label

    def is_empty_event(self):
        return self.label == ''

class Trace:
    def __init__(self, local_data):
        self.local_data = local_data
        self.events = []

    def append_event(self, event):
        self.events.append(event)

class LabelledEdge:
    def __init__(self, label):
        self.label = label

class LTSUtil:
    @staticmethod
    def get_prefix(lts, data_configurations, s):
        t = defaultdict(lambda: defaultdict(Trace))
        stack = deque()
        predecessors = lts.predecessor_list_of(s)
        init_data, pred, curr = None, None, s

        while curr not in data_configurations:
            pred = random.choice(predecessors)
            event = lts.get_edge(pred, curr).label
            stack.append(event)
            init_data = curr
            curr = pred
            predecessors = lts.predecessor_list_of(curr)

        for proc in init_data.get_processes():
            t[proc] = {}
            for inst in init_data.get_instances(proc):
                t[proc][inst] = Trace(init_data.get_local_data())

        while stack:
            e = stack.pop()
            if e.is_empty_event():
                continue
            t[e.process][e.instance].append_event(e)

        return t

# Main Execution Example

def main():
    # Initialize LTS
    lts = DirectedWeightedPseudograph()

    # Example nodes and edges
    config1 = Configuration({'p1': 1}, processes=['proc1'], instances=defaultdict(list, {'proc1': ['inst1']}))
    config2 = Configuration({'p2': 1}, processes=['proc1'], instances=defaultdict(list, {'proc1': ['inst1']}))
    event1 = Event('proc1', 'inst1', 'A')
    edge1 = LabelledEdge(event1)

    lts.add_edge(config1, config2, edge1)

    # Define data configurations
    data_configurations = {config1}

    # Get prefix
    prefix = LTSUtil.get_prefix(lts, data_configurations, config2)

    # Print results
    for proc in prefix:
        for inst in prefix[proc]:
            trace = prefix[proc][inst]
            events = [e.label for e in trace.events]
            print(f"Process: {proc}, Instance: {inst}, Events: {events}")

if __name__ == "__main__":
    main()

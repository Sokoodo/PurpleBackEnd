from pm4py.objects.log.obj import EventLog, Trace
from werkzeug.datastructures import FileStorage

from purple.evaluator.delta import Delta
from purple.evaluator.log_evaluator.log_evaluator_or.log_evaluator_or import LogEvaluator, ILogEvaluator
from purple.model_manager import bpmn_model_manager
from purple.semantic_engine.i_semantic_engine import ISemanticEngine
from purple.semantic_engine.or_semantic_engine import PetriSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.simulator.or_simulator import OrSimulator
from purple.evaluator.trace_evaluator.trace_evaluator import TraceEvaluator, ITraceEvaluator
from purple.util.lts_utils import show_lts


def purple_routine(se: ISemanticEngine, sim: ISimulator, le: ILogEvaluator, te: ITraceEvaluator, tau: int):
    simple_traces = []
    event_log: EventLog = EventLog()
    initial_marking = se.get_initial_marking()
    state_mapping = sim.initialize_lts(initial_marking)

    # Debug: Initial Marking and State Mapping
    print(f"Initial State Mapping: {state_mapping}")

    state_mapping, st = sim.global_simulate(None, initial_marking, state_mapping)
    simple_traces.extend(st)

    delta = le.evaluate(simple_traces, tau)
    print(f"Initial Delta Missing: {delta.get_missing()}")

    print("Simple Traces After Initial Simulation:")
    print(simple_traces)
    while delta and not delta.is_empty():
        for delta_trace in delta.get_missing():
            state_mapping, temp_guided_traces = sim.global_simulate(delta_trace, initial_marking, state_mapping)
            simple_traces.extend(temp_guided_traces)  # Use extend to add lists of events
            # Debug: Trace the new traces and delta
            print(f"New Guided Traces: {temp_guided_traces}")
            print(f"State Mapping: {state_mapping}")
            delta = le.evaluate(simple_traces, tau)
            print(f"Updated Delta Missing: {delta.get_missing()}")
            if delta.is_empty():
                print("Delta is empty, breaking loop.")
                break
        delta = le.evaluate(simple_traces, tau)

    print("Final Simple Traces:")
    print(simple_traces)

    for trace in simple_traces:
        event_log.append(trace)

    show_lts(sim.get_lts_graph())
    return event_log


def remove_duplicate_traces(event_log: EventLog) -> EventLog:
    unique_traces = set()
    new_event_log = EventLog()

    for trace in event_log:
        # Represent the trace as a tuple of event names to check for uniqueness
        trace_tuple = tuple(event["marking:name"] for event in trace)

        if trace_tuple not in unique_traces:
            unique_traces.add(trace_tuple)
            new_event_log.append(trace)

    return new_event_log


def order_relation(file: FileStorage, tau: int, instance_path):
    net, initial_marking, final_marking = bpmn_model_manager.load_model(file, instance_path)
    # pm4py.view_petri_net(net, initial_marking, final_marking)
    # print(net, initial_marking, final_marking)

    if net is [] or net is None:
        return None
        # print(net)
    le = LogEvaluator(net)
    te = TraceEvaluator()
    se = PetriSemanticEngine(net)
    sim = OrSimulator(se, te)
    return purple_routine(se, sim, le, te, tau)


def custom_noise(file, slider_value):
    pass


def traces_frequency(file, slider_value):
    pass


def alignment_cost(file, slider_value):
    pass

from pm4py.objects.log.obj import EventLog, Trace
from werkzeug.datastructures import FileStorage

from purple.evaluator.delta import Delta
from purple.evaluator.log_evaluator.log_evaluator_or.log_evaluator_or import LogEvaluator, ILogEvaluator, \
    find_unmatched_paths
from purple.model_manager import bpmn_model_manager
from purple.semantic_engine.i_semantic_engine import ISemanticEngine
from purple.semantic_engine.or_semantic_engine import PetriSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.simulator.or_simulator import OrSimulator
from purple.evaluator.trace_evaluator.trace_evaluator import TraceEvaluator, ITraceEvaluator
from purple.util.lts_utils import show_lts, create_events_from_paths


def or_purple_routine(se: ISemanticEngine, sim: ISimulator, le: ILogEvaluator, te: ITraceEvaluator, tau: int):
    simple_traces = []
    event_log: EventLog = EventLog()
    initial_marking = se.get_initial_marking()
    state_mapping = sim.initialize_lts(initial_marking)

    # Debug: Initial Marking and State Mapping
    print(f"Initial State Mapping: {state_mapping}")

    state_mapping, st = sim.global_simulate(None, initial_marking, state_mapping)
    simple_traces.extend(st)

    delta, tau_interruption = le.evaluate(simple_traces, tau)
    print(f"Initial Delta Missing: {delta.get_missing()}")

    print("Simple Traces After Initial Simulation:")
    print(simple_traces)
    while delta and not delta.is_empty():
        for delta_trace in delta.get_missing():
            state_mapping, temp_guided_traces = sim.global_simulate(delta_trace, initial_marking, state_mapping)
            for temp_guided_trace in temp_guided_traces:
                for trace in simple_traces:
                    if not are_traces_equal(trace, temp_guided_trace):
                        simple_traces.extend(temp_guided_traces)  # Use extend to add lists of events
            # Debug: Trace the new traces and delta
            print(f"New Guided Traces: {temp_guided_traces}")
            print(f"State Mapping: {state_mapping}")
            delta, tau_interruption = le.evaluate(simple_traces, tau)
            print(f"Updated Delta Missing: {delta.get_missing()}")
            if delta.is_empty():
                print("Delta is empty, breaking loop.")
                break

    if not tau_interruption:
        all_paths = le.get_all_paths_from_petri()
        print(f"All_paths: {all_paths}")
        print(f"Simple Traces: {simple_traces}")
        unmatched_paths = find_unmatched_paths(all_paths, simple_traces)
        print(f"unmatched_paths: {unmatched_paths}")
        unmatched_traces = create_events_from_paths(unmatched_paths)
        for unmatched_trace in unmatched_traces:
            for trace in simple_traces:
                if not are_traces_equal(trace, unmatched_trace):
                    simple_traces.extend(unmatched_trace)
        print(f"Final Simple Traces: {simple_traces}")

    for trace in simple_traces:
        event_log.append(trace)

    show_lts(sim.get_lts_graph())
    return event_log


def are_traces_equal(trace1, trace2):
    """
    Compare two Trace objects for equality.
    """
    if len(trace1) != len(trace2):
        return False

    for event1, event2 in zip(trace1, trace2):
        if event1['concept:name'] != event2['concept:name']:
            return False
        if event1['time:timestamp'] != event2['time:timestamp']:
            return False
        if event1['marking'] != event2['marking']:
            return False

    return True


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
    return or_purple_routine(se, sim, le, te, tau)


def custom_noise(file, cost, precision, traces_number, instance_path):
    net, initial_marking, final_marking = bpmn_model_manager.load_model(file, instance_path)
    if net is [] or net is None:
        return None
    le = LogEvaluator(net)
    te = TraceEvaluator()
    se = PetriSemanticEngine(net)
    sim = OrSimulator(se, te)
    return EventLog()


def traces_frequency(file, slider_value):
    pass


def alignment_cost(file, slider_value):
    pass

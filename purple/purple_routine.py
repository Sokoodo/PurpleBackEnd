import pm4py
from pm4py.objects.log.obj import EventLog
from pm4py.visualization.powl.variants import net
from werkzeug.datastructures import FileStorage

from purple.evaluator.log_evaluator.cn_log_evaluator.cn_log_evaluator import CnLogEvaluator
from purple.evaluator.log_evaluator.or_log_evaluator.or_log_evaluator import LogEvaluatorOr, ILogEvaluator, \
    find_unmatched_paths
from purple.model_manager.model_manager import load_model
from purple.semantic_engine.i_semantic_engine import ISemanticEngine
from purple.semantic_engine.petri_semantic_engine import PetriSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.simulator.main_simulator import Simulator
from purple.evaluator.trace_evaluator.trace_evaluator import TraceEvaluator, ITraceEvaluator
from purple.util.event_log_utils import are_traces_equal
from purple.util.lts_utils import show_lts, create_events_from_paths


def order_relation(file: FileStorage, tau: int, instance_path):
    net, initial_marking, final_marking = load_model(file, instance_path)
    pm4py.view_petri_net(net, initial_marking, final_marking)
    # print(net, initial_marking, final_marking)

    if net is [] or net is None:
        return None
    le = LogEvaluatorOr(net)
    te = TraceEvaluator()
    se = PetriSemanticEngine(net)
    sim = Simulator(se, te)
    return or_purple_routine(se, sim, le, te, tau)


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


def custom_noise(file, traces_number, missing_head, missing_tail, missing_episode, order_perturbation, alien_activities,
                 instance_path):
    net, initial_marking, final_marking = load_model(file, instance_path)
    # pm4py.view_petri_net(net, initial_marking, final_marking)
    # print(net, initial_marking, final_marking)
    if net is [] or net is None:
        return None
    le = CnLogEvaluator(traces_number, missing_head, missing_tail, missing_episode,
                        order_perturbation, alien_activities)
    te = TraceEvaluator()
    se = PetriSemanticEngine(net)
    sim = Simulator(se, te)

    return cn_purple_routine(se, sim, le, te, traces_number)


def cn_purple_routine(se: ISemanticEngine, sim: ISimulator, le: ILogEvaluator, te: ITraceEvaluator, traces_number: int):
    simple_traces = []
    event_log: EventLog = EventLog()
    initial_marking = se.get_initial_marking()
    state_mapping = sim.initialize_lts(initial_marking)

    if net is [] or net is None:
        return None

    for i in range(traces_number):
        state_mapping, random_traces = sim.random_simulation(initial_marking, state_mapping)
        simple_traces.extend([random_traces])

    event_log = le.evaluate(simple_traces)

    # show_lts(sim.get_lts_graph())
    return event_log


def traces_frequency(file, slider_value):
    pass


def alignment_cost(file, slider_value):
    pass

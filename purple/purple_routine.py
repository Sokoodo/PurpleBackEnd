from pm4py import PetriNet, Marking
from pm4py.objects.log.obj import EventLog
from werkzeug.datastructures import FileStorage

from purple.evaluator.delta import Delta
from purple.evaluator.log_evaluator.log_evaluator_or.alpha_relations import AlphaRelations
from purple.evaluator.log_evaluator.log_evaluator_or.log_evaluator_or import LogEvaluator, ILogEvaluator
from purple.model_manager import bpmn_model_manager
from purple.model_manager.bpmn_model_manager import save_file_get_path
from purple.semantic_engine.i_semantic_engine import ISemanticEngine
from purple.semantic_engine.or_semantic_engine import OrSemanticEngine
from purple.simulator.i_simulator import ISimulator
from purple.simulator.or_simulator import OrSimulator
from purple.evaluator.trace_evaluator.trace_evaluator import TraceEvaluator, ITraceEvaluator


def purple_routine(se: ISemanticEngine, sim: ISimulator, le: ILogEvaluator, te: ITraceEvaluator, tau: int):
    event_log: EventLog = EventLog()

    for trace in sim.global_simulate(None):
        event_log.append(trace)
        # print("eventLog")
        # print(event_log)
    delta: Delta = le.evaluate(event_log, tau)
    # while not delta.is_empty():
    for trace in sim.global_simulate(delta):
        event_log.append(trace)
    #     delta = le.evaluate(event_log, tau)

    # event_log_footprint_matrix = ar.get_footprint_matrix_from_event_log(event_log)
    # print(le.get_footprint_matrix())
    # print(event_log_footprint_matrix)
    # delta = ar.compare_footprint_matrices(event_log_footprint_matrix, le.get_footprint_matrix(), tau )
    # print(delta.get_missing())
    new_event_log = remove_duplicate_traces(event_log)
    sim.show_lts()
    return new_event_log


def remove_duplicate_traces(event_log: EventLog) -> EventLog:
    unique_traces = set()
    new_event_log = EventLog()

    for trace in event_log:
        # Represent the trace as a tuple of event names to check for uniqueness
        trace_tuple = tuple(event["concept:name"] for event in trace)

        if trace_tuple not in unique_traces:
            unique_traces.add(trace_tuple)
            new_event_log.append(trace)

    return new_event_log


def order_relation(file: FileStorage, tau: int, instance_path):
    net: PetriNet = PetriNet()
    initial_marking: Marking
    final_marking: Marking
    if file.filename.endswith('.bpmn') or file.filename.endswith('.pnml'):
        if file.filename.endswith('.bpmn'):
            new_path = save_file_get_path(file, instance_path, '../bpmn_model.bpmn')
            net, initial_marking, final_marking = bpmn_model_manager.read_bpmn_from_file(new_path)
            # print(net, initial_marking, final_marking)
        elif file.filename.endswith('.pnml'):
            new_path = save_file_get_path(file, instance_path, '../pnml_model.pnml')
            net, initial_marking, final_marking = bpmn_model_manager.read_petri_net_from_file(new_path)
            # pm4py.view_petri_net(net, initial_marking, final_marking)
            # print(net, initial_marking, final_marking)

        if net is [] or net is None:
            return None
        # print(net)
        le = LogEvaluator(net)
        te = TraceEvaluator()
        se = OrSemanticEngine(net)
        sim = OrSimulator(se, te)
        return purple_routine(se, sim, le, te, tau)
    else:
        return None


def custom_noise(file, slider_value):
    pass


def traces_frequency(file, slider_value):
    pass


def alignment_cost(file, slider_value):
    pass

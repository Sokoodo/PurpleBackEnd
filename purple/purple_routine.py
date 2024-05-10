import pm4py
from pm4py import PetriNet, Marking
from pm4py.objects.log.obj import EventLog
from werkzeug.datastructures import FileStorage

from purple.log_evaluator.log_evaluator import LogEvaluator, ILogEvaluator
from purple.model_manager import bpmn_model_manager
from purple.model_manager.bpmn_model_manager import save_file_get_path
from purple.semantic_engine.semantic_engine import SemanticEngine, ISemanticEngine
from purple.simulator.simulator import Simulator, ISimulator
from purple.trace_evaluator.trace_evaluator import TraceEvaluator, ITraceEvaluator


def purple_routine(se: ISemanticEngine, sim: ISimulator, le: ILogEvaluator, te: ITraceEvaluator):
    delta: [] = []
    event_log: EventLog = sim.global_simulate(delta)
    print(se.get_initial_state())
    # while delta is not []:
        # print("c")
        # sim.global_simulate(delta)
        # delta = le.evaluate(event_log, delta)

    return event_log


def order_relation(file: FileStorage, slider_value: str, instance_path):
    net: PetriNet = PetriNet()
    initial_marking: Marking
    final_marking: Marking
    if file.filename.endswith('.bpmn') or file.filename.endswith('.pnml'):
        if file.filename.endswith('.bpmn'):
            new_path = save_file_get_path(file, instance_path, '../bpmn_model.bpmn')
            net, initial_marking, final_marking = bpmn_model_manager.read_bpmn_from_file(new_path)
            print(net, initial_marking, final_marking)
        elif file.filename.endswith('.pnml'):
            new_path = save_file_get_path(file, instance_path, '../pnml_model.pnml')
            net, initial_marking, final_marking = bpmn_model_manager.read_petri_net_from_file(new_path)
            # pm4py.view_petri_net(net, initial_marking, final_marking)
            print(net, initial_marking, final_marking)

        if net is [] or net is None:
            return None
        le = LogEvaluator()
        te = TraceEvaluator()
        se = SemanticEngine(net)
        sim = Simulator(se, te)
        return purple_routine(se, sim, le, te)
    else:
        return None


def custom_noise(file, slider_value):
    pass


def traces_frequency(file, slider_value):
    pass


def alignment_cost(file, slider_value):
    pass

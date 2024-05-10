import os

import pm4py
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def read_petri_net_from_file(filename):
    try:
        pn_temp_graph = pm4py.read.read_pnml(filename)
        return pn_temp_graph
    except Exception as e:
        print("Error:", e)
        return None


def read_bpmn_from_file(filename):
    try:
        bpmn_temp_graph = pm4py.read.read_bpmn(filename)
        net, im, fm = pm4py.convert_to_petri_net(bpmn_temp_graph)
        return net, im, fm
    except Exception as e:
        print("Error:", e)
        return None


def save_file_get_path(file: FileStorage, instance_path, filename: str):
    file.stream.seek(0)
    new_path = os.path.join(instance_path, secure_filename(filename))
    file.save(new_path)
    return new_path



#
#
# def print_bpmn_elements(bpmn_graph):
#     nodes = pm4py.BPMN.get_nodes(bpmn_graph)
#     flows = pm4py.BPMN.get_flows(bpmn_graph)
#     print("\nNodes:")
#     for node in nodes:
#         print(node)
#
#     print("\nFlows:")
#     for flow in flows:
#         print(flow)
#
#
# def convert_model_to_event_log(model_representation):
#     # Convert the model representation to a BPMN graph object
#     bpmn_graph = model_representation
#
#     # Simulate the execution of the process model to generate an event log
#     event_log = pm4py.sim.play_out(bpmn_graph)
#
#     return event_log

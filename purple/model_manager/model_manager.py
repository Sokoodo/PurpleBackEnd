import os

import pm4py
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def load_model(file, instance_path):
    if file.filename.endswith('.pnml'):
        new_path = save_file_get_path(file, instance_path, '../pnml_model.pnml')
        net, initial_marking, final_marking = pm4py.read.read_pnml(new_path)
    elif file.filename.endswith('.bpmn'):
        new_path = save_file_get_path(file, instance_path, '../bpmn_model.bpmn')
        bpmn_model = pm4py.read.read_bpmn(new_path)
        net, initial_marking, final_marking = pm4py.convert_to_petri_net(bpmn_model)
    else:
        raise ValueError("Unsupported file format. Only .pnml and .bpmn are supported.")
    return net, initial_marking, final_marking


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

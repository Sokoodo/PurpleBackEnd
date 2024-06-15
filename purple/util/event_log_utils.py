import json

from flask import jsonify
from pm4py.objects.log.obj import EventLog


def event_log_to_json(event_log: EventLog):
    log_dict = []
    for trace in event_log:
        trace_dict = {
            "attributes": trace.attributes,
            "events": []
        }
        for event in trace:
            event_dict = {
                "attributes": dict(event)  # Convert event to a dictionary
            }
            trace_dict["events"].append(event_dict)
        log_dict.append(trace_dict)
    return jsonify(log_dict)

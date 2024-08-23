from flask import jsonify  # Assuming you're using Flask for JSON serialization


def event_log_to_json(event_log):
    log_dict = []
    for trace in event_log:
        trace_dict = {
            "attributes": trace.attributes,
            "events": [],
        }
        for event in trace:
            # Convert event to a dictionary by accessing its attributes
            event_dict = {key: value for key, value in event.items()}
            trace_dict["events"].append(event_dict)
        log_dict.append(trace_dict)
    return jsonify(log_dict)

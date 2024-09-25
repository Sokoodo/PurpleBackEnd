from flask import jsonify


def event_log_to_json(event_log):
    """
    Translates event log to json
    """
    log_dict = []
    for trace in event_log:
        trace_dict = {
            "attributes": trace.attributes if hasattr(trace, 'attributes') else {},  # Check if attributes exist
            "events": [],
        }
        for event in trace:
            # Convert event to a dictionary by accessing its attributes
            event_dict = {key: value for key, value in event.items()}
            trace_dict["events"].append(event_dict)
        log_dict.append(trace_dict)
    return jsonify(log_dict)


def are_traces_equal(trace1, trace2):
    """
    Compare two Trace objects for equality.
    """
    if len(trace1) != len(trace2):
        return False

    for event1, event2 in zip(trace1, trace2):
        if event1['concept:name'] != event2['concept:name']:
            return False
        if event1['marking'] != event2['marking']:
            return False

    return True


def remove_duplicate_traces(traces):
    """
    Remove duplicate traces and return a list of new unique traces.
    """
    unique_traces = []
    unique_trace_names = []

    for trace in traces:
        event_names = [event["concept:name"] for event in trace]

        if event_names not in unique_trace_names:
            unique_traces.append(trace)
            unique_trace_names.append(event_names)

    return unique_traces

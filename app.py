import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from purple import purple_routine
from purple.util.event_log_utils import event_log_to_json

UPLOAD_FOLDER = '/path/to/the/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)
cors = CORS(app, resource={
    r"/*": {
        "origins": "*"
    }
})


@app.route('/api/order-relation/event-log', methods=['POST'])
def order_relation():
    """
    Order Relation API, to get the event log with all the traces below the specified threshold

    :return: event log with all the traces
    """
    start_time = time.time()
    file = request.files['singleFile']
    slider_value = int(request.args.get('sliderValue'))
    event_log = purple_routine.order_relation(file, slider_value, app.instance_path[:-9])

    file_name = secure_filename(file.filename)
    if event_log is None:
        return ["Problem with event log generation", ]
    # print(file.filename)
    else:
        end_time = time.time()  # End timer
        execution_time = end_time - start_time  # Calculate the difference

        print(f"Execution time: {execution_time:.4f} seconds")
        return event_log_to_json(event_log)


@app.route('/api/custom-noise/event-log', methods=['POST'])
def custom_noise():
    """
    Custom Noise API, to get a list of desired traces and also adding the required noisy traces to the final Event Log

    :return: the final event log with noisy traces
    """
    start_time = time.time()
    file = request.files['singleFile']
    traces_number = int(request.args.get('tracesNumber'))

    missing_head = float(request.args.get('missingHead'))
    missing_tail = float(request.args.get('missingTail'))
    missing_episode = float(request.args.get('missingEpisode'))
    order_perturbation = float(request.args.get('orderPerturbation'))
    alien_activities = float(request.args.get('alienActivities'))
    event_log = purple_routine.custom_noise(file, traces_number, missing_head, missing_tail, missing_episode,
                                            order_perturbation, alien_activities, app.instance_path[:-9])

    file_name = secure_filename(file.filename)
    if event_log is None:
        return ["Problem with event log generation", ]
    # print(file.filename)
    else:
        print(len(event_log))
        end_time = time.time()  # End timer
        execution_time = end_time - start_time  # Calculate the difference

        print(f"Execution time: {execution_time:.4f} seconds")
        return event_log_to_json(event_log)


if __name__ == '__main__':
    app.run()

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
def upload_graph():
    file = request.files['singleFile']
    slider_value = int(request.args.get('sliderValue'))
    event_log = purple_routine.order_relation(file, slider_value, app.instance_path[:-9])

    file_name = secure_filename(file.filename)
    if event_log is None:
        return ["Problem with event log generation", ]
    # print(file.filename)
    else:
        return "ciao"
        # return event_log_to_json(event_log)


if __name__ == '__main__':
    app.run()

from flask import Flask, request, jsonify
# import json
# import requests
# from requests.exceptions import HTTPError
# import pandas as pd
# import datetime
# import subprocess
import time
import logging
import threading
from api_handler import Translator

translator_api = Translator()

# Global variables to track last API call time and EC2 state
last_api_call_time = time.time()
ec2_idle_time = None

ec2_state = translator_api.ec2_state

app = Flask(__name__)


# Set up logging
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - [Thread %(thread)d] - %(message)s'
    )
    # Remove all handlers associated with the root logger object
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Add your own handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [Thread %(thread)d] - %(message)s')
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)



# Set up logging
# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s -  [Thread %(thread)d] - %(message)s')

setup_logging()
logger = logging.getLogger(__name__)




def reset_ec2_idle_time():
    global last_api_call_time
    #global ec2_idle_time
    #ec2_idle_time = time.time()
    
    last_api_call_time = time.time()
    logging.info(f"Resetting ec2_idle time...")


def monitor_api_calls():
    global last_api_call_time
    idle_time_limit = 15*60 #15minutes
    while True:
        current_time = time.time()
        ec2_idle_time = current_time - last_api_call_time
        # if current_time - last_api_call_time > 900:  # 15 minutes (900 seconds)

        if ec2_idle_time > idle_time_limit:
            if ec2_state == "running":
                translator_api.stop_ec2() #stop_ec2()
                logger.info(f"EC2 {translator_api.ec2_id} is stopped due to inactivity for 15 minutes.")
        
        time.sleep(5)  # Check every 5s
        message = f"Monitor Thread : EC2 {translator_api.api_ec2_id} is idle for {int(ec2_idle_time)}/{idle_time_limit} seconds"
        logger.info(message)


@app.route("/") #healthcheck
def health_check():
    message,status = translator_api.health_check()
    response = {"message":message,
            "status" : status}
    return jsonify(response),200
     

@app.route("/get_ec2_details")
def get_ec2_details():
    message, status = translator_api.get_ec2_details()
    response = {"message" : message,
                "status": status}
    return jsonify(response), 200

@app.route("/start_ec2")
def start_ec2():
    message, status = translator_api.start_ec2()
    response = {"message" : message,
                "status": status}
    return jsonify(response), 200

@app.route("/stop_ec2")
def stop_ec2():
    message, status = translator_api.stop_ec2()
    response = {"message" : message,
                "status": status}
    return jsonify(response), 200

@app.route("/translate")
def translate():
    message = f"Invalid Request! Please make POST request. For more details refer the documentation..."
    status = "success"
    response = {"message" : message,
                 "status": status}
    return jsonify(response), 200

@app.route("/translate", methods = ["POST"])
def translate_texts():

    reset_ec2_idle_time()

    input_data = request.get_json()
    if not isinstance(input_data, list) or not all(isinstance(item, str) for item in input_data):
            message = "Invalid input format. Expected a list of strings."
            return jsonify({"error": message}), 400
    
    #input_data_format = request.args.get("format")
    #translate_direction = request.args.get("direction")

    params = {
         "input_data_format" : request.args.get("format"),
         "input_data": input_data,
         "translate_direction" : request.args.get("direction")
    }

    message, status = translator_api.translate(params=params)

    return jsonify({"message": message, "status": status}), 200
    


#post_request
@app.route("/post_req", methods = ["POST"])
def post_req():
    data = request.get_json()

    return jsonify(data), 200


def run_flask_app():
    app.run(debug=True, port=5050)

if __name__ == "__main__":

    # Start monitoring API calls in a separate thread
    threading.Thread(target=monitor_api_calls).start()
    # monitor_thread.start()

    run_flask_app()


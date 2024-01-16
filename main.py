from flask import Flask, request
import requests
import json
from wrike import Project
from translator import get_objects_translator, get_status_translator
from access_tokens import get_access_token
from handlers import home, respond, respond_wrike, handle_auth
import threading

app = Flask(__name__)

# These variables will store the access token and refresh token
access_token = None
refresh_token = None

lock = threading.Lock()
# home page
@app.route('/')
def home_route():
    return home()


# Listen when a deal stage is "Offer elaboration" and creates a project in Wrike with the same stage.
@app.route('/webhook', methods=['POST'])
def respond_route():
    with lock:
        return respond()

@app.route('/wrikelistener', methods=['POST'])
def respond_wrike_route():
    with lock:
        return respond_wrike()

@app.route('/auth', methods=['GET'])
def handle_auth_route():
    return handle_auth()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

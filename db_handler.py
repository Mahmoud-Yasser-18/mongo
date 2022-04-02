# https://askubuntu.com/questions/1379425/system-has-not-been-booted-with-systemd-as-init-system-pid-1-cant-operate
# sudo -b unshare --pid --fork --mount-proc /lib/systemd/systemd --system-unit=basic.target
# sudo -E nsenter --all -t $(pgrep -xo systemd) runuser -P -l $USER -c "exec $SHELL"

from pymongo import MongoClient
from random import randint

from flask              import Flask, request
from flask_cors         import CORS
import flask
import json





def flask_resp(*, message_dict=None, resp_code, headers_opt=0):
    resp = None
    if message_dict:
        resp = flask.Response(json.dumps(message_dict), status=resp_code) 
    else:
        resp = flask.Response(status=resp_code)
    if headers_opt == 1:
        resp.headers['Content-Type'] = 'text/html'
    else:    
        resp.headers['Content-Type'] = 'application/json'
        resp.headers['Access-Control-Allow-Origin'] = "*"
        resp.headers['Access-Control-Allow-Headers'] = "*"
        resp.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PATCH, PUT'
    return resp




#Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient(port=27017)
db=client.players_info

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/health-check', methods=['GET'])
def health_check():
    resp = {
        'status': True, 
        'error': None, 
        'response': 'The server is up and running'
    }

    return flask_resp(resp_code=200, message_dict=resp)


@app.route('/login', methods=['POST'])
def login_api():
    contents = request.get_json(force=True)
    login_result = login(contents["email"],contents["password"])
    del login_result["data"]["_id"]
    print(login_result)
    return flask_resp(resp_code=200, message_dict=login_result)

@app.route('/signup', methods=['POST'])
def signup_api():
    contents = request.get_json(force=True)
    signup_result = signup(contents["email"],contents["password"])
    return flask_resp(resp_code=200, message_dict=signup_result)



def login(email,password):
    try:
        results = db.player_info.find({"email": email, "password": password})
        if results:
            return  {'available': True, 'explain': None, 'data': results[0]}
        return {'available': False, 'explain': 'No users found', 'data': None}
    except:
        return {'available': False, 'explain': "Couldn't retrieve from the database, check connections!", 'data': None}




def signup(email,password):
    is_already_available = user_exists(email)
    if is_already_available['available']:
        return {'created': False, 'error': 'user already available'}

    try:
        _ = db.player_info.insert_one({"email": email, "password": password})
        return {'created': True, 'error': None}
    except Exception as exp:
        return {'created': False, 'error': str(exp)}


def user_exists(email):
    try:
        results = db.player_info.find({"email": email})
        if results:
            return  {'available': True, 'explain': None, 'data': results[0]}
        return {'available': False, 'explain': 'No users found', 'data': None}
    except:
        return {'available': False, 'explain': "Couldn't retrieve from the database, check connections!", 'data': None}

if __name__ == "__main__":
    port = 5000
    app.run( host='0.0.0.0', port=port)

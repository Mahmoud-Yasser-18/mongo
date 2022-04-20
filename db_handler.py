# https://askubuntu.com/questions/1379425/system-has-not-been-booted-with-systemd-as-init-system-pid-1-cant-operate
# sudo -b unshare --pid --fork --mount-proc /lib/systemd/systemd --system-unit=basic.target
# sudo -E nsenter --all -t $(pgrep -xo systemd) runuser -P -l $USER -c "exec $SHELL"
# sudo systemctl start mongod
# sudo systemctl status mongod

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
db_store=client.store

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
    print("contents:")
    print(contents)
    login_result = login(contents["email"],contents["password"])
    if login_result["available"]:
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


def item_exists(item_name):
    try:
        results = db_store.item_info.find({"item_name": item_name})
        if results:
            return  {'available': True, 'explain': None, 'data': results[0]}
        return {'available': False, 'explain': 'No item found', 'data': None}
    except:
        return {'available': False, 'explain': "Couldn't retrieve from the database, check connections!", 'data': None}

def add_item(item_name,description, cost):
    is_already_available = item_exists(item_name)
    if is_already_available['available']:
        return {'created': False, 'error': 'user already available'}

    try:
        _ = db_store.item_info.insert_one({"item_name": item_name, "description": description,"cost": cost})
        return {'created': True, 'error': None}
    except Exception as exp:
        return {'created': False, 'error': str(exp)}

@app.route('/additem', methods=['POST'])
def additem():
    contents = request.get_json(force=True)
    added_item = add_item(contents["item_name"],contents["description"],contents["cost"])
    return flask_resp(resp_code=200, message_dict=signup_result)

@app.route('/listitems', methods=['GET'])
def list_all_items():
    items_list = db_store.item_info.find({})
    print(items_list)
    return items_list

if __name__ == "__main__":
    port = 5000
    app.run( host='0.0.0.0', port=port)

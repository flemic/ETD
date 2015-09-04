import protobuf_json
from flask import Flask, jsonify
from flask import Response
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask import make_response, request, current_app
import pymongo
from pymongo import Connection
from functools import wraps
from functools import update_wrapper
import json
import urllib2
from datetime import timedelta, datetime
import raw_data_pb2
import enriching_functionality as EF
import pprint
import time

# MongoDB setup
hostname = 'localhost'
port_number = 27017

def crossdomain(origin=None, methods=None, headers=None,
                max_age=201600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def get_coordinates_rssi(db_id,coll_id,transmitters):
    """ Given the database and collection IDs, function returns a list of measurment locations 
    (x,y) coordinates and the related RSSI measurments.  
    """

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")
      

    db_names = connection.database_names()
    if db_id in db_names:
        db = connection[db_id]
    else:
        return json.dumps("No such database!")  
    
    coll_names = db.collection_names()
    if coll_id in coll_names:
        collection = db[coll_id]
    else:
        return json.dumps("No such collection in the database!")
    
    try:
        message_collection = collection.find({})
    except:
        return json.dumps("Unable to read data from the collection!")

    message_collection_list = {}
    message_collection_list_full = list(message_collection)

    coordinates = []
    rssis = []
    for i in range(0,len(message_collection_list_full)):
        rssi_transmitter = {}
        coordinates.append((message_collection_list_full[i]['raw_measurement'][0]['receiver_location']['coordinate_x'],message_collection_list_full[i]['raw_measurement'][0]['receiver_location']['coordinate_y']))
        for meas in message_collection_list_full[i]['raw_measurement']:
            if meas['sender_bssid'] in transmitters:
                try:
                    rssi_transmitter[meas['sender_bssid']].append(meas['rssi'])
                except:
                    rssi_transmitter[meas['sender_bssid']] = []
                    rssi_transmitter[meas['sender_bssid']].append(meas['rssi'])
        rssis.append(rssi_transmitter)

    return coordinates,rssis

def store_virtual_fingerprints(db_id_original, coll_id_original, db_id_enriched, coll_id_enriched, points, virtual_fingerprints):
    """Store original and virtaul training fingerprint in the same database"""

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")
      
    db_names = connection.database_names()
    if db_id_original in db_names:
        db = connection[db_id_original]
    else:
        return json.dumps("No such database!")  
    
    coll_names = db.collection_names()
    if coll_id_original in coll_names:
        collection = db[coll_id_original]
    else:
        return json.dumps("No such collection in the database!")
    
    try:
        message_collection = collection.find({})
    except:
        return json.dumps("Unable to read data from the collection!")

    message_collection_list = {}
    message_collection_list_full = list(message_collection)

    if db_id_enriched in db_names:
        db = connection[db_id_enriched]
    else:
        return json.dumps("No such database!")  
    
    coll_names = db.collection_names()
    if coll_id_enriched in coll_names:
        collection = db[coll_id_enriched]
    else:
            return json.dumps("No such collection in the database!")
    
    for i in range(0,len(message_collection_list_full)):
        try:
            del message_collection_list_full[i]['_id']
            collection.insert(message_collection_list_full[i])
        except:
            return json.dumps("Unable to store data into the database!")

    data_id_virtual = len(message_collection_list_full) + 1

    iteration = 0
    for point in points:
        raw_data_collection = raw_data_pb2.RawRFReadingCollection()
        raw_data_collection.data_id = str(data_id_virtual)
        data_id_virtual += 1
        raw_data_collection.meas_number = message_collection_list_full[0]['meas_number']
        for key in virtual_fingerprints[iteration].keys():
            for num in range(0,len(virtual_fingerprints[iteration][key])):
                raw_data_reading = raw_data_collection.raw_measurement.add()
                x = datetime.utcnow()
                raw_data_reading.timestamp_utc = timestamp_utc = int(time.mktime(x.timetuple()))
                raw_data_reading.receiver_location.coordinate_x = point[0]
                raw_data_reading.receiver_location.coordinate_y = point[1]
                raw_data_reading.run_nr = num + 1
                raw_data_reading.sender_bssid = key
                raw_data_reading.rssi = float(virtual_fingerprints[iteration][key][num])
        iteration += 1
        try:
            collection.insert(protobuf_json.pb2json(raw_data_collection))
        except:
            collection.insert(message_backup)
            return json.dumps("Unable to store data into the collection!")

    return json.dumps('Data stored!')

app = Flask(__name__)

#######################################################################################################
# Home - Hello World! I'm alive!!!!!
#######################################################################################################
@app.route("/")
@crossdomain(origin='*')
def hello():
    response = {'EVARILOS welcomes you!': 'This is a prototype of the webservices for the EVARILOS project',
                'Databases': url_for("databases", _external = True)}
    return json.dumps(response)


#######################################################################################################
# Task 1: Get the list of all databases [GET]
#######################################################################################################
@app.route('/etd/v1.0/database', methods = ['GET'])
@crossdomain(origin='*')
def databases():

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")
      
    db_names = connection.database_names() 
    db_list = {}
    for iter_id in db_names:
        if iter_id != 'local':
            if iter_id != 'admin':
                db_list[iter_id] = url_for("database", db_id = iter_id, _external = True)
    return json.dumps(db_list)


#######################################################################################################
# Task 2: Get the list of all collections in the database [GET]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection', methods = ['GET'])
@crossdomain(origin='*')
def database(db_id):

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")
    
    db_names = connection.database_names()
    if db_id in db_names:
        db = connection[db_id]
    else:
        return json.dumps("No such database!")

    coll_names = db.collection_names()
    coll_list = {}
    for iter_id in coll_names:
        if iter_id != 'system.indexes':
            coll_list[iter_id] = url_for("collection", db_id = db_id, coll_id = iter_id, _external = True)
    return json.dumps(coll_list)


#######################################################################################################
# Task 3: Get the list of messages description from the collection [GET]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>/message', methods = ['GET'])
@crossdomain(origin='*')
def collection(db_id, coll_id):

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")
      

    db_names = connection.database_names()
    if db_id in db_names:
        db = connection[db_id]
    else:
        return json.dumps("No such database!")  
    
    coll_names = db.collection_names()
    if coll_id in coll_names:
        collection = db[coll_id]
    else:
        return json.dumps("No such collection in the database!")
    
    try:
        message_collection = collection.find({})
    except:
        return json.dumps("Unable to read data from the collection!")
    
    message_collection_list = {}
    message_collection_list_full = list(message_collection)
    
    for i in range(0,len(message_collection_list_full)):
        message_collection_list[i] = {}
        message_collection_list[i]['_id'] = str(message_collection_list_full[i]['_id'])
        message_collection_list[i]['data_id'] = message_collection_list_full[i]['data_id']
        message_collection_list[i]['URI'] = url_for("message", db_id = db_id, coll_id = coll_id, data_id = message_collection_list_full[i]['data_id'], _external = True)

    return json.dumps(message_collection_list)


#######################################################################################################
# Task 4: Get the message from the collection [GET]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>/message/<data_id>', methods = ['GET'])
@crossdomain(origin='*')
def message(db_id, coll_id, data_id): 

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")
      
    db = connection[db_id]   
    collection = db[coll_id]
    
    try:
        message_collection = collection.find_one({'data_id':data_id})
    except:
        return json.dumps("Unable to read data from the collection!")
    
    if message_collection is None:
        return json.dumps("No data with this ID in the collection!")
    
    message_collection['_id'] = str(message_collection['_id'])

    if request.data == 'protobuf':
        try:
            pb_message = protobuf_json.json2pb(raw_data_pb2.RawRFReadingCollection(), message_collection)
        except:
            return json.dumps("Unable to read message from the collection!")
        pb_message_string = pb_message.SerializeToString()
        return pb_message_string
    else:
        return json.dumps(message_collection)


#######################################################################################################
# Task 5: Add a message into the collection [POST]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>', methods = ['POST'])
@crossdomain(origin='*')
def store_message(db_id, coll_id):

    try:
        raw_data_collection = raw_data_pb2.RawRFReadingCollection()
        raw_data_collection.ParseFromString(request.data)
    except:
        return json.dumps('Message is not well formated!')
    
    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")

    db_names = connection.database_names()
    if db_id in db_names:
        db = connection[db_id]
    else:
        return json.dumps("No such database!")  
    
    coll_names = db.collection_names()
    if coll_id in coll_names:
        collection = db[coll_id]
    else:
        return json.dumps("No such collection in the database!")
    
    try:
        collection.insert(protobuf_json.pb2json(raw_data_collection))
    except:
        return json.dumps("Unable to store data into the database!")

    return json.dumps('Data stored!')

#######################################################################################################
# Task 6: Creating a new collection in the database [POST]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection', methods = ['POST'])
@crossdomain(origin='*')
def create_collection(db_id):
    
    coll_id = request.data

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")

    db_names = connection.database_names()
    if db_id in db_names:
        db = connection[db_id]
    else:
        return json.dumps("No such database!")  
    
    coll_names = db.collection_names()
    if coll_id in coll_names:
        return json.dumps("Collection already exists!")
    
    try:
        db.create_collection(coll_id)
    except:
        return json.dumps("Unable to create a collection")

    return json.dumps('Collection successfully created!')

#######################################################################################################
# Task 7: Creating a new database [POST]
#######################################################################################################
@app.route('/etd/v1.0/database', methods = ['POST'])
@crossdomain(origin='*')
def create_database():
    
    db_id = request.data

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")

    db_names = connection.database_names()
    if db_id in db_names:
        return json.dumps("Database already exists!")  
    
    try:
        db = connection[db_id]
        coll = db.create_collection('test_tmp')
    except:
        return json.dumps("Unable to create new database")

    db.test_tmp.drop()
    return json.dumps('Database successfully created!')


#######################################################################################################
# Task 8: Delete the database [DELETE]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>', methods = ['DELETE'])
@crossdomain(origin='*')
def delete_database(db_id):

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")


    db_names = connection.database_names()
    if db_id not in db_names:
        return json.dumps("Database doesn't exist!")  
    
    try:
        connection.drop_database(db_id)
    except:
        return json.dumps("Unable to delete the database")

    return json.dumps('Database successfully deleted!')


#######################################################################################################
# Task 9: Delete the collection from the database [DELETE]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>', methods = ['DELETE'])
@crossdomain(origin='*')
def delete_collection(db_id, coll_id):

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")


    db_names = connection.database_names()
    if db_id not in db_names:
        return json.dumps("Database doesn't exist!")  
    
    db = connection[db_id]
    coll_names = db.collection_names()
    if coll_id not in coll_names:
        return json.dumps("Collection doesn't exist!")  

    try:
        db.drop_collection(coll_id)
    except:
        return json.dumps("Unable to delete the collection")

    return json.dumps('Collection successfully deleted!')


#######################################################################################################
# Task 10: Delete the mesage from the collection [DELETE]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>/message/<data_id>', methods = ['DELETE'])
@crossdomain(origin='*')
def delete_message(db_id, coll_id, data_id):

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")

    db_names = connection.database_names()
    if db_id not in db_names:
        return json.dumps("Database doesn't exist!")  
    
    db = connection[db_id]
    coll_names = db.collection_names()
    if coll_id not in coll_names:
        return json.dumps("Collection doesn't exist!")  

    collection = db[coll_id]
    try:
        collection.remove({"data_id": data_id})
    except:
        return json.dumps("Unable to delete the message")

    return json.dumps('Message successfully deleted!')

#######################################################################################################
# Task 11: Replace the message [PUT]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>/message/<data_id>', methods = ['PUT'])
@crossdomain(origin='*')
def replace_message(db_id, coll_id, data_id):

    raw_data_collection = raw_data_pb2.RawRFReadingCollection()
    raw_metadata = raw_metadata_pb2.Metadata()

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")

    try:
        raw_data_collection.ParseFromString(request.data)
    except:
        return json.dumps('Message is not well defined!')
    
    db_names = connection.database_names()
    if db_id not in db_names:
        return json.dumps("Database doesn't exist!")  
    
    db = connection[db_id]
    coll_names = db.collection_names()
    if coll_id not in coll_names:
        return json.dumps("Collection doesn't exist!")  

    collection = db[coll_id]
    
    try:
        message_collection = collection.find_one({'data_id':data_id})
    except:
        return json.dumps("Unable to read data from the collection!")
    
    if message_collection is None:
        return json.dumps("No data with this ID in the collection!")

    message_collection['_id'] = str(message_collection['_id'])
    message_backup = message_collection

    try:
        collection.remove({'data_id':data_id})
    except:
        collection.insert(message_backup)
        return json.dumps("Unable to read data from the database!")

    try:
        collection.insert(protobuf_json.pb2json(raw_data_collection))
    except:
        collection.insert(message_backup)
        return json.dumps("Unable to store data into the collection!")

    return json.dumps('Message successfully replaced!')


#######################################################################################################
# Task 12: Change the message parameters [PATCH]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>/message/<data_id>', methods = ['PATCH'])
@crossdomain(origin='*')
def change_message(db_id, coll_id, data_id):

    new_message_parameters = json.loads(request.data)
        
    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")

    db_names = connection.database_names()
    if db_id not in db_names:
        return json.dumps("Database doesn't exist!")  
    
    db = connection[db_id]
    coll_names = db.collection_names()
    if coll_id not in coll_names:
        return json.dumps("Collection doesn't exist!")  

    collection = db[coll_id]
    try:
        message_collection = collection.find_one({'data_id':data_id})
    except:
        return json.dumps("Unable to read data from the collection!")

    if message_collection is None:
        return json.dumps("No data with this ID in the collection!")

    message_collection['_id'] = str(message_collection['_id'])
    message_backup = message_collection

    for key in new_message_parameters.keys():   
        message_collection[key] = new_message_parameters[key]

    try:
        collection.remove({'data_id': data_id})
        collection.insert(message_collection)
    except:
        collection.insert(message_backup)
        return json.dumps("Unable to store data into the database!")

    return json.dumps('Message successfully replaced!')


#######################################################################################################
# Task 13: Change the collection name [PATCH]
#######################################################################################################
@app.route('/etd/v1.0/database/<db_id>/collection/<coll_id>', methods = ['PATCH'])
@crossdomain(origin='*')
def change_collection(db_id, coll_id):

    new_name = request.data

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")

    db_names = connection.database_names()
    if db_id not in db_names:
        return json.dumps("Database doesn't exist!")  
    
    db = connection[db_id]
    coll_names = db.collection_names()
    if coll_id not in coll_names:
        return json.dumps("Collection doesn't exist!")  
    if new_name in coll_names:
        return json.dumps("New name already exist!")

    collection = db[coll_id]
    try:
        collection.rename(new_name)
    except:
        return json.dumps("Unable to change the name of the collection!")
    return json.dumps("Collection's name changed!")

#######################################################################################################
# Task 14: Enriching functionality 
#######################################################################################################
@app.route('/etd/v1.0/<db_id_original>/<coll_id_original>/<db_id_enriched>/<coll_id_enriched>', methods = ['GET'])
@crossdomain(origin='*')
def generate_virutal_training_fingerprints(db_id_original, coll_id_original, db_id_enriched, coll_id_enriched):

    parameters = json.loads(request.data)

    # Connect to the database MongoDB
    try:
        connection = Connection(hostname, port_number)
    except:
        return json.dumps("Unable to connect to the database!")
      
    db_names = connection.database_names()
    if db_id_original in db_names:
        db1 = connection[db_id_original]
    else:
        return json.dumps("Database" + db_id_original + "doesn't exist!")
    
    if db_id_enriched in db_names:
        db2 = connection[db_id_enriched]
    else:
        return json.dumps("Database" + db_id_enriched + "doesn't exist!")      
    
    coll_names = db1.collection_names()
    if coll_id_original not in coll_names:
        return json.dumps("Collection" + Coll_id_original + "doesn't exist!")

    coll_names = db2.collection_names()
    if coll_id_enriched not in coll_names:
        return json.dumps("Collection" + coll_id_enriched + "doesn't exist!")

    coordinates,rssis = get_coordinates_rssi(db_id_original, coll_id_original, parameters['transmitters'])

    if parameters['define_virtual_points'] == 'User':
        points = EF.virtual_point_user()
    elif parameters['define_virtual_points'] == 'Voronoi':
        points = EF.virtual_point_modified_voronoi(coordinates)
    else:
        return json.dumps('Unknown method for the definition of virtual training points')

    if parameters['propagation_model'] == 'IDWI':
        virtual_fingerprints = EF.generate_virtual_fingerprints_idwi(coordinates, rssis, points, parameters['transmitters'])
        reply = store_virtual_fingerprints(db_id_original, coll_id_original, db_id_enriched, coll_id_enriched, points, virtual_fingerprints)
        return json.dumps(reply)

    elif parameters['propagation_model'] == 'Multiwall':
        pass
    else:
        return "Unknown method for the generation of virtual training fingerprints"

    return json.dumps("Something is wrong!")


#######################################################################################################
# Additional help functions
#######################################################################################################

# Error handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404) 

# Creating the URIs
def make_public_task(function):
    new_function = {}
    for field in function:
        if field == 'id':
            new_function['uri'] = url_for('get_function', function_id = function['id'], _external = True)
        else:
            new_function[field] = function[field]
    return new_function

# Enabling DELETE, PUT, etc.
class RequestWithMethod(urllib2.Request):
    """Workaround for using DELETE with urllib2"""
    def __init__(self, url, method, data=None, headers={}, origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self) 

#######################################################################################################
# Start the server on port 5000
#######################################################################################################


if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True, port = 5000)

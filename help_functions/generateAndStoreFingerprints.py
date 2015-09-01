#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""generateAndStoreFingerprints.py: Generate fingerprints from the stored raw WiFi RSSI 
measurements and store them in the ETD service."""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2015, Telecommunication Networks Group (TKN), TU Berlin"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"

import sys
import urllib2
from generateURL import RequestWithMethod
from datetime import datetime
from protobuf_json import json2pb
from scipy.stats.mstats import mquantiles
import numpy as np
import raw_data_pb2
import json
import time

# The URL where server listens
apiURL = 'http://localhost:5000/'

# The ID of the database storing raw WiFi RSSI measurements
db_id = 'test_db_raw'

# The ID of the collection in the database storing raw WiFi RSSI measurements
coll_id = 'test_db_raw'

# The ID of the database storing training fingerprints
db_id_training = 'test_db_training'

# The ID of the collection in the database storing training fingerprints
coll_id_training = 'test_coll_training'

req = urllib2.Request(apiURL + 'etd/v1.0/database/' + db_id  + '/collection/' + coll_id + '/message', headers={"Content-Type": "application/json"})
resp = urllib2.urlopen(req)
messages = json.loads(resp.read())

for mes_key in messages.keys():
	data_id = messages[mes_key]['data_id']
	raw_data_collection = raw_data_pb2.RawRFReadingCollection() 
	req = RequestWithMethod(apiURL + 'etd/v1.0/database/' + db_id  + '/collection/' + coll_id + '/message/' + data_id, 'GET', headers={"Content-Type": "application/json"}, data = 'json')
	response = urllib2.urlopen(req)
	message = json.loads(response.read())

	raw_data_collection = raw_data_pb2.RawRFReadingCollection()
	raw_data_collection.data_id = data_id
    
	# Raw RSSI measurements from each AP are stored in a dictionary structure. Dictionary keys are the AP BSSIDs. 
	meas_aps = {}

	for i in message['raw_measurement']:
		
		try:
			meas_aps[i['sender_bssid']]['rssi'].append(i['rssi'])
		except:
			meas_aps[i['sender_bssid']] = {}
			meas_aps[i['sender_bssid']]['rssi'] = []
			meas_aps[i['sender_bssid']]['rssi'].append(i['rssi'])
			meas_aps[i['sender_bssid']]['channel'] = i['channel']

	### HERE YOU SHOULD MODIFY THE CODE TO BE ABLE TO STORE YOUR TRAINING FINGERPRINTS ###

	## Example 1  - training fingerprint is the average RSSI value for each AP visible at a certain 
	## measurement location.

	# training = {}
	# for key in meas_aps.keys():
	# 	training[key] = np.mean(meas_aps[key]['rssi'])

    ## Example 2  - training fingerprint are the 4 quantile values for each AP visible at a certain 
	## measurement location.

	training = {}
	for key in meas_aps.keys():
	    training[key] = np.array(mquantiles(meas_aps[key]['rssi'], [0, 0.33, 0.67, 1]))

	for key in training.keys():
		for value in range(0,len(training[key])):
			raw_data_reading = raw_data_collection.raw_measurement.add()
			x = datetime.utcnow()
			raw_data_reading.timestamp_utc = int(time.mktime(x.timetuple()))
			raw_data_reading.receiver_location.coordinate_x = i['receiver_location']['coordinate_x']
			raw_data_reading.receiver_location.coordinate_y = i['receiver_location']['coordinate_y']
			raw_data_reading.run_nr = value + 1
			raw_data_reading.sender_bssid = key
			raw_data_reading.rssi = int(training[key][value])
			raw_data_reading.channel = meas_aps[key]['channel']

	raw_data_collection.meas_number = len(training[key])

	json2pb(raw_data_collection, message)
	obj = raw_data_collection.SerializeToString()

	req = urllib2.Request(apiURL + 'etd/v1.0/database/' + db_id_training + '/collection/' + coll_id_training, headers={"Content-Type": "application/x-protobuf"}, data = obj)
	resp = urllib2.urlopen(req)
	print json.loads(resp.read())
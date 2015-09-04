# ETD - Enriched Training Database 

<div class="align-justify">The Enriched Training Database (ETD) a web-based service that enables storage and management of different types of training fingerprints for enabling WiFi RSSI-based indoor fingerprinting, with an additional "enriching" functionality. The user can leverage the enriching functionality to generate virtual training fingerprints based on propagation modeling in virtual training points.</div>

## Table of Contents

- [ETD v1.0](#)
  - [Requirements](#setup)
  - [Installation and Setup](#installation)
  - [Envisioned Usage Concept](#general_idea)
  - [Basic Usage](#basic-usage)
  - [Raw Data Format](#raw_data)
  - [Generating and Storing Training Fingerprints](#fingerprints)
  - [Enriching Functionality](#enriched-usage)
  - [Implementation of New Virtual Points Definition Methods](#virutal_training_points)
  - [Implementation of New Propagation Models](#propagation_model)
  - [Multi-Wall Model in New Environments](#multiwall)

<a name="setup"></a>
## Requirements

* <a href="http://flask.pocoo.org/">Flask</a> - a Python micro-framework for creating RESTful web services.
* <a href="https://www.mongodb.org/">MongoDB</a> - an open-source Not only SQL (NoSQL) database.
* <a href="https://developers.google.com/protocol-buffers/">Google Protocol Buffers</a> - mechanism for encoding and serializing structured data.
* Python libraries: <a href="https://api.mongodb.org/python/current/"scipy>PyMongo</a>, <a href="https://docs.python.org/2/library/functools.html">functools</a>, <a href="https://docs.python.org/2/library/json.html">json</a>, <a href="https://docs.python.org/2/library/urllib2.html">urllib2</a>, <a href="https://docs.python.org/2/library/datetime.html">datetime</a>, <a href="http://www.numpy.org/">NumPy</a>, <a href="http://www.scipy.org/">SciPy</a>. 

<a name="installation"></a>
## Installation and Setup

* Start a MongoDB service on a defined port number (default port number is 27017) and provide the path to a folder where data is to be stored:

 ```vim
 sudo mongod --dbpath <path_to_data> --port <port_num> 
 ```

* Download the ETD service and navigate to the etd_core folder. Set the MongoDB port number and hostname ('localhost' if MongoDB and ETD services are running on the same machine) -  lines 19 and 20 in the _etd_core.py_. Set the ETD service host and port  -  last line in the _etd_core.py_.  Start the ETD service with: 

 ```vim
 python etd_core.py 
 ```

<a name="general_idea"></a>
## Envisioned Usage Concept
![alt tag](https://github.com/flemic/ETD/blob/master/general_idea.png)


<a name="basic-usage"></a>
## Basic Usage

A set of Python scripts that allows basic data management in the ETD service is provided in the folder _examples_. At the moment all necessary parameters have to be defined by editing the scripts.  

* Create new database: _createNewDatabase.py_ 
* Create new collection: _createNewCollection.py_ 
* Collect WiFi RSSI measurements: _rawWiFiRssiScanner.py_
* Get message: _getMessage.py_
* Get a list of messages in a collection: _getMessageList.py_
* Get a list of collections in a database: _getCollections.py_
* Get a list of databases: _getDatabases.py_
* Change message parameters: _changeMessage.py_
* Replace message: _replaceMessage.py_
* Change the name of a collection: _changeCollectionName.py_
* Delete message: _deleteMessage.py_
* Delete collection: _deleteCollection.py_
* Delete database: _deleteDatabase.py_

<a name="raw_data"></a>
## Raw Data Format

The format of the message for storing WiFi RSSI measurements is given below. The message is provided in the folder _message_types_ and it is named _raw_data.proto_.  

```vim
message RawRFReading {
  optional string sender_id = 1;                 // ID of the sender
  required string sender_bssid = 2;              // BSSID of the sender
  required string channel = 3;                   // Channel
  required int32 rssi = 4;                       // RSSI (Received Signal Strength Indicator)
  optional int64 timestamp_utc = 5;              // Milliseconds from 1.1.1970.
  required int32 run_nr = 6;                     // Run number
  required Location receiver_location = 7;       // Location of the receiver
	
  message Location {
    required double coordinate_x = 1;            // x-coordinate
    required double coordinate_y = 2;            // y-coordinate
    optional double coordinate_z = 3;            // z-coordinate
    optional string room_label = 4;              // Room label
  }
} 

message RawRFReadingCollection {
  repeated RawRFReading raw_measurement = 1;     // Collections of raw RSSI data
  required int32 meas_number = 2;                // Number of measurements
  required string data_id = 3;                   // ID of the data
  required bytes _id = 4;                        // Internal ID given by the MongoDB 
  optional int64 timestamp_utc_start = 5;        // Milliseconds from 1.1.1970. start time
  optional int64 timestamp_utc_stop = 6;         // Milliseconds from 1.1.1970. stop time
}
```

<div class="align-justify">This message can be changed according to the specific needs of a particular user. However, the required parameters have to be in included in the message format and values have to be given to them during the training survey measurement campaign. In case the message format is changed, a new translation of a Protocol Buffer structure to Python has to be performed:</div>

```vim
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/raw_data.proto
```
This command will generate (if the new message is properly defined) a _raw_data_pb2.py_ file, and this file has to be used for replacing the obsolete version in directories _examples_, _help_functions_ and _etd_core_.

<a name="fingerprints"></a>
## Generating and Storing Training Fingerprints

<div class="align-justify">After collecting WiFi RSSI measurements at predefined locations and storing them in the ETD service, the user has to modify and then use the script _generateAndStoreFingerprints.py_ in the directory _help_functions_. The modification of the script has to reflect the intended training fingerprints. The script contains two examples: (1) training fingerprint is a set of averaged RSSI values from each visible WiFi AP at a certain measurement location; (2) training fingerprint is the 4 quantile values from each WiFi AP visible at a certain measurement location.</div>   

<a name="enriched-usage"></a>
## Enriching Functionality

Generation of virtual training fingerprints can be performed with the script _virtualizeTrainingFingerprints.py_ in folder _help_functions_. In the script, one has to set the desired parameters: 

* Database/collection that contains original training fingerprints; 
* Enriched database/collection in which original and generated virtual fingerprints are to be stored;
* Virtual training points definition method (at the moment: User or modified Voronoi based);
* Propagation model (at the moment: IDWI and Multi-wall);
* BSSIDs of WiFI APs whose RSSIs are to be modeled in the defined virtual training points;

<a name="virutal_training_points"></a>
## Implementation of New Virtual Points Definition Methods
The design of the ETD allows implementation of new methods for the definition of virtual training points. In order to implement a new method for virtual training points definition, the user firstly has to add this option in the _etd_core.py_ script (line 692). This code segment:

```vim
  if parameters['define_virtual_points'] == 'User':
      points = EF.virtual_point_user()
  elif parameters['define_virtual_points'] == 'Voronoi':
      points = EF.virtual_point_modified_voronoi(coordinates)
  else:
      return json.dumps('Unknown method for the definition of virtual training points')
```  

has to be replaced with the following:

```vim
  if parameters['define_virtual_points'] == 'User':
      points = EF.virtual_point_user()
  elif parameters['define_virtual_points'] == 'Voronoi':
      points = EF.virtual_point_modified_voronoi(coordinates)
  elif parameters['define_virtual_points'] == 'new_method_name':
      points = EF.virtual_point_'new_method'()
  else:
      return json.dumps('Unknown method for the definition of virtual training points')
``` 

For the generation of virtual training points the user may require the locations of original training points. These locations are provided in the variable _coordinates_ in the following format:

```vim
list[tuple_point_0(coordinate_x,coordinate_y),...,tuple_point_N(coordinate_x,coordinate_y)]
```

The user is then able to implement a new function for defining virtual training points. The required output is the same as for the original set of points shown above  - list of tuples.

<a name="propagation_model"></a>
## Implementation of New Propagation Models

<a name="multiwall"></a>
## Multi-Wall model in New Environments
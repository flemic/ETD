# ETD - Enriched Training Database 

The Enriched Training Database (ETD) a web-based service that enables storage and management of different types of training fingerprints for enabling WiFi RSSI-based indoor fingerprinting, with an additional "enriching" functionality. The user can leverage the enriching functionality to generate virtual training fingerprints based on propagation modeling in virtual training points.

## Table of Contents

- [etd v1.0](#)
	- [Requirements](#setup)
	- [Installation and Setup](#installation)
	- [Basic Usage](#basic-usage)
	- [Raw Data Format](#raw_data)
	- [Enriching Functionality](#enriched-usage)

<a name="setup"></a>
## Requirements

* <a href="http://flask.pocoo.org/">Flask</a> - a Python micro-framework for creating RESTful web services.
* <a href="https://www.mongodb.org/">MongoDB</a> - an open-source Not only SQL (NoSQL) database.
* <a href="https://developers.google.com/protocol-buffers/">Google Protocol Buffers</a> - mechanism for encoding and serializing structured data.
* Python libraries: <a href="https://api.mongodb.org/python/current/"">PyMongo</a>, <a href="https://docs.python.org/2/library/functools.html">functools</a>, <a href="https://docs.python.org/2/library/json.html">json</a>, <a href="https://docs.python.org/2/library/urllib2.html">urllib2</a>, <a href="https://docs.python.org/2/library/datetime.html">datetime</a>  

<a name="installation"></a>
## Installation and Setup

* Start a MongoDB service on a defined port number (default port number is 27017) and provide the path to a folder where data is to be stored.

 ```vim
 sudo mongod --dbpath <path_to_data> --port <port_num> 
 ```

* Download the ETD service and navigate to the etd_core folder. Set the MongoDB port number and hostname ('localhost' if MongoDB and ETD services are running on the same machine) -  lines 19 and 20 in the _etd_core.py_. Set the ETD service host and port  -  last line in the _etd_core.py_.  Start the ETD service with: 

 ```vim
 python etd_core.py 
 ```

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
Delete database: _deleteDatabase.py_


<a name="raw_data"></a>
## Raw Data Format

```vim
message RawRFReading {
  optional string sender_id = 1;                 // ID of the sender
  optional string sender_bssid = 2;              // BSSID of the sender
  optional string receiver_id = 3;               // ID of the receiver
  optional string receiver_bssid = 4;            // BSSID of the receiver
  optional string channel = 5;                   // Channel
  optional int32 rssi = 6;                       // RSSI (Received Signal Strength)
  optional int64 timestamp_utc = 7;              // Milliseconds from 1.1.1970. time
  optional int32 run_nr = 8;                     // Run number
  optional Location sender_location = 9;         // Location of the sender
  optional Location receiver_location = 10;      // Location of the receiver
	
  message Location {
    optional double coordinate_x = 1;            // x-coordinate
    optional double coordinate_y = 2;            // y-coordinate
    optional double coordinate_z = 3;            // z-coordinate
    optional string room_label = 4;              // Room label
    optional string node_label = 5;              // Additional label
  }
} 

message RawRFReadingCollection {
  repeated RawRFReading raw_measurement = 1;     // Collections of raw RSSI data
  required int32 meas_number = 2;                // Number of measurments
  required string data_id = 3;                   // ID of the data
  optional bytes _id = 4;                        // Internal ID given by the MongoDB 
  optional int64 timestamp_utc_start = 5;        // Milliseconds from 1.1.1970. start time
  optional int64 timestamp_utc_stop = 6;         // Milliseconds from 1.1.1970. stop time
}
```

<a name="enriched-usage"></a>
## Enriching Functionality

# ETD - Enriched Training Database 

The Enriched Training Database (ETD) a web-based service that enables storage and management of different types of training fingerprints for enabling WiFi RSSI-based indoor fingerprinting, with an additional "enriching" functionality. The user can leverage the enriching functionality to generate virtual training fingerprints based on propagation modeling in virtual training points.

## Table of Contents

- [etd v1.0](#)
	- [Requirements](#setup)
	- [Installation and Setup](#installation)
	- [Basic Usage](#basic-usage)
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

* Download the ETD service and navigate to the etd_core folder. Set the MongoDB port number and hostname ('localhost' if both MondoDB and ETD services are running on the same machine) -  lines 19 and 20 in the _etd_core.py_. Set the ETD service host and port  -  last line in the _etd_core.py_.  Start the ETD service with: 

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


<a name="enriched-usage"></a>
## Enriching Functionality

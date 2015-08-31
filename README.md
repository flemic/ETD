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
* <a href="https://developers.google.com/protocol-buffers/">Google Protocol Buffers</a> - mechanism for encoding and serializing structured data using an efficient and extensible binary format.

<a name="installation"></a>
## Installation and Setup

* Start a MongoDB service on a defined <port_num> (default port number 27017) and provide a path to folder where the data will be stored <path_to_data>.

 ```vim
 sudo mongod --dbpath <path_to_data> --port <port_num> 
 ```

<a name="basic-usage"></a>
## Basic Usage

<a name="enriched-usage"></a>
## Enriching Functionality

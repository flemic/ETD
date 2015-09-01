#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""enriching_functionality.py: Generation of virtual training fingerprints based on propagation modeling."""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2015, Telecommunication Networks Group (TKN), TU Berlin"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"

import sys
import urllib2
import json
import raw_data_pb2
from scipy.spatial import Voronoi
import scipy
import numpy as np


# The URL where server listens
apiURL = 'http://localhost:5000/'

def virtual_point_modified_voronoi(coordinates):
	"""Define locations of virtual training points based on modified Voronoi diagrams"""
	
	vor = Voronoi(coordinates)
	vertices = vor.vertices
	
	dist = knn_avg_dist(coordinates)

	return vertices

def knn_avg_dist(coordinates):
    """Calculates for points in rows of X, the average distance of each, to their k-nearest neighbours"""

    kdt = scipy.spatial.cKDTree(coordinates) 
    k = 4 # number of nearest neighbors 
    dists, neighs = kdt.query(coordinates, k+1)
    avg_dists = np.mean(dists[:, 1:], axis=1)

    return min(avg_dists)

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


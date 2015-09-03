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
from scipy.spatial import Voronoi, voronoi_plot_2d
import scipy
import math
import numpy as np
import matplotlib.pyplot as plt


# The URL where server listens
apiURL = 'http://localhost:5000/'

def virtual_point_user(coordinates):
    pass

def virtual_point_modified_voronoi(coordinates):
    """Define locations of virtual training points based on modified Voronoi diagrams"""

    vor = Voronoi(coordinates)
    vertices = vor.vertices
    vertices = vertices.tolist()

    # Remove vertices that are outside the area where original training points are distributed
    limit = min_max_x_y(coordinates)

    excluded_points_ids = []
    for i in range(0,len(vertices)):
        if vertices[i][0] < limit[0] or vertices[i][0] > limit[1] or vertices[i][1] < limit[2] or vertices[i][1] > limit[3]:
            excluded_points_ids.append(i)

    for offset, index in enumerate(excluded_points_ids):
        index -= offset
        del vertices[index]

    # Merge vertices that are close to one another
    dist = knn_avg_dist(coordinates)

    sum_close_vertices = []
    for i in range(0,len(vertices)):
        close_vertices = []
        close_vertices.append(i)
        for j in range(0,len(vertices)):

            if i != j and math.sqrt(pow(vertices[i][0]-vertices[j][0],2) + pow(vertices[i][1]-vertices[j][1],2)) < dist/2:
                close_vertices.append(j)
        sum_close_vertices.append(close_vertices)

    for i in range(0,len(sum_close_vertices)):
        sum_close_vertices[i].sort()

    cleanlist = []
    [cleanlist.append(x) for x in sum_close_vertices if x not in cleanlist]

    to_delete = []
    to_add = []
    for i in cleanlist:
        if len(i) > 1:
            x = 0.0
            y = 0.0
            num = 0
            for j in i:
                num = num + 1
                x = x + vertices[j][0]
                y = y + vertices[j][1]
                to_delete.append(j)
            to_add.append((x/num,y/num))    

    to_delete_clean = []
    [to_delete_clean.append(x) for x in to_delete if x not in to_delete_clean]

    for offset, index in enumerate(sorted(to_delete_clean)):
        index -= offset
        del vertices[index]

    return vertices + to_add

def knn_avg_dist(coordinates):
    """Calculates for points in rows of X, the average distance of each, to their k-nearest neighbors"""

    kdt = scipy.spatial.cKDTree(coordinates) 
    k = 4 # number of nearest neighbors 
    dists, neighs = kdt.query(coordinates, k+1)
    avg_dists = np.mean(dists[:, 1:], axis=1)
    
    return min(avg_dists)

def min_max_x_y(coordinates):
    """Returns min and max X and Y coordinates of the original set of points"""

    min_x = coordinates[0][0]
    max_x = coordinates[0][0]
    min_y = coordinates[0][1]
    max_y = coordinates[0][1]

    for i in coordinates: 
        if i[0] < min_x:
            min_x = i[0]
        if i[0] > max_x:
            max_x = i[0]
        if i[1] < min_y:
            min_y = i[1]
        if i[1] > max_y:
            max_y = i[1]

    return (min_x,max_x,min_y,max_y)

def generate_virtual_fingerprints_idwi(coordinates,rssis,points,transmitters):
    """Propagation modeling based on Inverse Distance Weighted Interpolation"""

    x = []
    y = []
    xi = []
    yi = []

    for i in coordinates:
        x.append(i[0])
        y.append(i[1])

    for i in points:
        xi.append(i[0])
        yi.append(i[1])

    dist = distance_matrix(x, y, xi, yi)

    # In IDW, weights are 1 / distance
    weights = 1.0 / dist

    # Make weights sum to one
    weights /= weights.sum(axis=0)

    max_elements = 0
    for point in rssis:
        for transmitter in point.keys():
            if len(point[transmitter]) > max_elements:
                max_elements = len(point[transmitter])

    virtual_fingerprints = {}
    # For each BSSID
    for transmitter in transmitters:
        virtual_fingerprints[transmitter] = {}
        # For each meas number 
        for i in range(0,max_elements):
            z = []
            # For each point
            for point in rssis:
                try:
                    z.append(point[transmitter][i])
                except:
                    z.append(-90)
            
            # Multiply the weights for each interpolated point by all observed Z-values
            virtual_fingerprints[transmitter][i] = np.dot(weights.T, z) # Interpolated values for one measurement, one transmitter and all virtual points
            
    return virtual_fingerprints

def distance_matrix(x0, y0, x1, y1):
    """Provides a distance matrix between all locations"""

    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)

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


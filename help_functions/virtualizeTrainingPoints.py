#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""virtualizeTrainingPoints.py: Creates virtual training points and generates virtual training fingerprints in 
those points."""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2015, Telecommunication Networks Group (TKN), TU Berlin"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"

import urllib2
import json
from scipy.spatial import voronoi_plot_2d
import matplotlib.pyplot as plt
from generateURL import RequestWithMethod

# The URL where server listens
apiURL = 'http://localhost:5000/'

# ID of the database where original training fingerprints are stored
db_id_training = 'db_id_training'

# ID of the collection in the database original training fingerprints are stored
coll_id_training = 'coll_id_training'

# ID of the database where original and virtual training fingerprints should be stored
db_id_enriched = 'db_id_enriched'

# The ID of the collection where original and virtual training fingerprints should be stored
coll_id_enriched = 'coll_id_enriched'

parameters= {}
parameters['define_virtual_points'] = 'Voronoi' # User or Voronoi
parameters['propagation_model'] = 'IDWI'        # IDWI or Multiwall
# Define WiFi APs (BSSIDs) that you want to use in the propagation modeling. 
parameters['transmitters'] = ['64:70:02:3e:aa:ef','64:70:02:3e:9f:63','64:70:02:3e:aa:11','64:70:02:3e:aa:d9']

req = RequestWithMethod(apiURL + 'etd/v1.0/' + db_id_training  + '/' + coll_id_training + '/' + db_id_enriched + '/' + coll_id_enriched,'GET', headers={"Content-Type": "application/json"}, data=json.dumps(parameters))
resp = urllib2.urlopen(req)
response = json.loads(resp.read())
print response



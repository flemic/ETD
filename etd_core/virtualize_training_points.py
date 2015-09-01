#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""virtualize_training_points.py: Request for generation of virtual training fingerprints."""

__author__ = "Filip Lemic"
__copyright__ = "Copyright 2015, Telecommunication Networks Group (TKN), TU Berlin"

__version__ = "1.0.0"
__maintainer__ = "Filip Lemic"
__email__ = "lemic@tkn.tu-berlin.de"
__status__ = "Development"

import sys
import urllib2
import json
import time

# Name of the original training database
db_id_original = 'test_db_original'

# Name of the original training collection
coll_id_original = 'test_coll_original'

# Name of the enriched training database
db_id_enriched = 'test_db_enriched'

# Name of the original training collection
coll_id_original = 'test_coll_enriched'

parameters = {}
parameters['define_virtual_points'] = 'Voronoi' # User or Voronoi
parameters['propagation_model'] = 'Multiwall' # IDWI or Multiwall


req = urllib2.Request(apiURL + 'etd/v1.0/database/' + db_id  + '/collection/' + coll_id + '/message', headers={"Content-Type": "application/json"}, data=parameters)
resp = urllib2.urlopen(req)
messages = json.loads(resp.read())
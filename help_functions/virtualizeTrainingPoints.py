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
parameters['generate_virtual_fingerprints'] = 'IDWI' # IDWI or Multi-wall

req = urllib2.Request(apiURL + 'etd/v1.0/' + db_id_training  + '/' + coll_id_training + '/' + db_id_enriched + '/' + coll_id_enriched, headers={"Content-Type": "application/json"})
resp = urllib2.urlopen(req)
print json.loads(resp.read())

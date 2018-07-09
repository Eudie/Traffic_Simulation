#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
This file is just to test intermediate functions

"""

import traffic_from_api

minlon, minlat, maxlon, maxlat = 77.7519486464, 12.9833797192, 77.7528560462, 12.9842016832

minlat=str(minlat) # bottom
minlon=str(minlon) #left
maxlat=str(maxlat) # top
maxlon=str(maxlon) # right

data_fold = '../hoodi_test'

here = traffic_from_api.HereMapInfo(data_fold, minlat, minlon, maxlat,  maxlon)
mapped = here.find_mapping()

print(mapped)



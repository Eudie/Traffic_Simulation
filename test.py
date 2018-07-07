#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
This file is just to test intermediate functions

"""

import traffic_from_api

minlat = "12.9380131671"
minlon = "77.6319900345"
maxlat = "12.939314082"
maxlon = "77.6337735827"

data_fold = '/home/eudie/Study/Quantela/hoodi_test'

here = traffic_from_api.HereMapInfo(data_fold, minlat, minlon, maxlat,  maxlon)
mapped = here.find_mapping()

print(mapped)



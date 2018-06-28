#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
In file is just to make file paths
"""
import os


class FileName:
    """
    This class is just to make names of the file, which we are gonna use across sub-models
    """
    def __init__(self, data_folder):
        self.data_folder = data_folder

        self.osm_map = os.path.join(self.data_folder, 'map.osm')
        self.original_sumo_map = os.path.join(self.data_folder, 'original_sumo.net.xml')
        self.original_sumo_poly = os.path.join(self.data_folder, 'original_sumo.poly.xml')
        self.typemap = os.path.join(self.data_folder, 'typemap.xml')
        self.joining_nodes = os.path.join(self.data_folder, 'joining_nodes.xml')
        self.routes = os.path.join(self.data_folder, 'route.rou.xml')
        self.traffic_flow_file = os.path.join(self.data_folder, 'traffic_flow.json')
        self.vehicle_properties = os.path.join(data_folder, 'vehicle_properties.xml')
        self.sumo_tripinfo_file = os.path.join(self.data_folder, 'tripinfo.xml')
        self.sumo_cfg_file = os.path.join(self.data_folder, 'configuration.sumo.cfg')

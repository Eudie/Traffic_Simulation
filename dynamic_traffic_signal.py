#!/home/eudie/miniconda3/envs/Traffic_Simulation/bin/python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
In this class I am trying in structure dynamic traffic signal module. Which will be used in product.
We are trying to optimize the signal using simulation. We are using OpenStreetMap to get map and SUMO for optimization.

"""


from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
import numpy as np
import pandas as pd
import shutil
import requests
import overpass
import sumo_information
import sumo_simulation


class DynamicTrafficSignal:
    """
    Here we will structure all submodules of the project.
    """

    def __init__(self, name, data_dir='..'):
        self.name = name
        self.data_folder = os.path.join(data_dir, name)
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        shutil.copy2('configuration.sumo.cfg', self.data_folder)
        shutil.copy2('typemap.xml', self.data_folder)

    def get_map(self, left, bottom, right, top):
        """
        By this function user can get the map from openstreetmap and convert to sumo map.
        """

        # TODO: get data with bounding box http://api.openstreetmap.org/api/0.6/map?bbox=11,50,11.1,50.1, save in folder
        link = 'https://api.openstreetmap.org/api/0.6/map?bbox='+",".join([str(left), str(bottom), str(right), str(top)])
        data = requests.get(link)

        api = overpass.API()
        MapQuery = overpass.MapQuery(left, bottom, right, top)
        response = api.get(MapQuery)
        # TODO: find nodes to be merged and save in nodes.xml
        # TODO: using sumpopy netconvert with lefthand and merge nodes
        # TODO: change node id with human read name in sumo map

        self.osm_map = 'name_location_of_osm_map'
        self.original_sumo_map = 'name_location_of_converted_map'

        return data, response

    def edit_map(self, source='original'):
        """
        This function will open UI window or help to open UI window by sending information.
        It will capture all changes in name of sumo map elements and save new graph.
        :param source: which map file to edit, 'original' or 'pre-edited'
        :return: success or failure
        """

        # TODO: With the help of UI allow to make changes in the original_sumo_map and save to edited_sumo_map.

        self.edited_sumo_map = 'name_location_of_edited_sumo_map'

        return 0

    def build_traffic(self, how='manual'):
        """
        This function will open UI window or help to open UI window by sending information.
        It will capture all traffic info of each pair of roads.
        :param how: method by which user want to input values
        :return: success or failure
        """

        # TODO: Capture all values, generate sumo trips xml and save name of location_name
        # TODO: find all the links passing through traffic signal
        # TODO: take inputs for all combination or roads
        # TODO: generate routefile

        self.trip_info = 'name_location_of_trip_info'

        return 0

    def optimize_traffic_lights(self, timing_range, gui=False):
        """
        Here we do all the magic. We simulate traffic in the area multiple time and optimize all signals for best perf.
        :return: json file of optimized signal properties containing all signals in the map.
        """

        # TODO: simulate and optimize

        sim = sumo_simulation.Simulation(self.data_folder)
        sim.optimize(timing_range=timing_range)
        self.optimized_result = sim.final_rule

        if gui:
            sim.run(rule=self.optimized_result, gui=True)
        return self.optimized_result

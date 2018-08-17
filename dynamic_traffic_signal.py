#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
In this class I am trying in structure dynamic traffic signal module. Which will be used in product.
We are trying to optimize the signal using simulation. We are using OpenStreetMap to get map and SUMO for optimization.

"""


from __future__ import absolute_import
from __future__ import print_function

import os
import shutil
import requests
import sumo_information
import sumo_simulation
import traffic_from_api
import operator
from make_file_names import FileName


class DynamicTrafficSignal:
    """
    Here we will structure all submodules of the project.
    """

    def __init__(self, name, data_dir='..'):
        self.name = name
        self.data_folder = os.path.join(os.path.realpath(data_dir), name)
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        shutil.copy2('configuration.sumo.cfg', self.data_folder)
        shutil.copy2('typemap.xml', self.data_folder)
        shutil.copy2('vehicle_properties.xml', self.data_folder)

        self.filename = FileName(self.data_folder)

        self.left = None
        self.bottom = None
        self.right = None
        self.top = None

        self.junction_info = None
        self.nodes_to_join = None
        self.optimized_result = None
        self.biggest_junction = None

    def get_map(self, left, bottom, right, top):
        """
        By this function user can get the map from openstreetmap and convert to sumo map.
        """

        self.left = str(left)
        self.bottom = str(bottom)
        self.right = str(right)
        self.top = str(top)
        link = 'https://api.openstreetmap.org/api/0.6/map?bbox='+",".join([self.left, self.bottom, self.right, self.top])
        data = requests.get(link)

        with open(self.filename.osm_map, 'w') as f:
            f.write(data.text)

        # Finding nodes to merge and saving in xml
        osm_data = sumo_information.OsmNetworkInfo(self.filename.osm_map)
        self.nodes_to_join = osm_data.get_nodes_to_merge()

        if not os.path.isfile(self.filename.joining_nodes):
            with open(self.filename.joining_nodes, "w") as routes:
                print("<nodes>", file=routes)
                for i in range(len(self.nodes_to_join)):
                    print('   <join nodes="{}"/>'.format(" ".join(self.nodes_to_join[i]['nodes'])), file=routes)

                print("</nodes>", file=routes)

        # converting osm to sumo net and using poligon to building
        netconvert_cmd = ' '.join(['netconvert', '--osm-files', self.filename.osm_map,
                                   '--lefthand', '-n', self.filename.joining_nodes,
                                   '--tls.yellow.time', '0',
                                   '--tls.left-green.time', '0',
                                   '-o', self.filename.original_sumo_map])
        os.system(netconvert_cmd)

        polyconvert_cmd = ' '.join(['polyconvert', '--net-file', self.filename.original_sumo_map,
                                    '--osm-files', self.filename.osm_map,
                                    '--type-file', self.filename.typemap, '-o', self.filename.original_sumo_poly])
        os.system(polyconvert_cmd)

    def edit_map(self, source='original'):
        """
        This function will open UI window or help to open UI window by sending information.
        It will capture all changes in name of sumo map elements and save new graph.
        :param source: which map file to edit, 'original' or 'pre-edited'
        :return: success or failure
        """

        # TODO: With the help of UI allow to make changes in the original_sumo_map and save to edited_sumo_map.

        self.filename.edited_sumo_map = 'name_location_of_edited_sumo_map'

        return 0

    def build_traffic(self, how='manual', road_mapping='automatic'):
        """
        This function will open UI window or help to open UI window by sending information.
        It will capture all traffic info of each pair of roads.
        :param how: method by which user want to input values ['manual', 'heremap']
        :param road_mapping: road mapping sometime require manual intervention ['manual', 'automatic']
        :return: success or failure
        """

        traffic = sumo_simulation.Traffic(self.data_folder)

        if not os.path.isfile(self.filename.traffic_flow_file):
            traffic.build_traffic_flow()

        if how == 'heremap':
            here = traffic_from_api.HereMapInfo(self.data_folder, self.bottom, self.left, self.top, self.right, mapping=road_mapping)
            here.update_traffic_flow()

        traffic.generate()

    def optimize_traffic_lights(self, timing_range, signal_pattern='one_road_open', gui=False):
        """
        Here we do all the magic. We simulate traffic in the area multiple time and optimize all signals for best perf.
        :return: json file of optimized signal properties containing all signals in the map.
        """
        net_info = sumo_information.SumoNetworkInfo(self.filename.original_sumo_map)
        self.junction_info = net_info.get_junction_routes()
        self.biggest_junction = max({key: len(value['routes']) for key, value in self.junction_info.items()}.items(),
                                    key=operator.itemgetter(1))[0]

        big_junction_phases = {self.biggest_junction: self.junction_info[self.biggest_junction]['phases']}
        sim = sumo_simulation.Simulation(self.data_folder, signal_pattern=signal_pattern, phases=big_junction_phases)
        sim.optimize(timing_range=timing_range)
        self.optimized_result = sim.final_rule

        if gui:
            sim.run(rule=self.optimized_result, gui=True)
        return self.optimized_result

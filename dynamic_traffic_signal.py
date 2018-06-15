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
import shutil
import requests
import sumo_information
import sumo_simulation
import operator


class DynamicTrafficSignal:
    """
    Here we will structure all submodules of the project.
    """

    def __init__(self, name, data_dir='..'):
        self.__name = name
        self.data_folder = os.path.join(os.path.realpath(data_dir), name)
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        shutil.copy2('configuration.sumo.cfg', self.data_folder)
        shutil.copy2('typemap.xml', self.data_folder)

        self.osm_map = os.path.join(self.data_folder, 'map.osm')
        self.original_sumo_map = os.path.join(self.data_folder, 'original_sumo.net.xml')
        self.original_sumo_poly = os.path.join(self.data_folder, 'original_sumo.poly.xml')
        self.typemap = os.path.join(self.data_folder, 'typemap.xml')
        self.joining_nodes = os.path.join(self.data_folder, 'joining_nodes.xml')
        self.routes = os.path.join(self.data_folder, 'route.rou.xml')

        self.junction_info = None
        self.nodes_to_join = None
        self.optimized_result = None
        self.biggest_junction = None

    def get_map(self, left, bottom, right, top):
        """
        By this function user can get the map from openstreetmap and convert to sumo map.
        """

        link = 'https://api.openstreetmap.org/api/0.6/map?bbox='+",".join([str(left), str(bottom), str(right), str(top)])
        data = requests.get(link)

        with open(self.osm_map, 'w') as f:
            f.write(data.text)

        # Finding nodes to merge and saving in xml
        osm_data = sumo_information.OsmNetworkInfo(self.osm_map)
        self.nodes_to_join = osm_data.get_nodes_to_merge()

        with open(self.joining_nodes, "w") as routes:
            print("<nodes>", file=routes)
            for i in range(len(self.nodes_to_join)):
                print('   <join nodes="{}"/>'.format(" ".join(self.nodes_to_join[i]['nodes'])), file=routes)

            print("</nodes>", file=routes)

        # converting osm to sumo net and using poligon to building
        netconvert_cmd = ' '.join(['netconvert', '--osm-files', self.osm_map,
                                   '--lefthand', '-n', self.joining_nodes,
                                   '--tls.yellow.time', '0',
                                   '--tls.left-green.time', '0'
                                   '-o', self.original_sumo_map])
        os.system(netconvert_cmd)

        polyconvert_cmd = ' '.join(['polyconvert', '--net-file', self.original_sumo_map,
                                    '--osm-files', self.osm_map,
                                    '--type-file', self.typemap, '-o', self.original_sumo_poly])
        os.system(polyconvert_cmd)

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

        net_info = sumo_information.SumoNetworkInfo(self.original_sumo_map)
        self.junction_info = net_info.get_junction_routes()
        self.biggest_junction = max({key: len(value['routes']) for key, value in self.junction_info.items()}.items(),
                               key=operator.itemgetter(1))[0]

        junction_name_for_muggles = self.biggest_junction

        # To get suggested name: not working as of now
        # if self.biggest_junction[:7] is "cluster":
        #     for k, i in self.nodes_to_join.items():
        #         print("cluster_"+ "_".join(i['nodes'].sort()))
        #         if "cluster_"+ "_".join(i['nodes'].sort()) == self.biggest_junction and i['suggested_name'] is not None:
        #             junction_name_for_muggles = i['suggested_name']

        print("Input traffic value for each road passing the junction: {}".format(junction_name_for_muggles))

        for i in range(len(self.junction_info[self.biggest_junction]['routes'])):
            route = self.junction_info[self.biggest_junction]['routes'][i]
            self.junction_info[self.biggest_junction]['routes'][i]['traffic_value'] = input('from: {} to: {} via: {} s'.format(route['from'], route['to'], route['via']))

        traffic = sumo_simulation.Traffic(self.routes)
        traffic.generate(self.junction_info[self.biggest_junction])

    def optimize_traffic_lights(self, timing_range, signal_pattern='one_road_open', gui=False):
        """
        Here we do all the magic. We simulate traffic in the area multiple time and optimize all signals for best perf.
        :return: json file of optimized signal properties containing all signals in the map.
        """

        big_junction_phases = {self.biggest_junction: self.junction_info[self.biggest_junction]['phases']}
        sim = sumo_simulation.Simulation(self.data_folder, signal_pattern=signal_pattern, phases=big_junction_phases)
        sim.optimize(timing_range=timing_range)
        self.optimized_result = sim.final_rule

        if gui:
            sim.run(rule=self.optimized_result, gui=True)
        return self.optimized_result

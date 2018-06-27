#!/home/eudie/miniconda3/envs/Traffic_Simulation/bin/python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
Here we are trying to do all coding related to sumo traci simulations
"""

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import random
import numpy as np
import sumo_information
import operator
import json
import xml.etree.ElementTree as Xml
from scipy.optimize import brute

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci


class Simulation:
    """
    Here we are doing everything related to traci
    """

    def __init__(self, area_name, signal_pattern, phases):
        self.area_name = area_name
        self.signal_pattern = signal_pattern
        self.phases = phases
        self.sumo_cfg_file = os.path.join(self.area_name, 'configuration.sumo.cfg')
        self.sumo_tripinfo_file = os.path.join(self.area_name, 'tripinfo.xml')
        self.final_rule = {'junction': '_',
                           'phases': [],
                           'time': []}

    def get_signal_schema(self, signal_pattern):
        """
        here we will get different schema for signal
        :param signal_pattern:
        :return: signal_schema
        """
        schema = None
        if signal_pattern == "one_road_open":
            first_phase = list(self.phases.values())[0][0]['state'].lower()

            sig_len = []
            phases = []
            starting_index = 0
            for i in range(1, len(first_phase)):
                if first_phase[i - 1] != first_phase[i]:
                    sig_len.append(i - starting_index)
                    string = 'r' * len(first_phase[:starting_index]) + 'G' * len(
                        first_phase[starting_index:i]) + 'r' * len(first_phase[i:])
                    phases.append(string)
                    starting_index = i

            last_string = 'r' * len(first_phase[:starting_index]) + 'G' * len(first_phase[starting_index:])
            phases.append(last_string)
            time = [0]*len(phases)

            schema = {'junction': list(self.phases.keys())[0], 'phases': phases, 'time': time}

        return schema

    def run(self, rule, gui=False):
        """execute the TraCI control loop"""
        if gui:
            sumo_binary = checkBinary('sumo-gui')
        else:
            sumo_binary = checkBinary('sumo')

        traci.start([sumo_binary, "-c", self.sumo_cfg_file, "--tripinfo-output", self.sumo_tripinfo_file])

        step = 0

        total_cycle = rule['time'][-1]
        cycle_step = 0
        traci.trafficlights.setRedYellowGreenState(rule['junction'], rule['phases'][0])
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

            if cycle_step == total_cycle:
                # there is a vehicle from the north, switch
                cycle_step = 0
                traci.trafficlights.setRedYellowGreenState(rule['junction'], rule['phases'][0])
            elif cycle_step in rule['time']:
                # otherwise try to keep green for EW
                index = rule['time'].index(cycle_step)
                traci.trafficlights.setRedYellowGreenState(rule['junction'], rule['phases'][index+1])
            step += 1
            cycle_step += 1

        traci.close()
        sys.stdout.flush()

    def __objective(self, array):
        """
        Internal objective function to optimize
        :param array: signal timings
        :return: total mean duration in the simulation
        """
        rule = self.get_signal_schema(self.signal_pattern)
        rule['time'] = np.cumsum(array).tolist()

        self.run(rule)
        info = sumo_information.SumoTripInfo(self.sumo_tripinfo_file)
        df = info.get_df()
        return np.mean(df['duration'])

    def optimize(self, timing_range):
        """
        Here we run simulation multiple times and find the most optimized value
        :param timing_range: tuple of max and min time for lane opening
        :return: set optimized result
        """

        if self.signal_pattern is not None:
            rule = self.get_signal_schema(self.signal_pattern)

        no_of_signals = len(rule['time'])

        bounds = (slice(timing_range['min'], timing_range['max'], 1),)*no_of_signals

        x, f_val, grid, j_out = brute(self.__objective, ranges=bounds, full_output=True, finish=None)
        self.final_rule = rule
        self.final_rule['time'] = np.cumsum(x).tolist()


class Traffic:
    """
    In this class we handel all traffic and route related information
    """

    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.route_file = os.path.join(data_folder, 'route.rou.xml')
        self.traffic_flow = os.path.join(data_folder, 'traffic_flow.json')
        self.original_sumo_map = os.path.join(data_folder, 'original_sumo.net.xml')
        self.vehicle_properties = os.path.join(data_folder, 'vehicle_properties.xml')
        self.junction_info = None
        self.biggest_junction = None

    def build_traffic_flow(self):
        """
        Here we will generate json with default values, that we can edit manually or with api
        """

        net_info = sumo_information.SumoNetworkInfo(self.original_sumo_map)
        self.junction_info = net_info.get_junction_routes()
        self.biggest_junction = max({key: len(value['routes']) for key, value in self.junction_info.items()}.items(),
                                    key=operator.itemgetter(1))[0]
        biggest_juction_info = {self.biggest_junction: self.junction_info[self.biggest_junction]}

        output = {}
        for key, value in biggest_juction_info.items():
            temp_route = []
            for key1, value1 in value.items():
                if key1 == 'routes':
                    for route in value1:
                        temp_route.append((route['from'], route['to']))

            temp_route = list(set(temp_route))
            temp_dict = []
            for i in temp_route:
                temp_dict.append(
                    {'from': i[0], 'to': i[1], 'vehicle_flow': 0.1, 'vehicle_ratio': {'car': 1, 'bike': 1, 'bus': 1}})
            output[key] = temp_dict

        with open(self.traffic_flow, 'w') as outfile:
            json.dump(output, outfile, indent=4)

    def generate(self):
        """
        Here we are going to generate traffic based on input values from user
        :param route_info:
        :return: save route file with generated traffic
        """
        #random.seed(42)  # make tests reproducible
        N = 90  # number of time steps

        with open(self.traffic_flow, 'r') as outfile:
            traffic_flow = json.load(outfile)

        with open(self.route_file, "w") as route_file:
            print("<routes>", file=route_file)

            e = Xml.parse(self.vehicle_properties).getroot()
            for i in e:
                print((Xml.tostring(i, 'unicode')), end='', file=route_file)

            for junction, routes in traffic_flow.items():
                for i, connection in enumerate(routes):
                    print('<route id="r_{}" edges="{} {}"/>'.format(i, connection['from'], connection['to']),
                          file=route_file)

            for j in range(N):
                for junction, routes in traffic_flow.items():
                    for i, connection in enumerate(routes):
                        ratio_total = sum(connection['vehicle_ratio'].values())
                        for v_type, v_ratio in connection['vehicle_ratio'].items():
                            v_ratio = float((v_ratio/ratio_total) * connection['vehicle_flow'])

                            if random.uniform(0, 1) < v_ratio:
                                print('    <vehicle id="{}_{}_{}" type="{}" route="r_{}" depart="{}"/>'.
                                      format(v_type, i, j, v_type, i, j), file=route_file)

            print("</routes>", file=route_file)

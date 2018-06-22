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
from scipy.optimize import minimize
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

    def __init__(self, xml_name_location):
        self.xml_name_location = xml_name_location

    def generate(self, route_info):
        """
        Here we are going to generate traffic based on input values from user
        :param route_info:
        :return: save route file with generated traffic
        """

        random.seed(42)  # make tests reproducible
        N = 180  # number of time steps
        vehNr = 0
        with open(self.xml_name_location, "w") as routes:
            print("""<routes>
        <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
        <vType id="bike" length="1.8" width="0.8" maxSpeed="20" accel="0.8" decel="1.5" sigma="0.5" speedDev="0.5" vClass="bicycle"/>
        <vType id="bus" accel="0.5" decel="4.5" sigma="0.5" length="7" minGap="5" maxSpeed="10" guiShape="bus"/>""",
                  file=routes)

            for i, connection in enumerate(route_info['routes']):

                print('<route id="r_{}" edges="{} {}"/>'.format(i, connection['from'], connection['to']), file=routes)

            for j in range(N):
                for i, connection in enumerate(route_info['routes']):
                    if random.uniform(0, 1) < float(connection['traffic_value']):
                        print('    <vehicle id="car_{}_{}" type="car" route="r_{}" depart="{}"/>'.format(i, j, i, j),
                              file=routes)
                        print('    <vehicle id="bike_{}_{}" type="bike" route="r_{}" depart="{}" color="0,1,0"/>'.format(i, j, i, j),
                              file=routes)
                        print('    <vehicle id="bus_{}_{}" type="bus" route="r_{}" depart="{}" color="1,0,0"/>'.format(i, j, i, j),
                              file=routes)

            print("</routes>", file=routes)

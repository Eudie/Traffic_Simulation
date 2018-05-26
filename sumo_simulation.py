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
import optparse
import subprocess
import random
import numpy as np
import pandas as pd
import sumo_information

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

    def __init__(self, area_name):
        self.area_name = area_name
        self.sumo_cfg_file = os.path.join(self.area_name, 'configuration.sumo.cfg')
        self.sumo_tripinfo_file = os.path.join(self.area_name, 'tripinfo.xml')

    def run(self, rule, gui=False):
        """execute the TraCI control loop"""
        if gui:
            sumo_binary = checkBinary('sumo-gui')
        else:
            sumo_binary = checkBinary('sumo')

        traci.start([sumo_binary, "-c", self.sumo_cfg_file, "--tripinfo-output", self.sumo_tripinfo_file])

        step = 0

        total_cycle = sum(rule.values())
        cycle_step = 0
        traci.trafficlights.setRedYellowGreenState("0", "GGGgrrrGGGgrrr")
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

            if cycle_step == total_cycle:
                # there is a vehicle from the north, switch
                cycle_step = 0
                traci.trafficlights.setRedYellowGreenState("0", "GGGgrrrGGGgrrr")
            elif cycle_step == rule['one']:
                # otherwise try to keep green for EW
                traci.trafficlights.setRedYellowGreenState("0", "rrrrGGgrrrrGGg")
            step += 1
            cycle_step += 1
        traci.close()
        sys.stdout.flush()

    def optimize(self, timing_range):
        """
        Here we run simulation multiple times and find the most optimized value
        :param timing_range: tuple of max and min time for lane opening
        :return: set optimized result
        """

        last_duration = 10000000000
        self.final_rule = {'one': 0, 'two': 0}
        for one in range(timing_range['min'], timing_range['max']):
            for two in range(timing_range['min'], timing_range['max']):
                print(one, two)

                rule = {'one': one, 'two': two}
                self.run(rule)
                info = sumo_information.SumoTripInfo(self.sumo_tripinfo_file)
                df = info.get_df()
                avg_duration = np.mean(df['duration'])
                if avg_duration < last_duration:
                    self.final_rule = rule
                    last_duration = avg_duration
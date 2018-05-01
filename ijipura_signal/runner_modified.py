#!/usr/bin/env python
"""
@file    runner.py
@author  Lena Kalleske
@author  Daniel Krajzewicz
@author  Michael Behrisch
@author  Jakob Erdmann
@date    2009-03-26
@version $Id: runner.py 22608 2017-01-17 06:28:54Z behrisch $

Tutorial for traffic light control via the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2017 DLR/TS, Germany

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random

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


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 10
    pEW = 1. / 11
    pNS = 1. / 20
    pSN = 1. / 20
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
        <vType id="bike" length="1.8" width="0.8" maxSpeed="20" accel="0.8" decel="1.5" sigma="0.5" speedDev="0.5" vClass="bicycle"/>
        <vType id="bus" accel="0.5" decel="4.5" sigma="0.5" length="7" minGap="5" maxSpeed="10" guiShape="bus"/>

        <route id="right" edges="1o 2i" />
        <route id="left" edges="2o 1i" />
        <route id="down" edges="54o 4i 3o 53i" />
        <route id="up" edges="53o 3i 4o 54i" />""", file=routes)
        lastVeh = 0
        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                print('    <vehicle id="car_right_%i" type="car" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bike_right_%i" type="bike" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bus_right_%i" type="bus" route="right" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="car_left_%i" type="car" route="left" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bike_left_%i" type="bike" route="left" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bus_left_%i" type="bus" route="left" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pNS:
                print('    <vehicle id="car_down_%i" type="car" route="down" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bike_down_%i" type="bike" route="down" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bus_down_%i" type="bus" route="down" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i

            if random.uniform(0, 1) < pSN:
                print('    <vehicle id="car_up_%i" type="car" route="up" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bike_up_%i" type="bike" route="up" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                print('    <vehicle id="bus_up_%i" type="bus" route="up" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>





def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    #
    # phases = []
    #
    # phases.append(traci.trafficlights.Phase(30, 0, 0, "GGGgrrrGGGgrrr"))
    # phases.append(traci.trafficlights.Phase(10, 0, 0, "rrrGrrrrrrGrrr"))
    # phases.append(traci.trafficlights.Phase(40, 0, 0, "rrrrGGgrrrrGGg"))
    # phases.append(traci.trafficlights.Phase(20, 0, 0, "rrrrrrGrrrrrrG"))
    #
    # logic = traci.trafficlights.Logic("new-program", 0, 0, 0, phases)
    #
    # traci.trafficlights.setCompleteRedYellowGreenDefinition("0", logic)


    rule = {'one' : 120, 'two': 90}
    total_cycle = sum(rule.values())
    cycle_step = 0
    traci.trafficlights.setRedYellowGreenState("0", "GGGgrrrGGGgrrr")
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print(traci.trafficlights.getPhase("0"))
        # print(traci.trafficlights.getRedYellowGreenState("0"))
        # print(traci.trafficlights.getCompleteRedYellowGreenDefinition("0"))
        # print('one done \n')

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


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()

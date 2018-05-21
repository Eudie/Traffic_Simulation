#!/home/eudie/miniconda3/envs/Traffic_Simulation/bin/python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
Here we are trying to organize the code for extracting information from SUMO xml files
"""

import pandas as pd
import numpy as np
import os


class SumoNetworkInfo:
    """
    In this class we will get all information about sumo network graph
    """

    def __init__(self, xml_name_location):
        self.xml_name_location = xml_name_location

    # TODO: add method to extract information from xml. If these method have to used in loop, we have to get all at once


class SumoTripInfo:
    """
    In this class we will get all information about sumo trips happened after simulation
    """

    def __init__(self, xml_name_location):
        self.xml_name_location = xml_name_location

    # TODO: add method to extract information from xml. If these method have to used in loop, we have to get all at once

#!/home/eudie/miniconda3/envs/Traffic_Simulation/bin/python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
Here we are trying to organize the code for extracting information from SUMO xml files
"""

import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET


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

    def get_df(self):
        """
        This function read the read the information from trips xml file in pandas dataframe
        :return: pandas dataframe
        """

        parsed_xml = ET.parse(self.xml_name_location)
        tripinfo_list = []
        for full_doc in parsed_xml.iter('tripinfos'):
            for trip in full_doc.iter('tripinfo'):
                tripinfo_list.append(trip.attrib)

        trips_df = pd.DataFrame(tripinfo_list)
        to_float_col = ['arrivalSpeed', 'depart', 'departDelay', 'departSpeed', 'duration', 'speedFactor', 'timeLoss']
        trips_df[to_float_col] = trips_df[to_float_col].astype(np.float)
        return trips_df

    # TODO: add method to extract information from xml. If these method have to used in loop, we have to get all at once

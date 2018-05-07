#!/usr/bin/env python
"""
@file trip_info.py


This to read tripinfo.xml and find the features of simulation
"""

import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET


def read_as_df(filename='tripinfo.xml'):
    """
    This function read the read the information from trips xml file in pandas datafrome
    :param filename: name of trips xml file
    :return: pandas dataframe
    """

    parsed_xml = ET.parse(filename)
    tripinfo_list = []
    for full_doc in parsed_xml.iter('tripinfos'):
        for trip in full_doc.iter('tripinfo'):
            tripinfo_list.append(trip.attrib)

    trips_df = pd.DataFrame(tripinfo_list)
    to_float_col = ['arrivalSpeed', 'depart', 'departDelay', 'departSpeed', 'duration', 'speedFactor', 'timeLoss']
    trips_df[to_float_col] = trips_df[to_float_col].astype(np.float)
    return trips_df


if __name__ == "__main__":
    data_frame = read_as_df("tripinfo.xml")
    print(data_frame)




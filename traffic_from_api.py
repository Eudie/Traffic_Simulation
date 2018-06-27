#!/home/eudie/miniconda3/envs/Traffic_Simulation/bin/python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
In this class I am trying to get vehicle flow from some api

"""
import operator
import requests
import json
import os
import pandas as pd
import datetime
import xml.etree.ElementTree as Xml
import sumo_information


class HereMapInfo:
    """
    Here we get the data from heremap, which we will use to build traffic flow for sumo
    """
    def __init__(self, data_folder, bottom, left, top, right):
        self.data_folder = data_folder
        self.left = str(left)
        self.bottom = str(bottom)
        self.right = str(right)
        self.top = str(top)

        self.osm_map = os.path.join(self.data_folder, 'map.osm')
        self.original_sumo_map = os.path.join(self.data_folder, 'original_sumo.net.xml')
        self.original_sumo_poly = os.path.join(self.data_folder, 'original_sumo.poly.xml')
        self.typemap = os.path.join(self.data_folder, 'typemap.xml')
        self.joining_nodes = os.path.join(self.data_folder, 'joining_nodes.xml')
        self.routes = os.path.join(self.data_folder, 'route.rou.xml')
        self.traffic_flow_file = os.path.join(self.data_folder, 'traffic_flow.json')
        self.vehicle_properties = os.path.join(data_folder, 'vehicle_properties.xml')

        with open('heremap_credentials.json') as f:
            api_keys = json.load(f)

        url = 'https://traffic.cit.api.here.com/traffic/6.1/flow.json?bbox=' + \
              self.bottom + '%2C' + self.left + '%3B' + self.top + '%2C' + self.right +\
              '&responseattributes=sh,fc&app_code='+api_keys['app_code']+'&app_id='+api_keys['app_id']

        data = requests.get(url)
        self.data_json = data.json()

        # with open('data_comparision/heremap.json') as f:
        #     self.data_json = json.load(f)

        e = Xml.parse(self.vehicle_properties).getroot()
        self.vehicle_length = {}
        for i in e:
            self.vehicle_length[i.attrib['id']] = float(i.attrib['length'])

        with open(self.traffic_flow_file) as f:
            self.traffic_flow = json.load(f)

    def heremap_data_as_df(self):
        """
        For simplicity here we convert nested json data from heremap to dataframe
        :param heremap_json:
        :return:
        """
        RWS = self.data_json['RWS']
        l = []
        for rw in RWS:
            EBU_COUNTRY_CODE = rw['EBU_COUNTRY_CODE']
            EXTENDED_COUNTRY_CODE = rw['EXTENDED_COUNTRY_CODE']
            UNITS = rw['UNITS']
            for elem in rw['RW']:
                DE = elem['DE']
                LI = elem['LI']
                PBT = elem['PBT']
                mid = elem['mid']
                FIS = elem['FIS']
                for FI in FIS:
                    elem_1 = FI['FI']
                    for elem_2 in elem_1:
                        LE = elem_2['TMC']['LE']
                        PC = elem_2['TMC']['PC']
                        QD = elem_2['TMC']['QD']
                        SHP = elem_2['SHP']
                        CF = elem_2['CF']
                        for elem_3 in CF:
                            FF = elem_3['FF']
                            CN = elem_3['CN']
                            JF = elem_3['JF']
                            SP = elem_3['SP']
                            TY = elem_3['TY']
                            l.append(
                                [EBU_COUNTRY_CODE, EXTENDED_COUNTRY_CODE, UNITS, DE, LI, PBT, mid, LE, PC, QD, SHP, FF,
                                 CN, JF, SP, TY])
        column_names = ['EBU_COUNTRY_CODE', 'EXTENDED_COUNTRY_CODE', 'UNITS', 'DE', 'LI', 'PBT', 'mid', 'LE', 'PC', 'QD', 'SHP',
                'FF', 'CN', 'JF', 'SP', 'TY']
        df = pd.DataFrame(l, columns=column_names)
        df['PBT'] = datetime.datetime.now()

        df['SHP'] = df['SHP'].astype(str)
        df['PATCH'] = df['PC'].map(str) + df['QD']
        return df

    def find_mapping(self):
        """
        Here we will find the which road from here map is linked to that of sumo or osm
        :return: dictionary for
        """

        sumo_road = ['122516806', '143215059', '580921886#0', '28043853']
        here_map_road = ['2572+', '1835+', '2572-', '1836-']

        mapping = pd.DataFrame({'sumo_road': sumo_road, 'here_map_road': here_map_road})

        return mapping

    def average_vehicle_length(self, road):
        """
        Mathematically calculate flow from jamfactor and other lane information
        :param road: all information of lane from here map
        :param vehicle_ratio: distribution of type of vehicles
        :return: average_length of vehicle
        """

        total_vehicle_ratio = dict.fromkeys(self.vehicle_length, 0)

        for junction, roads in self.traffic_flow.items():
            for i in roads:
                if i['from'] == road:
                    for vehicle_type in total_vehicle_ratio.keys():
                        total_vehicle_ratio[vehicle_type] += i['vehicle_ratio'][vehicle_type]

        average_length = 0.0
        all_vehicle_count = sum(total_vehicle_ratio.values())

        for vehicle_type in total_vehicle_ratio.keys():
            average_length += self.vehicle_length[vehicle_type] * total_vehicle_ratio[vehicle_type] / all_vehicle_count

        return average_length

    def update_traffic_flow(self):
        """
        Here we will match heremap congestion data to sumo traffic flow
        :return:
        """

        sumo_info = sumo_information.SumoNetworkInfo(self.original_sumo_map)

        mapping = self.find_mapping()
        mapping['average_vehicle_length'] = mapping['sumo_road'].apply(self.average_vehicle_length)
        mapping['total_lanes'] = mapping['sumo_road'].apply(sumo_info.get_total_lanes)

        heremap_df = self.heremap_data_as_df()
        merge_df = pd.merge(mapping, heremap_df, left_on='here_map_road', right_on='PATCH')

        merge_df['total_flow'] = (merge_df['total_lanes'] * merge_df['JF'] * merge_df['SP'])/(merge_df['average_vehicle_length'] * 18)

        flow_divide = dict.fromkeys(merge_df['sumo_road'], 0)

        for junction, roads in self.traffic_flow.items():
            for i in roads:
                flow_divide[i['from']] += 1

        output = self.traffic_flow
        for junction, roads in self.traffic_flow.items():
            for i in roads:
                flow_divide[i['from']] += 1

        for junction, roads in output.items():
            for i in roads:
                i['vehicle_flow'] = float(merge_df['total_flow'][merge_df['sumo_road'] == i['from']])/flow_divide[i['from']]

        with open(self.traffic_flow_file, 'w') as outfile:
            json.dump(output, outfile, indent=4)

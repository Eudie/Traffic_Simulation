#!/home/eudie/miniconda3/envs/Traffic_Simulation/bin/python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
In this class I am trying to get vehicle flow from some api

"""
import operator
import requests
import json


class HereMapInfo:
    """
    Here we get the data from heremap, which we will use to build traffic flow for sumo
    """
    def __init__(self, left, bottom, right, top):
        self.left = str(left)
        self.bottom = str(bottom)
        self.right = str(right)
        self.top = str(top)

        # with open('heremap_credentials.json') as f:
        #     api_keys = json.load(f)
        #
        # url = 'https://traffic.cit.api.here.com/traffic/6.1/flow.json?bbox=' + \
        #       self.left + '%2C' + self.bottom + '%3B' + self.right + '%2C' + self.top +\
        #       '&responseattributes=sh,fc&app_code='+api_keys['app_code']+'&app_id='+api_keys['app_id']
        #
        # data = requests.get(url)
        # self.data_json = data.json()

        with open('data_comparision/heremap.json') as f:
            self.data_json = json.load(f)

    def build_traffic_flow(self, junction_info, biggest_junction):
        """
        Here we will match heremap congestion data to sumo traffic flow
        :param junction_info:
        :return:
        """

        # TODO: from here map find the number of vehicles
        # TODO: find the flow for each lane
        # TODO: map flow to each sumo lane with equal distribution
        return self.data_json

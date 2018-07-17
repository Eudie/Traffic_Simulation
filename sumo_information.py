#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
Here we are trying to organize the code for extracting information from SUMO xml files
"""

import pandas as pd
import numpy as np
import networkx as nx
import defusedxml.ElementTree as Xml
from geopy.distance import great_circle


class OsmNetworkInfo:
    """
    Here we are parsing and extracting relevenat information from osm file to use in our model
    """

    def __init__(self, xml_name_location):
        self.xml_name_location = xml_name_location

    def get_raw_traffic_light_nodes(self):
        """
        here we are finding all raw traffic light nodes
        :return: dictionary of all traffic light nodes
        """
        e = Xml.parse(self.xml_name_location).getroot()
        raw_traffic_light_nodes = {}
        for i in e:
            if i.tag == "node":
                junction_name = "None"
                is_signal = False
                for j in i:

                    if j.tag == "tag":
                        if j.attrib["k"] in ["designation", "name"]:
                            junction_name = j.attrib["v"]

                        if j.attrib["v"] == "traffic_signals":
                            is_signal = True
                            raw_traffic_light_nodes[i.attrib["id"]] = {'lat': i.attrib["lat"],
                                                                       'long': i.attrib["lon"]}

                # We are adding junction name below because first we want to confirm that its a signal
                # and have understood all the tags
                if is_signal:
                    raw_traffic_light_nodes[i.attrib["id"]]['junction_name'] = junction_name

        return raw_traffic_light_nodes

    def get_nodes_to_merge(self, max_distance=30):
        """
        here we are finding the nodes of junction which has to be merged is sumo to get proper junction
        :return: list of lists that contain nodes to be merged
        """
        graph = nx.Graph()
        e = Xml.parse(self.xml_name_location).getroot()
        raw_nodes = self.get_raw_traffic_light_nodes()

        # Now we will find all the traffic nodes that are connected
        for i in e:
            if i.tag == "way":
                way_tmp = []
                insert = True
                for j in i:
                    if j.tag == "nd":
                        if j.attrib["ref"] in raw_nodes.keys():
                            way_tmp.append(j.attrib["ref"])
                        else:
                            insert = False  # If any connection in the way is of non-traffic signal node, we reject it
                            break
                if insert:
                    graph.add_path(way_tmp)

        nx.set_node_attributes(graph, raw_nodes)

        # Now we are removing the connections of the node that are very far and genuinely 2 different traffic signals
        for i in graph.edges:
            distance = great_circle((graph.nodes[i[0]]['lat'], graph.nodes[i[0]]['long']),
                                    (graph.nodes[i[1]]['lat'], graph.nodes[i[1]]['long'])).meters
            if distance > max_distance:
                graph.remove_edge(*i)

        # Now after finding the clusters, we are grouping nodes and suggesting name based on the real world name
        output = {}
        i = 0

        for h in nx.connected_component_subgraphs(graph):
            output[i] = {'nodes': list(h.nodes), 'suggested_name': 'None'}

            for node in h.nodes:
                if h.nodes[node]['junction_name'] is not 'None':
                    output[i]['suggested_name'] = h.nodes[node]['junction_name']
            i += 1

        return output


class SumoNetworkInfo:
    """
    In this class we will get all information about sumo network graph
    """

    def __init__(self, xml_name_location):
        self.xml_name_location = xml_name_location

    def get_total_lanes(self, road):
        """
        Here we are finding the total number of lanes of a road
        :param road: road for which lanes to find
        :return: numnber of lanes
        """
        lanes = 0
        parsed_xml = Xml.parse(self.xml_name_location).getroot()
        for i in parsed_xml:
            if i.tag == 'edge':
                if i.attrib['id'] == road:
                    for j in i:
                        if j.tag == 'lane':
                            lanes += 1
        return lanes

    def get_transform(self, list_point):
        """
        To convert sumo point to original lat-long
        """
        x = list_point[0]
        y = list_point[1]

        parsed_xml = Xml.parse(self.xml_name_location).getroot()
        for i in parsed_xml:
            if i.tag == 'location':
                loc = [float(i) for i in i.attrib['origBoundary'].split(',')]
                points = [float(i) for i in i.attrib['convBoundary'].split(',')]

        l1 = loc[0] + ((loc[2] - loc[0]) / (points[2] - points[0])) * x
        l2 = loc[1] + ((loc[3] - loc[1]) / (points[3] - points[1])) * y
        return [l2, l1]

    def get_road_polyline(self, roads):
        """
        Here we are extracting polyline of all list of roads
        :param roads: list of roads
        :return: dict of polyline with key as roads
        """

        parsed_xml = Xml.parse(self.xml_name_location).getroot()

        output = {}
        for i in parsed_xml:
            if i.tag == 'edge' and (i.attrib['id'] in roads):
                all_lanes_polyline = []
                for j in i:
                    if j.tag == 'lane':
                        list_points = []
                        for ll in j.attrib['shape'].split():
                            list_points.append(self.get_transform([float(i) for i in ll.split(',')]))

                        all_lanes_polyline.append(list_points)

                output[i.attrib['id']] = np.around(np.average(all_lanes_polyline, axis=0), 5).tolist()

        return output

    def signal_road_index(self, signal):
        """
        This function is for geting signal incoming index
        """
        parsed_xml = Xml.parse(self.xml_name_location).getroot()

        output = {}
        for i in parsed_xml:
            if i.tag == 'connection' and i.attrib['state'] == 'o':
                if i.attrib['tl'] == signal:
                    output[int(i.attrib['linkIndex'])] = i.attrib['from']

        return output

    def get_junction_location(self, junction):
        """
        Here we are extracting lat long of given junction
        :param junction: junction name
        :return: [lat, long]
        """
        parsed_xml = Xml.parse(self.xml_name_location).getroot()

        for i in parsed_xml:

            if i.tag == 'junction' and i.attrib['id'] == junction:
                return np.around(self.get_transform([float(i.attrib['x']), float(i.attrib['y'])]), 5).tolist()

    def get_junction_routes(self):
        """
        To get the routes which are passing from the junctions, these routes will be used to generate routefile
        :return: dictionary of traffic junction with the list of passing route
        """

        parsed_xml = Xml.parse(self.xml_name_location).getroot()

        output = {}
        for i in parsed_xml:

            if i.tag == 'junction' and i.attrib['type'] == 'traffic_light':
                output[i.attrib['id']] = {'x': i.attrib['x'], 'y': i.attrib['y'],
                                          'incLanes': i.attrib['incLanes'].split(),
                                          'intLanes': i.attrib['intLanes'].split(),
                                          'shape': i.attrib['shape'].split(),
                                          'request': [],
                                          'routes': [],
                                          'phases': []}

                for j in i:
                    if j.tag == "request":
                        output[i.attrib['id']]['request'].append({'index': j.attrib['index'],
                                                                  'response': j.attrib['response'],
                                                                  'foes': j.attrib['foes'],
                                                                  'cont': j.attrib['cont']})

            if i.tag == "connection":
                if 'tl' in i.attrib:
                    output[i.attrib['tl']]['routes'].append({
                                   'from': i.attrib['from'],
                                   'to': i.attrib['to'],
                                   'fromLane': i.attrib['fromLane'],
                                   'toLane': i.attrib['toLane'],
                                   'via': i.attrib['via'],
                                   'linkIndex': i.attrib['linkIndex'],
                                   'dir': i.attrib['dir'],
                                   'state': i.attrib['state']})

        for i in parsed_xml:
            if i.tag == "tlLogic":
                for j in i:
                    if j.tag == "phase":
                        output[i.attrib['id']]['phases'].append({'duration': j.attrib['duration'],
                                                                 'state': j.attrib['state']})

        return output


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

        parsed_xml = Xml.parse(self.xml_name_location)
        tripinfo_list = []
        for full_doc in parsed_xml.iter('tripinfos'):
            for trip in full_doc.iter('tripinfo'):
                tripinfo_list.append(trip.attrib)

        trips_df = pd.DataFrame(tripinfo_list)
        to_float_col = ['arrivalSpeed', 'depart', 'departDelay', 'departSpeed', 'duration', 'speedFactor', 'timeLoss']
        trips_df[to_float_col] = trips_df[to_float_col].astype(np.float)
        return trips_df

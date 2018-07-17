#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
This file is just to test intermediate functions

"""

# import traffic_from_api
#
# minlon, minlat, maxlon, maxlat = 77.7519486464, 12.9833797192, 77.7528560462, 12.9842016832
#
# minlat=str(minlat) # bottom
# minlon=str(minlon) #left
# maxlat=str(maxlat) # top
# maxlon=str(maxlon) # right
#
# data_fold = '../hoodi_test'
#
# here = traffic_from_api.HereMapInfo(data_fold, minlat, minlon, maxlat,  maxlon)
# mapped = here.find_mapping(force=True)
#
# print(mapped)


import dynamic_traffic_signal

traffic_signal = dynamic_traffic_signal.DynamicTrafficSignal('hoodi_test')

traffic_signal.optimize_traffic_lights(timing_range={'min': 45, 'max': 75}, gui=True)


# def __objective(self, **signal):
#     """
#     Internal objective function to optimize
#     :param array: signal timings
#     :return: total mean duration in the simulation
#     """
#     rule = self.get_signal_schema(self.signal_pattern)
#     # rule['time'] = np.cumsum(list(signal.values())).tolist()
#
#     rule_time_list = []
#     value = 0
#     for key in sorted(signal):
#         value += signal[key]
#         rule_time_list.append(value)
#
#     rule['time'] = rule_time_list
#
#     time, teleport = self.run(rule)
#
#     with open(self.filename.log_file, "r") as f:
#         for line in f:
#             if line[:10] == ' Duration:':
#                 log_time = int(line[11:-3])
#
#             if line[:18] == ' Real time factor:':
#                 rtf = float(line[19:-1])
#     # info = sumo_information.SumoTripInfo(self.filename.sumo_tripinfo_file)
#     # df = info.get_df()
#     # self.n += 1
#     # return -1*np.mean(df['timeLoss'])
#
#     return -1 * log_time * rtf
#
#
# def optimize(self, timing_range):
#     """
#     Here we run simulation multiple times and find the most optimized value
#     :param timing_range: tuple of max and min time for lane opening
#     :return: set optimized result
#     """
#
#     if self.signal_pattern is not None:
#         rule = self.get_signal_schema(self.signal_pattern)
#
#     no_of_signals = len(rule['time'])
#
#     bounds = {}
#     for i in range(no_of_signals):
#         bounds['signal' + str(i)] = (timing_range['min'], timing_range['max'])
#
#     bo = BayesianOptimization(self.__objective, bounds)
#     bo.maximize(init_points=(no_of_signals + 1), n_iter=20, acq='ucb', kappa=2)
#
#     # bounds = (slice(timing_range['min'], timing_range['max'], 1),)*no_of_signals
#
#     # x, f_val, grid, j_out = brute(self.__objective, ranges=bounds, full_output=True, finish=None)
#     bo.points_to_csv('check.csv')
#     print(bo.res['all'])
#     print(bo.res['max'])
#     self.final_rule = rule
#
#     time_list = []
#     value = 0
#     for key in sorted(bo.res['max']['max_params']):
#         value += bo.res['max']['max_params'][key]
#         time_list.append(value)
#
#     self.final_rule['time'] = time_list

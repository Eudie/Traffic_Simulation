#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
Here I am trying to make probalistic function to find two line segments are actually one.
This is the extension of normal distribution in zero dimension.

"""


class Distribution:
    """
    Here we will convert zero dimensional normal distribution to 1 dimension to work for line segments
    """

    def __init__(self, sigma):
        self.sigma = sigma

    def probability_line(self, first_seg, second_seg):
        """
        Here we will compare one segment to another
        :param first_seg: coordinates of end points of first segment line [[x1, y1], [x2, y2]]
        :param second_seg: coordinates of end points of second segment line [[x1, y1], [x2, y2]]
        :return: float containing prob
        """

        # TODO Transform lines to first [(0,0), (0, n)] and relatively other


    def probability_polyline(self, first_polyline, second_polyline):
        """
        Here we will compare one segment to another
        :param first_polyline: coordinates of points of first polyline line [[x1, y1], [x2, y2], [x3, y3]]
        :param second_polyline: coordinates of points of second polyline line [[x1, y1], [x2, y2], [x3, y3]]
        :return: float containing prob
        """

        prob = 0
        for i in range(1, len(first_polyline)):
            for j in range(1, len(second_polyline)):
                seg_1 = [first_polyline[i - 1], first_polyline[i]]
                seg_2 = [second_polyline[j - 1], second_polyline[j]]

                prob += self.probability_line(seg_1, seg_2)

        return prob

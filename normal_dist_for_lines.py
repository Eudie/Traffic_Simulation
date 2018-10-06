#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Eudie

"""
This is utility module, extending the normal distribution methods for line segments. Generally we have mean and sigma of
a value and for new experiment value, we check if Z value to check weather it belongs to same distribution. This class
extend this feature of z value testing for 2 line segments.
"""

import numpy as np
from scipy import integrate
from scipy import special


class Distribution:
    """
    Entry point to initialize distribution class and define all the calculation methods.
    """

    def __init__(self, sigma):
        self.sigma = sigma

    def similarity_line(self, first_seg, second_seg):
        """
        This method compares one segment to another
        :param first_seg: coordinates of end points of first segment line [[x1, y1], [x2, y2]]
        :param second_seg: coordinates of end points of second segment line [[x1, y1], [x2, y2]]
        :return: float containing probability
        """

        first_seg = np.array(first_seg)
        second_seg = np.array(second_seg)
        points = np.concatenate((first_seg, second_seg))

        move = points[0]

        with np.errstate(divide='ignore', invalid='ignore'):
            angle = np.arctan((first_seg[1, 1] - first_seg[0, 1]) / (first_seg[1, 0] - first_seg[0, 0]))

        c, s = np.cos(angle), np.sin(angle)

        rotation = np.array([[c, s],
                             [-s, c]])

        points = np.around(np.squeeze(np.apply_along_axis(lambda row: np.dot(rotation, row - move), 1, points)), 7)

        q = points[1, 0]
        r = points[2, 0]
        s = points[3, 0]

        if (r < min(0, q) and s < min(0, q)) or (r > max(0, q) and s > max(0, q)):
            return 0.0

        x_coords, y_coords = zip(*points[2:])
        m, c = np.polyfit(x_coords, y_coords, 1)
        sigma = self.sigma

        # ranges = [[0, points[1, 0]], [points[2, 0], points[3, 0]]]

        # def function_to_integrate(x, u):
        #     """
        #     This is the function we are getting to integrate normal distribution probability of each point of line
        #     with each point of line 2 (u)
        #     """
        #     return np.exp(-0.5 * (np.square(x - u) + np.square(m * u + c)) / np.square(sigma)) * np.sqrt(
        #         1 + np.square(m)) / (sigma * np.sqrt((2 * np.pi)))
        #
        # output = integrate.nquad(function_to_integrate, ranges)

        def function_to_integrate(u):
            """
            This is the function we are getting to integrate normal distribution probability of each point of line with
            each point of line 2. (signal integration, much more efficient)
            """
            return (-(np.sqrt(np.pi) * sigma * np.exp(-(m * u + c) ** 2 / (2 * sigma ** 2)) * (
                        special.erf((u - q) / (np.sqrt(2) * sigma)) - special.erf(
                    u / (np.sqrt(2) * sigma)))) / np.sqrt(2)) * np.sqrt(1 + np.square(m)) / (
                               sigma * np.sqrt((2 * np.pi)))

        output = integrate.quad(function_to_integrate, r, s)

        return np.abs(output[0])

    def similarity_polyline(self, first_polyline, second_polyline):
        """
        This method compares one polyline to another polyline
        :param first_polyline: coordinates of points of first polyline line [[x1, y1], [x2, y2], [x3, y3] ....]
        :param second_polyline: coordinates of points of second polyline line [[x1, y1], [x2, y2], [x3, y3] ....]
        :return: float containing probability
        """

        similarity = 0.0
        for i in range(1, len(first_polyline)):
            for j in range(1, len(second_polyline)):
                seg_1 = [first_polyline[i - 1], first_polyline[i]]
                seg_2 = [second_polyline[j - 1], second_polyline[j]]

                similarity += self.similarity_line(seg_1, seg_2)

        return similarity

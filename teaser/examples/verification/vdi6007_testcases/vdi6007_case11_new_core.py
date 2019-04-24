#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
import os
import numpy as np

from teaser.project import Project
from teaser.logic.buildingobjects.building import Building
from teaser.logic.buildingobjects.thermalzone import ThermalZone
from teaser.logic.buildingobjects.calculation.two_element import TwoElement
from teaser.logic.simulation.vdi_core import VDICore

# import customized weather class
from teaser.data.weatherdata import WeatherData

import teaser.examples.verification.vdi6007_testcases.vdi6007_case01 as vdic


def run_case11(plot_res=False):
    """
    Run test case 11

    Test Case 11 of the VDI 6007 Part 1:
    Calculation of heat load excited with a given radiative heat source and a setpoint
    profile for room version S. It is based on Test Case 7, but with a cooling ceiling
    for cooling purposes instead of a pure convective ideal cooler.

    Boundary conditions :
      - constant outdoor air temperature 22°C
      - no solar or short-wave radiation on the exterior wall
      - no solar or short-wave radiation through the windows
      - no long-wave radiation exchange between exterior wall, windows and ambient
        environment

    This test validates implementation of cooling ceiling or floor heating.

    Parameters
    ----------
    plot_res : bool, optional
        Defines, if results should be plotted (default: False)

    Returns
    -------
    res_tuple : tuple (of floats)
        Results tuple with maximal deviations for temperatures and power
        values
        (max_dev_1_temp, max_dev_10_temp, max_dev_60_temp, max_dev_1,
            max_dev_10, max_dev_60)
    """

    # Definition of time horizon
    times_per_hour = 60
    timesteps = 24 * 60 * times_per_hour  # 60 days
    timesteps_day = int(24 * times_per_hour)

    # Zero inputs
    ventRate = np.zeros(timesteps)
    solarRad_in = np.zeros((timesteps, 1))
    Q_ig = np.zeros(timesteps)

    # Constant inputs
    alphaRad = np.zeros(timesteps) + 5
    equalAirTemp = np.zeros(timesteps) + 295.15  # all temperatures in K
    weatherTemperature = np.zeros(timesteps) + 295.15  # in K

    # Variable inputs
    source_igRad = np.zeros(timesteps_day)
    for q in range(int(6 * timesteps_day / 24), int(18 * timesteps_day / 24)):
        source_igRad[q] = 1000
    source_igRad = np.tile(source_igRad, 60)


    # new core

    weather = WeatherData()
    weather.air_temp = np.zeros(timesteps) + 295.15

    prj = Project()
    prj.weather_data = weather

    bldg = Building(prj)

    tz = ThermalZone(bldg)

    model_data = TwoElement(tz, merge_windows=False, t_bt=5)

    #  Store building parameters for testcase 1
    model_data.r1_iw = 0.000595693407511
    model_data.c1_iw = 14836354.6282
    model_data.area_iw = 75.5
    model_data.r_rest_ow = 0.03895919557
    model_data.r1_ow = 0.00436791293674
    model_data.c1_ow = 1600848.94
    model_data.area_ow = 10.5
    model_data.outer_wall_areas = [10.5]
    model_data.window_areas = np.zeros(1)
    model_data.transparent_areas = np.zeros(1)
    tz.volume = 52.5
    tz.density_air = 1.19
    tz.heat_capac_air = 0
    model_data.ratio_conv_rad_inner_win = 0.09
    model_data.weighted_g_value = 1
    model_data.alpha_comb_inner_iw = 2.24
    model_data.alpha_comb_inner_ow = 2.7
    model_data.alpha_conv_outer_ow = 20
    model_data.alpha_rad_outer_ow = 5
    model_data.alpha_comb_outer_ow = 25
    model_data.alpha_rad_inner_mean = 5
    # model_data.tilt_facade = []
    # model_data.orientation_facade = [180.0, -1, 0.0, -2, 90.0, 270.0]
    # model_data.alpha_wall = 25 * 10.5

    tz.model_attr = model_data

    calc = VDICore(tz)
    calc.equal_air_temp = np.zeros(timesteps) + 295.15
    calc.solar_rad_in = np.zeros((timesteps, 1))

    t_set = np.zeros(timesteps_day) + 273.15 + 22
    for q in range(int(6 * timesteps_day / 24), int(18 * timesteps_day / 24)):
        t_set[q] = 273.15 + 27
    t_set = np.tile(t_set, 60)

    calc.t_set_heating = t_set
    calc.t_set_cooling = t_set

    calc.heater_limit = np.zeros((timesteps, 3))
    calc.heater_limit[:, 0] = 500
    calc.heater_order = np.array([1, 2, 3])
    calc.cooler_limit = np.zeros((timesteps, 3))
    calc.cooler_limit[:, 0] = - 500
    calc.cooler_order = [2, 1, 3]

    source_igRad = np.zeros(timesteps_day)
    for q in range(int(6 * timesteps_day / 24), int(18 * timesteps_day / 24)):
        source_igRad[q] = 1000
    source_igRad = np.tile(source_igRad, 60)

    calc.internal_gains_rad = source_igRad

    t_air, q_air_hc = calc.simulate()

    T_air_c = t_air - 273.15
    T_air_mean = np.array(
        [np.mean(T_air_c[i * times_per_hour:(i + 1) * times_per_hour]) for i in
         range(24 * 60)])

    Q_hc_mean = np.array(
        [np.mean(q_air_hc[i * times_per_hour:(i + 1) * times_per_hour]) for i in
         range(24 * 60)])



    # # Load constant house parameters
    # houseData = {"R1i": 0.000595693407511,
    #              "C1i": 14836354.6282,
    #              "Ai": 75.5,
    #              "RRest": 0.03895919557,
    #              "R1o": 0.00436791293674,
    #              "C1o": 1600848.94,
    #              "Ao": [10.5],
    #              "Aw": np.zeros(1),
    #              "At": [0],
    #              "Vair": 0,
    #              "rhoair": 1.19,
    #              "cair": 1007,
    #              "splitfac": 0.09,
    #              "g": 1,
    #              "alphaiwi": 3,
    #              "alphaowi": 2.7,
    #              "alphaWall": 25 * 10.5,  # 25 * sum(Ao)
    #              "withInnerwalls": True}

    # krad = 1

    # # Define set points
    # t_set = np.zeros(timesteps_day) + 273.15 + 22
    # for q in range(int(6 * timesteps_day / 24), int(18 * timesteps_day / 24)):
    #     t_set[q] = 273.15 + 27
    # t_set = np.tile(t_set, 60)
    # t_set_heating = t_set
    # t_set_cooling = t_set

    # heater_limit = np.zeros((timesteps, 3))
    # cooler_limit = np.zeros((timesteps, 3))
    # heater_limit[:, 0] = 500
    # cooler_limit[:, 1] = -500

    # # Calculate indoor air temperature
    # T_air, Q_hc, Q_iw, Q_ow = \
    #     low_order_VDI.reducedOrderModelVDI(houseData,
    #                                        weatherTemperature,
    #                                        solarRad_in,
    #                                        equalAirTemp,
    #                                        alphaRad,
    #                                        ventRate,
    #                                        Q_ig,
    #                                        source_igRad,
    #                                        krad,
    #                                        t_set_heating,
    #                                        t_set_cooling,
    #                                        heater_limit,
    #                                        cooler_limit,
    #                                        heater_order=np.array(
    #                                            [1, 2,
    #                                             3]),
    #                                        cooler_order=np.array(
    #                                            [2, 1,
    #                                             3]),
    #                                        dt=int(
    #                                            3600 / times_per_hour))

    # Compute averaged results
    # Q_hc_mean = np.array(
    #     [np.mean(Q_hc[i * times_per_hour:(i + 1) * times_per_hour]) for i in
    #      range(24 * 60)])
    # Q_iw_mean = np.array(
    #     [np.mean(Q_iw[i * times_per_hour:(i + 1) * times_per_hour]) for i in
    #      range(24 * 60)])
    # Q_ow_mean = np.array(
    #     [np.mean(Q_ow[i * times_per_hour:(i + 1) * times_per_hour]) for i in
    #      range(24 * 60)])

    # Q_hc_1 = Q_hc_mean[0:24] + Q_iw_mean[0:24] + Q_ow_mean[0:24]
    # Q_hc_10 = Q_hc_mean[216:240] + Q_iw_mean[216:240] + Q_ow_mean[216:240]
    # Q_hc_60 = Q_hc_mean[1416:1440] + Q_iw_mean[1416:1440] + Q_ow_mean[
    #                                                         1416:1440]
    Q_hc_1 = Q_hc_mean[0:24]
    Q_hc_10 = Q_hc_mean[216:240]
    Q_hc_60 = Q_hc_mean[1416:1440]

    # T_air_c = T_air - 273.15
    # T_air_mean = np.array(
    #     [np.mean(T_air_c[i * times_per_hour:(i + 1) * times_per_hour]) for i in
    #      range(24 * 60)])

    T_air_1 = T_air_mean[0:24]
    T_air_10 = T_air_mean[216:240]
    T_air_60 = T_air_mean[1416:1440]

    this_path = os.path.dirname(os.path.abspath(__file__))
    ref_file = 'case11_res.csv'
    ref_path = os.path.join(this_path, 'inputs', ref_file)

    # Load reference results
    (load_res_1, load_res_10, load_res_60) = vdic.load_res(ref_path)
    Q_hc_ref_1 = load_res_1[:, 1]
    Q_hc_ref_10 = load_res_10[:, 1]
    Q_hc_ref_60 = load_res_60[:, 1]

    T_air_ref_1 = load_res_1[:, 0]
    T_air_ref_10 = load_res_10[:, 0]
    T_air_ref_60 = load_res_60[:, 0]

    # Plot comparisons
    def plot_result(res, ref, title="Results day 1"):

        import matplotlib.pyplot as plt

        plt.figure()
        ax_top = plt.subplot(211)
        plt.plot(ref, label="Reference", color="black", linestyle="--")
        plt.plot(res, label="Simulation", color="blue", linestyle="-")
        plt.legend()
        plt.ylabel("Heat load in W")

        plt.title(title)

        plt.subplot(212, sharex=ax_top)
        plt.plot(res - ref, label="Ref. - Sim.")
        plt.legend()
        plt.ylabel("Heat load difference in W")
        plt.xticks([4 * i for i in range(7)])
        plt.xlim([1, 24])
        plt.xlabel("Time in h")

        plt.show()

    if plot_res:
        plot_result(T_air_1, T_air_ref_1, "Results temperatures day 1")
        plot_result(T_air_10, T_air_ref_10, "Results temperatures day 10")
        plot_result(T_air_60, T_air_ref_60, "Results temperatures day 60")

        plot_result(Q_hc_1, Q_hc_ref_1, "Results heating/cooling day 1")
        plot_result(Q_hc_10, Q_hc_ref_10, "Results heating/cooling day 10")
        plot_result(Q_hc_60, Q_hc_ref_60, "Results heating/cooling day 60")

    max_dev_1_temp = np.max(np.abs(T_air_1 - T_air_ref_1))
    max_dev_10_temp = np.max(np.abs(T_air_10 - T_air_ref_10))
    max_dev_60_temp = np.max(np.abs(T_air_60 - T_air_ref_60))

    print("Deviations temperature in K:")
    print("Max. deviation day 1: " + str(max_dev_1_temp))
    print("Max. deviation day 10: " + str(max_dev_10_temp))
    print("Max. deviation day 60: " + str(max_dev_60_temp))

    max_dev_1 = np.max(np.abs(Q_hc_1 - Q_hc_ref_1))
    max_dev_10 = np.max(np.abs(Q_hc_10 - Q_hc_ref_10))
    max_dev_60 = np.max(np.abs(Q_hc_60 - Q_hc_ref_60))

    print("Deviations heating/cooling in W:")
    print("Max. deviation day 1: " + str(max_dev_1))
    print("Max. deviation day 10: " + str(max_dev_10))
    print("Max. deviation day 60: " + str(max_dev_60))

    return (max_dev_1_temp, max_dev_10_temp, max_dev_60_temp, max_dev_1,
            max_dev_10, max_dev_60)

if __name__ == '__main__':
    run_case11(plot_res=True)
